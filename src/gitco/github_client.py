"""GitHub API client for GitCo."""

import os
from dataclasses import dataclass
from typing import Any, Optional

from github import Github, GithubException

from .utils.common import (
    log_api_call,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)
from .utils.exception import (
    APIError,
    GitHubAuthenticationError,
)
from .utils.rate_limiter import RateLimitedAPIClient, get_rate_limiter
from .utils.retry import DEFAULT_RETRY_CONFIG, create_retry_session, with_retry


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


class GitHubClient(RateLimitedAPIClient):
    """GitHub API client with authentication and rate limiting."""

    def __init__(
        self,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token (preferred)
            username: GitHub username (for basic auth)
            password: GitHub password (for basic auth)
            base_url: GitHub API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Initialize rate limiter
        rate_limiter = get_rate_limiter("github")
        super().__init__(rate_limiter)

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create session with retry capabilities
        self.session = create_retry_session(
            max_attempts=max_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504, 429],
        )

        # Set up authentication
        self._setup_authentication(token, username, password)

        # Initialize PyGithub client
        self._init_github_client(token, username, password)

    def _setup_authentication(
        self,
        token: Optional[str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """Set up authentication for requests session.

        Args:
            token: GitHub personal access token
            username: GitHub username
            password: GitHub password
        """
        if token:
            self.session.headers.update(
                {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "GitCo/1.0.0",
                }
            )
            self.logger.debug("Using token authentication")
        elif username and password:
            self.session.auth = (username, password)
            self.session.headers.update(
                {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "GitCo/1.0.0",
                }
            )
            self.logger.debug("Using basic authentication")
        else:
            # Try to get token from environment
            token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN")
            if token:
                self.session.headers.update(
                    {
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "GitCo/1.0.0",
                    }
                )
                self.logger.debug("Using token from environment")
            else:
                # Anonymous access (limited)
                self.session.headers.update(
                    {
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "GitCo/1.0.0",
                    }
                )
                self.logger.warning("No authentication provided - limited API access")

    def _init_github_client(
        self,
        token: Optional[str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """Initialize PyGithub client.

        Args:
            token: GitHub personal access token
            username: GitHub username
            password: GitHub password
        """
        try:
            if token:
                self.github = Github(token, base_url=self.base_url)
            elif username and password:
                self.github = Github(username, password, base_url=self.base_url)
            else:
                # Try environment token
                env_token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN")
                if env_token:
                    self.github = Github(env_token, base_url=self.base_url)
                else:
                    # Anonymous access
                    self.github = Github(base_url=self.base_url)

            # Test authentication
            self._test_authentication()

        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub client: {e}")
            raise GitHubAuthenticationError(f"GitHub authentication failed: {e}") from e

    def _test_authentication(self) -> None:
        """Test GitHub authentication."""
        try:
            user = self.github.get_user()
            self.logger.info(f"Authenticated as: {user.login}")
        except GithubException as e:
            if e.status == 401:
                raise GitHubAuthenticationError("Invalid GitHub credentials") from e
            elif e.status == 403:
                raise GitHubAuthenticationError("GitHub API access denied") from e
            else:
                raise GitHubAuthenticationError(
                    f"GitHub authentication test failed: {e}"
                ) from e

    def _rate_limit_request(self) -> None:
        """Implement rate limiting between requests."""
        self.rate_limiter.wait_if_needed()

    @with_retry(config=DEFAULT_RETRY_CONFIG)
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
            GitHubRateLimitExceeded: When rate limit is exceeded
            APIError: When API request fails
        """
        url = f"{self.base_url}{endpoint}"

        self._rate_limit_request()

        log_api_call("github", endpoint, "started")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=self.timeout,
        )

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
        log_operation_start("github repository fetch", repo_name=repo_name)

        try:
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

        except GithubException as e:
            if e.status == 404:
                self.logger.warning(f"Repository not found: {repo_name}")
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
        """Get issues from repository with advanced filtering.

        Args:
            repo_name: Repository name (owner/repo)
            state: Issue state (open, closed, all)
            labels: Filter by labels (include)
            assignee: Filter by assignee
            milestone: Filter by milestone
            limit: Maximum number of issues to return
            exclude_labels: Filter by labels (exclude)
            created_after: Filter issues created after this date (ISO format)
            updated_after: Filter issues updated after this date (ISO format)

        Returns:
            List of issues
        """
        log_operation_start("github issues fetch", repo_name=repo_name, state=state)

        try:
            repo = self.github.get_repo(repo_name)

            # Build query parameters for PyGithub
            # PyGithub expects specific types, so we need to handle them properly
            all_issues = repo.get_issues(state=state)

            # Apply additional filtering after fetching
            filtered_issues = []
            for issue in all_issues:
                # Filter by labels if specified
                if labels:
                    issue_labels = [label.name for label in issue.labels]
                    if not any(label in issue_labels for label in labels):
                        continue

                # Filter by assignee if specified
                if assignee:
                    issue_assignees = [assignee.login for assignee in issue.assignees]
                    if assignee not in issue_assignees:
                        continue

                # Filter by milestone if specified
                if milestone and issue.milestone:
                    if issue.milestone.title != milestone:
                        continue
                elif milestone and not issue.milestone:
                    continue

                filtered_issues.append(issue)

            issues = filtered_issues

            # Convert to our data structure with additional filtering
            github_issues = []
            count = 0

            for issue in issues:
                if limit and count >= limit:
                    break

                # Apply additional filters
                if exclude_labels and any(
                    label in exclude_labels
                    for label in [label.name for label in issue.labels]
                ):
                    continue

                if created_after and issue.created_at.isoformat() < created_after:
                    continue

                if updated_after and issue.updated_at.isoformat() < updated_after:
                    continue

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
                    reactions_count=getattr(issue.reactions, "totalCount", 0),
                )

                github_issues.append(github_issue)
                count += 1

            log_operation_success(
                "github issues fetch", repo_name=repo_name, count=len(github_issues)
            )
            return github_issues

        except GithubException as e:
            log_operation_failure("github issues fetch", e, repo_name=repo_name)
            raise APIError(f"Failed to fetch issues from {repo_name}: {e}") from e

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
        """Search for issues across repositories with advanced filtering.

        Args:
            query: Search query
            state: Issue state (open, closed, all)
            labels: Filter by labels (include)
            language: Filter by programming language
            limit: Maximum number of issues to return
            exclude_labels: Filter by labels (exclude)
            created_after: Filter issues created after this date (ISO format)
            updated_after: Filter issues updated after this date (ISO format)

        Returns:
            List of matching issues
        """
        log_operation_start("github issues search", query=query, state=state)

        try:
            # Build search query
            search_query = query
            if state != "all":
                search_query += f" state:{state}"
            if labels:
                search_query += f" label:{','.join(labels)}"
            if language:
                search_query += f" language:{language}"

            issues = self.github.search_issues(search_query)

            # Convert to our data structure with additional filtering
            github_issues = []
            count = 0

            for issue in issues:
                if limit and count >= limit:
                    break

                # Apply additional filters
                if exclude_labels and any(
                    label in exclude_labels
                    for label in [label.name for label in issue.labels]
                ):
                    continue

                if created_after and issue.created_at.isoformat() < created_after:
                    continue

                if updated_after and issue.updated_at.isoformat() < updated_after:
                    continue

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
                    reactions_count=getattr(issue.reactions, "totalCount", 0),
                )

                github_issues.append(github_issue)
                count += 1

            log_operation_success(
                "github issues search", query=query, count=len(github_issues)
            )
            return github_issues

        except GithubException as e:
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
        """Get issues from multiple repositories with advanced filtering.

        Args:
            repositories: List of repository names (owner/repo)
            state: Issue state (open, closed, all)
            labels: Filter by labels (include)
            exclude_labels: Filter by labels (exclude)
            assignee: Filter by assignee
            milestone: Filter by milestone
            limit_per_repo: Maximum number of issues per repository
            total_limit: Maximum total number of issues across all repositories
            created_after: Filter issues created after this date (ISO format)
            updated_after: Filter issues updated after this date (ISO format)

        Returns:
            Dictionary mapping repository names to lists of issues
        """
        log_operation_start(
            "github issues fetch multiple repos",
            repositories=repositories,
            state=state,
        )

        try:
            all_issues: dict[str, list[GitHubIssue]] = {}
            total_count = 0

            for repo_name in repositories:
                if total_limit and total_count >= total_limit:
                    break

                try:
                    repo_issues = self.get_issues(
                        repo_name=repo_name,
                        state=state,
                        labels=labels,
                        exclude_labels=exclude_labels,
                        assignee=assignee,
                        milestone=milestone,
                        limit=limit_per_repo,
                        created_after=created_after,
                        updated_after=updated_after,
                    )

                    all_issues[repo_name] = repo_issues
                    total_count += len(repo_issues)

                except Exception as e:
                    # Log error but continue with other repositories
                    self.logger.warning(f"Failed to fetch issues from {repo_name}: {e}")
                    all_issues[repo_name] = []

            log_operation_success(
                "github issues fetch multiple repos",
                repositories=repositories,
                total_count=total_count,
            )
            return all_issues

        except Exception as e:
            log_operation_failure("github issues fetch multiple repos", e)
            raise APIError(
                f"Failed to fetch issues from multiple repositories: {e}"
            ) from e

    def get_rate_limit_status(self) -> dict[str, dict[str, int]]:
        """Get current rate limit status.

        Returns:
            Rate limit information
        """
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core": {
                    "limit": rate_limit.core.limit,  # type: ignore[attr-defined]
                    "remaining": rate_limit.core.remaining,  # type: ignore[attr-defined]
                    "reset": int(rate_limit.core.reset.timestamp()),  # type: ignore[attr-defined]
                },
                "search": {
                    "limit": rate_limit.search.limit,  # type: ignore[attr-defined]
                    "remaining": rate_limit.search.remaining,  # type: ignore[attr-defined]
                    "reset": int(rate_limit.search.reset.timestamp()),  # type: ignore[attr-defined]
                },
            }
        except GithubException as e:
            raise APIError(f"Failed to get rate limit status: {e}") from e

    def test_connection(self) -> bool:
        """Test GitHub API connection.

        Returns:
            True if connection is successful
        """
        try:
            self.github.get_rate_limit()
            return True
        except Exception as e:
            self.logger.error(f"GitHub API connection test failed: {e}")
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
                "name": user.name,
                "email": user.email,
                "id": user.id,
                "type": user.type,
            }
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            raise APIError(f"Failed to get user info: {e}") from e

    def get_rate_limit_info(self) -> dict[str, Any]:
        """Get rate limit information.

        Returns:
            Dictionary with rate limit information
        """
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core": {
                    "limit": rate_limit.core.limit,  # type: ignore[attr-defined]
                    "remaining": rate_limit.core.remaining,  # type: ignore[attr-defined]
                    "reset": (
                        int(rate_limit.core.reset.timestamp())  # type: ignore[attr-defined]
                        if hasattr(rate_limit.core.reset, "timestamp")  # type: ignore[attr-defined]
                        else rate_limit.core.reset  # type: ignore[attr-defined]
                    ),
                },
                "search": {
                    "limit": rate_limit.search.limit,  # type: ignore[attr-defined]
                    "remaining": rate_limit.search.remaining,  # type: ignore[attr-defined]
                    "reset": (
                        int(rate_limit.search.reset.timestamp())  # type: ignore[attr-defined]
                        if hasattr(rate_limit.search.reset, "timestamp")  # type: ignore[attr-defined]
                        else rate_limit.search.reset  # type: ignore[attr-defined]
                    ),
                },
            }
        except Exception as e:
            self.logger.error(f"Failed to get rate limit info: {e}")
            raise APIError(f"Failed to get rate limit info: {e}") from e


def create_github_client(
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    base_url: str = "https://api.github.com",
) -> GitHubClient:
    """Create a GitHub client instance.

    Args:
        token: GitHub personal access token
        username: GitHub username
        password: GitHub password
        base_url: GitHub API base URL

    Returns:
        Configured GitHub client
    """
    return GitHubClient(
        token=token,
        username=username,
        password=password,
        base_url=base_url,
    )
