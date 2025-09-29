"""GitHub API client for GitCo."""

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Optional

import requests
from github import Github

from ..utils.common import (
    get_logger,
    log_api_call,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)
from ..utils.exception import (
    APIError,
    ConnectionTimeoutError,
    GitHubAuthenticationError,
    NetworkTimeoutError,
    ReadTimeoutError,
    RequestTimeoutError,
)
from ..utils.rate_limiter import RateLimitedAPIClient, get_rate_limiter
from ..utils.retry import TIMEOUT_AWARE_RETRY_CONFIG, create_retry_session, with_retry
from .git_ops import detect_github_auth, test_github_auth


@dataclass
class GitHubIssue:
    """GitHub issue data structure."""

    number: int
    title: str
    state: str
    labels: list[str]
    assignees: list[str]
    created_at: str
    updated_at: str
    html_url: str
    body: Optional[str] = None
    user: Optional[str] = None
    milestone: Optional[str] = None
    comments_count: int = 0
    reactions_count: int = 0


@dataclass
class GitHubRepository:
    """GitHub repository data structure."""

    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    updated_at: str
    html_url: str
    clone_url: str
    default_branch: str
    topics: Optional[list[str]] = None
    archived: bool = False
    disabled: bool = False


@dataclass
class SSHGitHubResponse:
    """SSH GitHub API response."""

    status_code: int
    headers: dict[str, str]
    data: Any
    success: bool


class SSHGitHubClient:
    """SSH-based GitHub API client."""

    def __init__(self, auth_info):
        """Initialize SSH GitHub client.

        Args:
            auth_info: Git authentication information
        """
        self.auth_info = auth_info
        self.logger = get_logger()
        self.base_url = "https://api.github.com"

    def _make_ssh_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> SSHGitHubResponse:
        """Make SSH-based request to GitHub API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            SSHGitHubResponse with response data

        Raises:
            APIError: If request fails
        """
        try:
            # Build URL with query parameters
            url = f"{self.base_url}{endpoint}"
            if params:
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                url = f"{url}?{query_string}"

            # Prepare curl command
            curl_cmd = [
                "curl",
                "-s",  # Silent mode
                "-w",  # Write-out format for status code and headers
                "%{http_code}\\n%{header_json}\\n",
                "-X",
                method,
                url,
            ]

            # Add headers
            curl_cmd.extend(["-H", "Accept: application/vnd.github.v3+json"])
            curl_cmd.extend(["-H", "User-Agent: GitCo/1.0"])

            # Add authentication if available
            if self.auth_info.token:
                curl_cmd.extend(["-H", f"Authorization: token {self.auth_info.token}"])
            elif self.auth_info.username and self.auth_info.password:
                import base64

                credentials = base64.b64encode(
                    f"{self.auth_info.username}:{self.auth_info.password}".encode()
                ).decode()
                curl_cmd.extend(["-H", f"Authorization: Basic {credentials}"])

            # Add request body if present
            if data and method in ["POST", "PUT", "PATCH"]:
                json_data = json.dumps(data)
                curl_cmd.extend(["-H", "Content-Type: application/json"])
                curl_cmd.extend(["-d", json_data])

            # Execute curl command
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise APIError(f"SSH request failed: {result.stderr}")

            # Parse response
            lines = result.stdout.strip().split("\n")
            if len(lines) < 2:
                raise APIError("Invalid response format from GitHub API")

            status_code = int(lines[0])
            headers_json = lines[1]
            response_data = "\n".join(lines[2:]) if len(lines) > 2 else "{}"

            # Parse headers
            try:
                headers = json.loads(headers_json)
            except json.JSONDecodeError:
                headers = {}

            # Parse response data
            try:
                if response_data.strip():
                    data = json.loads(response_data)
                else:
                    data = {}
            except json.JSONDecodeError:
                data = response_data

            success = 200 <= status_code < 300

            return SSHGitHubResponse(
                status_code=status_code,
                headers=headers,
                data=data,
                success=success,
            )

        except subprocess.TimeoutExpired as e:
            raise APIError(f"SSH request timed out: {e}") from e
        except Exception as e:
            raise APIError(f"SSH request failed: {e}") from e

    def get_user(self) -> dict[str, Any]:
        """Get current user information.

        Returns:
            User information dictionary

        Raises:
            APIError: If request fails
            GitHubAuthenticationError: If authentication fails
        """
        log_api_call("github", "/user", "GET")

        response = self._make_ssh_request("GET", "/user")

        if response.status_code == 401:
            raise GitHubAuthenticationError("GitHub authentication failed")
        elif not response.success:
            raise APIError(f"Failed to get user info: {response.status_code}")

        return response.data

    def get_repository(self, repo_name: str) -> dict[str, Any]:
        """Get repository information.

        Args:
            repo_name: Repository name (owner/repo)

        Returns:
            Repository information dictionary

        Raises:
            APIError: If request fails
        """
        log_api_call("github", f"/repos/{repo_name}", "GET")

        response = self._make_ssh_request("GET", f"/repos/{repo_name}")

        if response.status_code == 404:
            raise APIError(f"Repository not found: {repo_name}")
        elif not response.success:
            raise APIError(f"Failed to get repository: {response.status_code}")

        return response.data

    def get_issues(
        self,
        repo_name: str,
        state: str = "open",
        labels: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        milestone: Optional[str] = None,
        limit: Optional[int] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        """Get issues for a repository.

        Args:
            repo_name: Repository name (owner/repo)
            state: Issue state (open, closed, all)
            labels: List of labels to include
            assignee: Assignee filter
            milestone: Milestone filter
            limit: Maximum number of issues to return
            page: Page number
            per_page: Issues per page

        Returns:
            List of issue dictionaries

        Raises:
            APIError: If request fails
        """
        log_api_call("github", f"/repos/{repo_name}/issues", "GET")

        params = {
            "state": state,
            "page": page,
            "per_page": min(per_page, 100),  # GitHub API limit
        }

        if labels:
            params["labels"] = ",".join(labels)
        if assignee:
            params["assignee"] = assignee
        if milestone:
            params["milestone"] = milestone

        response = self._make_ssh_request(
            "GET", f"/repos/{repo_name}/issues", params=params
        )

        if not response.success:
            raise APIError(f"Failed to get issues: {response.status_code}")

        issues = response.data if isinstance(response.data, list) else []

        # Apply limit if specified
        if limit and len(issues) > limit:
            issues = issues[:limit]

        return issues

    def search_issues(
        self,
        query: str,
        sort: str = "updated",
        order: str = "desc",
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """Search for issues.

        Args:
            query: Search query
            sort: Sort field
            order: Sort order (asc, desc)
            page: Page number
            per_page: Results per page

        Returns:
            Search results dictionary

        Raises:
            APIError: If request fails
        """
        log_api_call("github", "/search/issues", "GET")

        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100),  # GitHub API limit
        }

        response = self._make_ssh_request("GET", "/search/issues", params=params)

        if not response.success:
            raise APIError(f"Failed to search issues: {response.status_code}")

        return response.data

    def get_rate_limit(self) -> dict[str, Any]:
        """Get rate limit information.

        Returns:
            Rate limit information dictionary

        Raises:
            APIError: If request fails
        """
        log_api_call("github", "/rate_limit", "GET")

        response = self._make_ssh_request("GET", "/rate_limit")

        if not response.success:
            raise APIError(f"Failed to get rate limit: {response.status_code}")

        return response.data

    def test_connection(self) -> bool:
        """Test connection to GitHub API.

        Returns:
            True if connection is successful
        """
        try:
            self.get_user()
            return True
        except Exception:
            return False

    def get_issues_for_repositories(
        self,
        repositories: list[str],
        state: str = "open",
        labels: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        milestone: Optional[str] = None,
        limit_per_repo: Optional[int] = None,
        total_limit: Optional[int] = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Get issues for multiple repositories.

        Args:
            repositories: List of repository names
            state: Issue state (open, closed, all)
            labels: List of labels to include
            assignee: Assignee filter
            milestone: Milestone filter
            limit_per_repo: Maximum issues per repository
            total_limit: Maximum total issues across all repositories

        Returns:
            Dictionary mapping repository names to lists of issues

        Raises:
            APIError: If request fails
        """
        all_issues: dict[str, list[dict[str, Any]]] = {}
        total_issues = 0

        for repo_name in repositories:
            try:
                repo_issues = self.get_issues(
                    repo_name=repo_name,
                    state=state,
                    labels=labels,
                    assignee=assignee,
                    milestone=milestone,
                    limit=limit_per_repo,
                )

                all_issues[repo_name] = repo_issues
                total_issues += len(repo_issues)

                # Check total limit
                if total_limit and total_issues >= total_limit:
                    break

            except Exception as e:
                self.logger.warning(f"Failed to fetch issues for {repo_name}: {e}")
                all_issues[repo_name] = []

        return all_issues


def create_ssh_github_client(auth_info) -> SSHGitHubClient:
    """Create an SSH-based GitHub client.

    Args:
        auth_info: Git authentication information

    Returns:
        SSH-based GitHub client instance
    """
    return SSHGitHubClient(auth_info)


class GitHubClient(RateLimitedAPIClient):
    """GitHub API client with Git-based authentication and rate limiting."""

    def __init__(
        self,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        max_retries: int = 3,
        connect_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        repo_path: Optional[str] = None,
        use_git_auth: bool = True,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token (fallback if Git auth fails)
            username: GitHub username (fallback if Git auth fails)
            password: GitHub password (fallback if Git auth fails)
            base_url: GitHub API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            connect_timeout: Connection timeout in seconds (overrides timeout if set)
            read_timeout: Read timeout in seconds (overrides timeout if set)
            repo_path: Optional repository path for local Git authentication
            use_git_auth: Whether to use Git-based authentication (default: True)
        """
        # Initialize rate limiter
        rate_limiter = get_rate_limiter("github")
        super().__init__(rate_limiter)

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.connect_timeout = connect_timeout or timeout
        self.read_timeout = read_timeout or timeout
        self.token = token
        self.repo_path = repo_path
        self.use_git_auth = use_git_auth

        # Create session with retry capabilities
        self.session = create_retry_session(
            max_attempts=max_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504, 429],
        )

        # Set up authentication
        self._setup_authentication(token, username, password)

    def _setup_authentication(
        self,
        token: Optional[str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """Set up authentication for GitHub API.

        Args:
            token: GitHub personal access token (fallback)
            username: GitHub username (fallback)
            password: GitHub password (fallback)

        Raises:
            GitHubAuthenticationError: If authentication setup fails
        """
        try:
            # Try Git-based authentication first
            if self.use_git_auth:
                self._setup_git_authentication()
                if self._test_authentication():
                    return

            # Fall back to traditional authentication
            self._init_github_client(token, username, password)
            self._test_authentication()

        except Exception as e:
            raise GitHubAuthenticationError(
                f"Failed to set up GitHub authentication: {e}"
            ) from e

    def _setup_git_authentication(self) -> None:
        """Set up Git-based authentication.

        Raises:
            GitHubAuthenticationError: If Git authentication setup fails
        """
        try:
            # Detect Git authentication
            self.git_auth_info = detect_github_auth(self.repo_path)

            if self.git_auth_info.method == "none":
                raise GitHubAuthenticationError("No Git authentication found")

            # Test the authentication
            if not test_github_auth(self.git_auth_info):
                raise GitHubAuthenticationError("Git authentication test failed")

            # Create appropriate client based on authentication method
            if self.git_auth_info.method == "ssh":
                self.ssh_client = create_ssh_github_client(self.git_auth_info)
                self.auth_method = "ssh"
            else:
                # Use traditional GitHub client with Git credentials
                self._init_github_client(
                    self.git_auth_info.token,
                    self.git_auth_info.username,
                    self.git_auth_info.password,
                )
                self.auth_method = self.git_auth_info.method

        except Exception as e:
            raise GitHubAuthenticationError(
                f"Failed to set up Git authentication: {e}"
            ) from e

    def _init_github_client(
        self,
        token: Optional[str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """Initialize GitHub client with authentication.

        Args:
            token: GitHub personal access token
            username: GitHub username
            password: GitHub password
        """
        if token:
            # Use token authentication (preferred)
            self.github = Github(token, base_url=self.base_url)
            self.auth_method = "token"
        elif username and password:
            # Use basic authentication
            self.github = Github(username, password, base_url=self.base_url)
            self.auth_method = "basic"
        else:
            # Try to get token from environment
            token = os.getenv("GITHUB_TOKEN")
            if token:
                self.github = Github(token, base_url=self.base_url)
                self.auth_method = "token"
            else:
                # Anonymous access (limited API access)
                self.github = Github(base_url=self.base_url)
                self.auth_method = "anonymous"

    def _test_authentication(self) -> bool:
        """Test GitHub authentication.

        Returns:
            True if authentication is successful

        Raises:
            GitHubAuthenticationError: If authentication fails
        """
        try:
            if hasattr(self, "auth_method") and self.auth_method == "ssh":
                # Test SSH client
                return self.ssh_client.test_connection()
            elif hasattr(self, "github"):
                if self.auth_method == "anonymous":
                    # For anonymous access, just test the connection
                    self.github.get_rate_limit()
                    self.logger.info("GitHub anonymous access successful")
                    return True
                else:
                    # Test authentication by getting current user
                    user = self.github.get_user()
                    self.logger.info(
                        f"GitHub authentication successful for user: {user.login}"
                    )
                    return True
            else:
                return False
        except Exception as e:
            self.logger.debug(f"GitHub authentication test failed: {e}")
            return False

    def _rate_limit_request(self) -> None:
        """Check rate limits before making requests."""
        self.rate_limiter.wait_if_needed()

    @with_retry(config=TIMEOUT_AWARE_RETRY_CONFIG)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        """Make HTTP request to GitHub API with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Additional headers

        Returns:
            API response data

        Raises:
            NetworkTimeoutError: When network operation times out
            GitHubRateLimitExceeded: When rate limit is exceeded
            APIError: When API request fails
        """
        url = f"{self.base_url}{endpoint}"

        self._rate_limit_request()

        log_api_call("github", endpoint, "started")

        try:
            # Use tuple for timeout (connect_timeout, read_timeout)
            timeout_tuple = (self.connect_timeout, self.read_timeout)

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=timeout_tuple,
            )

        except requests.exceptions.ConnectTimeout as e:
            raise ConnectionTimeoutError(
                f"Connection to GitHub API timed out: {endpoint}",
                self.connect_timeout,
                f"GitHub API {method} {endpoint}",
            ) from e
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutError(
                f"Read from GitHub API timed out: {endpoint}",
                self.read_timeout,
                f"GitHub API {method} {endpoint}",
            ) from e
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(
                f"Request to GitHub API timed out: {endpoint}",
                self.timeout,
                f"GitHub API {method} {endpoint}",
            ) from e
        except requests.exceptions.RequestException as e:
            # Convert to our custom exception
            raise NetworkTimeoutError(
                f"Network error during GitHub API request: {endpoint}",
                self.timeout,
                f"GitHub API {method} {endpoint}",
            ) from e

        # Update rate limiter with response headers
        self.rate_limiter.update_from_response_headers(dict(response.headers))

        # Check rate limiting
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining and int(remaining) == 0:
            self.rate_limiter.handle_rate_limit_exceeded(dict(response.headers))
            # Let the retry decorator handle the retry
            raise APIError("Rate limit exceeded")

        # Handle response
        if response.status_code == 200:
            log_api_call("github", endpoint, "success")
            return response.json()
        elif response.status_code == 404:
            log_api_call("github", endpoint, "not_found")
            raise APIError(f"GitHub API endpoint not found: {endpoint}")
        elif response.status_code == 401:
            log_api_call("github", endpoint, "unauthorized")
            raise GitHubAuthenticationError("GitHub API authentication failed")
        elif response.status_code == 403:
            log_api_call("github", endpoint, "forbidden")
            raise APIError("GitHub API access denied")
        elif response.status_code >= 500:
            log_api_call("github", endpoint, "server_error")
            raise APIError(f"GitHub API server error: {response.status_code}")
        else:
            log_api_call("github", endpoint, "error")
            raise APIError(
                f"GitHub API error: {response.status_code} - {response.text}"
            )

    def get_repository(self, repo_name: str) -> Optional[GitHubRepository]:
        """Get repository information.

        Args:
            repo_name: Repository name (owner/repo)

        Returns:
            Repository information or None if not found
        """
        if not repo_name:
            return None

        log_operation_start("github repository fetch", repo_name=repo_name)

        try:
            # Use SSH client if available, otherwise use traditional client
            if hasattr(self, "auth_method") and self.auth_method == "ssh":
                repo_data = self.ssh_client.get_repository(repo_name)

                github_repo = GitHubRepository(
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    description=repo_data.get("description"),
                    language=repo_data.get("language"),
                    stargazers_count=repo_data.get("stargazers_count", 0),
                    forks_count=repo_data.get("forks_count", 0),
                    open_issues_count=repo_data.get("open_issues_count", 0),
                    updated_at=repo_data.get("updated_at", ""),
                    html_url=repo_data.get("html_url", ""),
                    clone_url=repo_data.get("clone_url", ""),
                    default_branch=repo_data.get("default_branch", "main"),
                    topics=repo_data.get("topics", []),
                    archived=repo_data.get("archived", False),
                    disabled=repo_data.get("disabled", False),
                )
            else:
                repo = self.github.get_repo(repo_name)

                github_repo = GitHubRepository(
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    language=repo.language,
                    stargazers_count=repo.stargazers_count,
                    forks_count=repo.forks_count,
                    open_issues_count=repo.open_issues_count,
                    updated_at=repo.updated_at.isoformat(),
                    html_url=repo.html_url,
                    clone_url=repo.clone_url,
                    default_branch=repo.default_branch,
                    topics=repo.get_topics(),
                    archived=repo.archived,
                    disabled=repo.disabled,
                )

            log_operation_success("github repository fetch", repo_name=repo_name)
            return github_repo

        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                log_operation_failure("github repository fetch", e, repo_name=repo_name)
                return None
            else:
                log_operation_failure("github repository fetch", e, repo_name=repo_name)
                raise APIError(f"Failed to fetch repository {repo_name}: {e}") from e

    def get_issues(
        self,
        repo_name: str,
        state: str = "open",
        labels: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        milestone: Optional[str] = None,
        limit: Optional[int] = None,
        exclude_labels: Optional[list[str]] = None,
        created_after: Optional[str] = None,
        updated_after: Optional[str] = None,
    ) -> list[GitHubIssue]:
        """Get issues for a repository.

        Args:
            repo_name: Repository name (owner/repo)
            state: Issue state (open, closed, all)
            labels: List of labels to include
            assignee: Assignee filter
            milestone: Milestone filter
            limit: Maximum number of issues to return
            exclude_labels: List of labels to exclude
            created_after: Filter issues created after this date
            updated_after: Filter issues updated after this date

        Returns:
            List of GitHub issues
        """
        if not repo_name:
            return []

        log_operation_start("github issues fetch", repo_name=repo_name)

        try:
            # Use SSH client if available, otherwise use traditional client
            if hasattr(self, "auth_method") and self.auth_method == "ssh":
                issues_data = self.ssh_client.get_issues(
                    repo_name=repo_name,
                    state=state,
                    labels=labels,
                    assignee=assignee,
                    milestone=milestone,
                    limit=limit,
                )

                # Convert to our data structure
                issues = []
                for issue_data in issues_data:
                    github_issue = GitHubIssue(
                        number=issue_data.get("number", 0),
                        title=issue_data.get("title", ""),
                        state=issue_data.get("state", "open"),
                        labels=[
                            label.get("name", "")
                            for label in issue_data.get("labels", [])
                        ],
                        assignees=[
                            assignee.get("login", "")
                            for assignee in issue_data.get("assignees", [])
                        ],
                        created_at=issue_data.get("created_at", ""),
                        updated_at=issue_data.get("updated_at", ""),
                        html_url=issue_data.get("html_url", ""),
                        body=issue_data.get("body"),
                        user=issue_data.get("user", {}).get("login")
                        if issue_data.get("user")
                        else None,
                        milestone=issue_data.get("milestone", {}).get("title")
                        if issue_data.get("milestone")
                        else None,
                        comments_count=issue_data.get("comments", 0),
                        reactions_count=issue_data.get("reactions", {}).get(
                            "total_count", 0
                        ),
                    )
                    issues.append(github_issue)
            else:
                # Get repository for validation
                self.github.get_repo(repo_name)
                issues = []

                # Build query parameters
                query_parts = [f"repo:{repo_name}", f"state:{state}"]

                if labels:
                    for label in labels:
                        query_parts.append(f'label:"{label}"')

                if assignee:
                    query_parts.append(f"assignee:{assignee}")

                if milestone:
                    query_parts.append(f'milestone:"{milestone}"')

                if created_after:
                    query_parts.append(f"created:>={created_after}")

                if updated_after:
                    query_parts.append(f"updated:>={updated_after}")

                query = " ".join(query_parts)

                # Search issues
                search_results: Any = self.github.search_issues(
                    query, sort="updated", order="desc"
                )

                # Apply limit
                if limit:
                    search_results = list(search_results)[:limit]

                # Filter out excluded labels
                if exclude_labels:
                    search_results = [
                        issue
                        for issue in search_results
                        if not any(
                            label.name in exclude_labels for label in issue.labels
                        )
                    ]

                # Convert to our data structure
                for issue in search_results:
                    github_issue = GitHubIssue(
                        number=issue.number,
                        title=issue.title,
                        state=issue.state,
                        labels=[label.name for label in issue.labels],
                        assignees=[assignee.login for assignee in issue.assignees],
                        created_at=issue.created_at.isoformat(),
                        updated_at=issue.updated_at.isoformat(),
                        html_url=issue.html_url,
                        body=issue.body,
                        user=issue.user.login if issue.user else None,
                        milestone=issue.milestone.title if issue.milestone else None,
                        comments_count=issue.comments,
                        reactions_count=(
                            len(issue.get_reactions())
                            if hasattr(issue, "get_reactions")
                            else 0
                        ),
                    )
                    issues.append(github_issue)

            log_operation_success("github issues fetch", repo_name=repo_name)
            return issues

        except Exception as e:
            log_operation_failure("github issues fetch", e, repo_name=repo_name)
            raise APIError(f"Failed to fetch issues for {repo_name}: {e}") from e

    def search_issues(
        self,
        query: str,
        state: str = "open",
        labels: Optional[list[str]] = None,
        language: Optional[str] = None,
        limit: Optional[int] = None,
        exclude_labels: Optional[list[str]] = None,
        created_after: Optional[str] = None,
        updated_after: Optional[str] = None,
    ) -> list[GitHubIssue]:
        """Search for issues across repositories.

        Args:
            query: Search query
            state: Issue state (open, closed, all)
            labels: List of labels to include
            language: Programming language filter
            limit: Maximum number of issues to return
            exclude_labels: List of labels to exclude
            created_after: Filter issues created after this date
            updated_after: Filter issues updated after this date

        Returns:
            List of GitHub issues
        """
        log_operation_start("github issues search", query=query)

        try:
            # Build search query
            search_parts = [query, f"state:{state}"]

            if labels:
                for label in labels:
                    search_parts.append(f'label:"{label}"')

            if language:
                search_parts.append(f"language:{language}")

            if created_after:
                search_parts.append(f"created:>={created_after}")

            if updated_after:
                search_parts.append(f"updated:>={updated_after}")

            search_query = " ".join(search_parts)

            # Search issues
            search_results: Any = self.github.search_issues(
                search_query, sort="updated", order="desc"
            )

            # Apply limit
            if limit:
                search_results = list(search_results)[:limit]

            # Filter out excluded labels
            if exclude_labels:
                search_results = [
                    issue
                    for issue in search_results
                    if not any(label.name in exclude_labels for label in issue.labels)
                ]

            # Convert to our data structure
            issues = []
            for issue in search_results:
                github_issue = GitHubIssue(
                    number=issue.number,
                    title=issue.title,
                    state=issue.state,
                    labels=[label.name for label in issue.labels],
                    assignees=[assignee.login for assignee in issue.assignees],
                    created_at=issue.created_at.isoformat(),
                    updated_at=issue.updated_at.isoformat(),
                    html_url=issue.html_url,
                    body=issue.body,
                    user=issue.user.login if issue.user else None,
                    milestone=issue.milestone.title if issue.milestone else None,
                    comments_count=issue.comments,
                    reactions_count=(
                        len(issue.get_reactions())
                        if hasattr(issue, "get_reactions")
                        else 0
                    ),
                )
                issues.append(github_issue)

            log_operation_success("github issues search", query=query)
            return issues

        except Exception as e:
            log_operation_failure("github issues search", e, query=query)
            raise APIError(f"Failed to search issues: {e}") from e

    def get_issues_for_repositories(
        self,
        repositories: list[str],
        state: str = "open",
        labels: Optional[list[str]] = None,
        exclude_labels: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        milestone: Optional[str] = None,
        limit_per_repo: Optional[int] = None,
        total_limit: Optional[int] = None,
        created_after: Optional[str] = None,
        updated_after: Optional[str] = None,
    ) -> dict[str, list[GitHubIssue]]:
        """Get issues for multiple repositories.

        Args:
            repositories: List of repository names
            state: Issue state (open, closed, all)
            labels: List of labels to include
            exclude_labels: List of labels to exclude
            assignee: Assignee filter
            milestone: Milestone filter
            limit_per_repo: Maximum issues per repository
            total_limit: Maximum total issues across all repositories
            created_after: Filter issues created after this date
            updated_after: Filter issues updated after this date

        Returns:
            Dictionary mapping repository names to lists of issues
        """
        log_operation_start(
            "github multi-repo issues fetch", repo_count=len(repositories)
        )

        try:
            all_issues: dict[str, list[GitHubIssue]] = {}
            total_issues = 0

            for repo_name in repositories:
                try:
                    repo_issues = self.get_issues(
                        repo_name=repo_name,
                        state=state,
                        labels=labels,
                        assignee=assignee,
                        milestone=milestone,
                        limit=limit_per_repo,
                        exclude_labels=exclude_labels,
                        created_after=created_after,
                        updated_after=updated_after,
                    )

                    all_issues[repo_name] = repo_issues
                    total_issues += len(repo_issues)

                    # Check total limit
                    if total_limit and total_issues >= total_limit:
                        break

                except Exception as e:
                    # Log error but continue with other repositories
                    self.logger.warning(f"Failed to fetch issues for {repo_name}: {e}")
                    all_issues[repo_name] = []

            log_operation_success(
                "github multi-repo issues fetch", repo_count=len(repositories)
            )
            return all_issues

        except Exception as e:
            log_operation_failure(
                "github multi-repo issues fetch", repo_count=len(repositories), error=e
            )
            raise APIError(
                f"Failed to fetch issues for multiple repositories: {e}"
            ) from e

    def get_rate_limit_status(self) -> dict[str, dict[str, int]]:
        """Get current rate limit status.

        Returns:
            Dictionary with rate limit information
        """
        try:
            rate_limit = self.github.get_rate_limit()

            def get_reset_timestamp(reset_value: Any) -> int:
                """Get reset timestamp, handling both datetime and int."""
                if hasattr(reset_value, "timestamp"):
                    return int(reset_value.timestamp())
                elif isinstance(reset_value, (int, float)):
                    return int(reset_value)
                else:
                    return 0

            return {
                "core": {
                    "limit": rate_limit.core.limit,
                    "remaining": rate_limit.core.remaining,
                    "reset": get_reset_timestamp(rate_limit.core.reset),
                },
                "search": {
                    "limit": rate_limit.search.limit,
                    "remaining": rate_limit.search.remaining,
                    "reset": get_reset_timestamp(rate_limit.search.reset),
                },
                "graphql": {
                    "limit": rate_limit.graphql.limit,
                    "remaining": rate_limit.graphql.remaining,
                    "reset": get_reset_timestamp(rate_limit.graphql.reset),
                },
            }
        except Exception as e:
            raise APIError(f"Failed to get rate limit status: {e}") from e

    def test_connection(self) -> bool:
        """Test connection to GitHub API.

        Returns:
            True if connection is successful
        """
        try:
            # Try to get current user to test connection
            self.github.get_user()
            return True
        except Exception:
            return False

    def get_user_info(self) -> dict[str, Any]:
        """Get current user information.

        Returns:
            Dictionary with user information
        """
        try:
            user = self.github.get_user()
            return {
                "login": user.login,
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "public_repos": user.public_repos,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        except Exception as e:
            raise APIError(f"Failed to get user info: {e}") from e

    def get_rate_limit_info(self) -> dict[str, Any]:
        """Get detailed rate limit information.

        Returns:
            Dictionary with detailed rate limit information
        """
        try:
            rate_limit = self.github.get_rate_limit()

            def get_reset_time(reset_value: Any) -> Optional[float]:
                """Get reset time as timestamp, handling both datetime and int."""
                if hasattr(reset_value, "timestamp"):
                    timestamp_result: float = reset_value.timestamp()
                    return timestamp_result
                elif isinstance(reset_value, (int, float)):
                    float_result: float = float(reset_value)
                    return float_result
                else:
                    return None

            return {
                "core": {
                    "limit": rate_limit.core.limit,
                    "remaining": rate_limit.core.remaining,
                    "reset": rate_limit.core.reset,
                    "reset_time": get_reset_time(rate_limit.core.reset),
                },
                "search": {
                    "limit": rate_limit.search.limit,
                    "remaining": rate_limit.search.remaining,
                    "reset": rate_limit.search.reset,
                    "reset_time": get_reset_time(rate_limit.search.reset),
                },
                "graphql": {
                    "limit": rate_limit.graphql.limit,
                    "remaining": rate_limit.graphql.remaining,
                    "reset": rate_limit.graphql.reset,
                    "reset_time": get_reset_time(rate_limit.graphql.reset),
                },
            }
        except Exception as e:
            raise APIError(f"Failed to get rate limit info: {e}") from e


def create_github_client(
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    base_url: str = "https://api.github.com",
    timeout: int = 30,
    connect_timeout: Optional[int] = None,
    read_timeout: Optional[int] = None,
    repo_path: Optional[str] = None,
    use_git_auth: bool = True,
) -> GitHubClient:
    """Create a GitHub client instance.

    Args:
        token: GitHub personal access token (fallback if Git auth fails)
        username: GitHub username (fallback if Git auth fails)
        password: GitHub password (fallback if Git auth fails)
        base_url: GitHub API base URL
        timeout: Request timeout in seconds
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
        repo_path: Optional repository path for local Git authentication
        use_git_auth: Whether to use Git-based authentication (default: True)

    Returns:
        Configured GitHub client instance
    """
    return GitHubClient(
        token=token,
        username=username,
        password=password,
        base_url=base_url,
        timeout=timeout,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
        repo_path=repo_path,
        use_git_auth=use_git_auth,
    )
