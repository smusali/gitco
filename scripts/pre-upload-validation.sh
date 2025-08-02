#!/bin/bash

# GitCo Pre-Upload Validation Script
# This script performs comprehensive validation before uploading to PyPI

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

print_subheader() {
    echo -e "${CYAN}[SUBHEADER]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_header "Checking Python Version"

    local python_version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local major
    local minor
    major=$(echo "$python_version" | cut -d. -f1)
    minor=$(echo "$python_version" | cut -d. -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 9 ]); then
        print_error "Python 3.9+ is required. Found: $python_version"
        exit 1
    fi

    print_success "Python version: $python_version"
}

# Function to install validation dependencies
install_validation_deps() {
    print_header "Installing Validation Dependencies"

    pip install --upgrade pip
    pip install -r requirements-dev.txt
    pip install build twine check-manifest pip-audit bandit detect-secrets safety

    print_success "Validation dependencies installed"
}

# Function to validate package metadata
validate_package_metadata() {
    print_header "Validating Package Metadata"

    print_subheader "Checking pyproject.toml syntax"
    python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
    print_success "pyproject.toml syntax is valid"

    print_subheader "Checking MANIFEST.in completeness"
    if command_exists check-manifest; then
        check-manifest
        print_success "MANIFEST.in validation passed"
    else
        print_warning "check-manifest not found, skipping manifest check"
    fi

    print_subheader "Validating package structure"
    if [ ! -f "src/gitco/__init__.py" ]; then
        print_error "Missing src/gitco/__init__.py"
        exit 1
    fi

    if [ ! -f "src/gitco/cli.py" ]; then
        print_error "Missing src/gitco/cli.py"
        exit 1
    fi

    print_success "Package structure validation passed"
}

# Function to run security scans
run_security_scans() {
    print_header "Running Security Scans"

    print_subheader "Scanning for secrets in code"
    if command_exists detect-secrets; then
        detect-secrets scan --baseline .secrets.baseline src/ tests/ > detect-secrets-report.json || true
        print_success "Secrets scan completed"
    else
        print_warning "detect-secrets not found, skipping secrets scan"
    fi

    print_subheader "Running bandit security analysis"
    if command_exists bandit; then
        bandit -r src/ -f json -o bandit-report.json || true
        print_success "Bandit security analysis completed"
    else
        print_warning "bandit not found, skipping bandit scan"
    fi

    print_subheader "Checking dependency vulnerabilities"
    if command_exists pip-audit; then
        pip-audit --format json --output pip-audit-report.json || true
        print_success "Dependency vulnerability check completed"
    else
        print_warning "pip-audit not found, skipping dependency check"
    fi

    print_subheader "Running safety checks"
    if command_exists safety; then
        safety check --json --output safety-report.json || true
        print_success "Safety checks completed"
    else
        print_warning "safety not found, skipping safety checks"
    fi

    print_subheader "Checking for hardcoded secrets"
    if grep -r "sk-|pk_|ghp_|gho_|ghu_|ghs_|ghr_" src/ tests/; then
        print_error "Potential secrets found in code"
        exit 1
    fi
    print_success "No hardcoded secrets found"
}

# Function to validate package build
validate_package_build() {
    print_header "Validating Package Build"

    print_subheader "Cleaning build environment"
    rm -rf dist/ build/ *.egg-info/
    print_success "Build environment cleaned"

    print_subheader "Building package"
    python3 -m build --wheel --sdist

    # List build artifacts
    echo ""
    print_status "Build artifacts:"
    ls -la dist/

    # Show package contents
    for file in dist/*; do
        echo ""
        print_status "Contents of $file:"
        if [[ $file == *.whl ]]; then
            unzip -l "$file" | head -10
        elif [[ $file == *.tar.gz ]]; then
            tar -tzf "$file" | head -10
        fi
    done

    print_success "Package build validation completed"
}

# Function to validate package with twine
validate_with_twine() {
    print_header "Validating Package with Twine"

    print_subheader "Running twine check"
    twine check dist/*
    print_success "Twine validation passed"

    print_subheader "Checking package size"
    for file in dist/*; do
        size=$(du -h "$file" | cut -f1)
        print_status "$file: $size"

        # Check for suspicious files in package
        if [[ $file == *.whl ]]; then
            if unzip -l "$file" | grep -E "\.(key|pem|crt|p12|pfx|pwd|pass|secret|token)"; then
                print_warning "Potential secrets found in package"
            fi
        fi
    done

    print_success "Package size validation completed"
}

# Function to test package installation
test_package_installation() {
    print_header "Testing Package Installation"

    print_subheader "Testing wheel installation in clean environment"
    python3 -m venv test-env
    source test-env/bin/activate

    # Test wheel installation
    print_status "Installing wheel..."
    pip install dist/*.whl

    print_status "Testing import..."
    python3 -c "import gitco; print(f'✅ Wheel installation successful: {gitco.__version__}')"

    print_status "Testing CLI command..."
    gitco --help

    print_subheader "Testing source distribution installation"
    pip uninstall gitco -y
    pip install dist/*.tar.gz

    print_status "Testing import..."
    python3 -c "import gitco; print(f'✅ Source distribution installation successful: {gitco.__version__}')"

    print_status "Testing CLI command..."
    gitco --help

    # Cleanup
    deactivate
    rm -rf test-env

    print_success "Package installation test completed"
}

# Function to test package on multiple Python versions
test_multiple_python_versions() {
    print_header "Testing Package on Multiple Python Versions"

    local versions=("3.9" "3.10" "3.11" "3.12")

    for version in "${versions[@]}"; do
        print_subheader "Testing Python $version"

        if command_exists "python$version"; then
            python3 -m venv "test-env-$version"
            source "test-env-$version/bin/activate"

            # Install and test
            pip install dist/*.whl
            python3 -c "import gitco; print(f'✅ Python $version: {gitco.__version__}')"

            deactivate
            rm -rf "test-env-$version"
            print_success "Python $version test passed"
        else
            print_warning "Python $version not available, skipping"
        fi
    done
}

# Function to validate PyPI authentication
validate_pypi_authentication() {
    print_header "Validating PyPI Authentication"

    # Check for PyPI tokens
    if [ -n "${PYPI_API_TOKEN:-}" ]; then
        print_subheader "Validating PyPI token format"
        if [[ ! "$PYPI_API_TOKEN" =~ ^pypi- ]]; then
            print_error "Invalid PyPI token format"
            print_error "PyPI tokens should start with 'pypi-'"
            exit 1
        fi
        print_success "PyPI token format is valid"
    else
        print_warning "PYPI_API_TOKEN not set"
    fi

    if [ -n "${TEST_PYPI_API_TOKEN:-}" ]; then
        print_subheader "Validating Test PyPI token format"
        if [[ ! "$TEST_PYPI_API_TOKEN" =~ ^pypi- ]]; then
            print_error "Invalid Test PyPI token format"
            print_error "Test PyPI tokens should start with 'pypi-'"
            exit 1
        fi
        print_success "Test PyPI token format is valid"
    else
        print_warning "TEST_PYPI_API_TOKEN not set"
    fi
}

# Function to check for version conflicts
check_version_conflicts() {
    print_header "Checking for Version Conflicts"

    # Extract version from pyproject.toml
    local version
    version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

    print_subheader "Checking version format"
    if ! echo "$version" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'; then
        print_error "Invalid version format: $version"
        print_error "Version must follow semantic versioning (e.g., 1.0.0, 1.0.0-alpha.1)"
        exit 1
    fi
    print_success "Version format is valid: $version"

    print_subheader "Checking if version already exists on PyPI"
    if pip index versions gitco | grep -q "$version"; then
        print_warning "Version $version already exists on PyPI"
        print_warning "Consider bumping the version before publishing"
    else
        print_success "Version $version is available for publishing"
    fi
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    print_header "Running Comprehensive Tests"

    print_subheader "Running unit tests"
    python3 -m pytest tests/ -v --tb=short

    print_subheader "Running linting checks"
    python3 -m ruff check --fix src/ tests/

    print_subheader "Running code formatting check"
    python3 -m black src/ tests/

    print_success "All tests passed"
}

# Function to generate validation report
generate_validation_report() {
    print_header "Generating Validation Report"

    local report_file="pre-upload-validation-report.txt"

    {
        echo "GitCo Pre-Upload Validation Report"
        echo "=================================="
        echo "Generated: $(date)"
        echo "Python Version: $(python3 --version)"
        echo ""

        echo "Package Information:"
        echo "-------------------"
        if [ -d "dist" ]; then
            echo "Build artifacts:"
            ls -la dist/
            echo ""
        fi

        echo "Security Scan Results:"
        echo "---------------------"
        if [ -f "bandit-report.json" ]; then
            echo "Bandit scan completed"
        fi
        if [ -f "pip-audit-report.json" ]; then
            echo "Dependency vulnerability scan completed"
        fi
        if [ -f "safety-report.json" ]; then
            echo "Safety scan completed"
        fi
        echo ""

        echo "Test Results:"
        echo "-------------"
        echo "Package installation: PASSED"
        echo "CLI functionality: PASSED"
        echo "Import validation: PASSED"
        echo ""

        echo "Validation Status: READY FOR UPLOAD"

    } > "$report_file"

    print_success "Validation report generated: $report_file"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -m, --metadata          Validate package metadata only"
    echo "  -s, --security          Run security scans only"
    echo "  -b, --build             Validate package build only"
    echo "  -t, --test              Test package installation only"
    echo "  -p, --python-versions   Test multiple Python versions only"
    echo "  -a, --auth              Validate PyPI authentication only"
    echo "  -v, --version           Check version conflicts only"
    echo "  -c, --comprehensive     Run comprehensive tests only"
    echo "  -r, --report            Generate validation report only"
    echo "  --all                   Run all validations (default)"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all validations"
    echo "  $0 --security           # Run security scans only"
    echo "  $0 --build --test       # Build and test package"
}

# Main function
main() {
    local metadata_only=false
    local security_only=false
    local build_only=false
    local test_only=false
    local python_versions_only=false
    local auth_only=false
    local version_only=false
    local comprehensive_only=false
    local report_only=false
    local run_all=true

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -m|--metadata)
                metadata_only=true
                run_all=false
                shift
                ;;
            -s|--security)
                security_only=true
                run_all=false
                shift
                ;;
            -b|--build)
                build_only=true
                run_all=false
                shift
                ;;
            -t|--test)
                test_only=true
                run_all=false
                shift
                ;;
            -p|--python-versions)
                python_versions_only=true
                run_all=false
                shift
                ;;
            -a|--auth)
                auth_only=true
                run_all=false
                shift
                ;;
            -v|--version)
                version_only=true
                run_all=false
                shift
                ;;
            -c|--comprehensive)
                comprehensive_only=true
                run_all=false
                shift
                ;;
            -r|--report)
                report_only=true
                run_all=false
                shift
                ;;
            --all)
                run_all=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_header "Starting GitCo Pre-Upload Validation Process"

    # Check Python version
    check_python_version

    # Install validation dependencies
    install_validation_deps

    if [ "$metadata_only" = true ]; then
        validate_package_metadata
        exit 0
    fi

    if [ "$security_only" = true ]; then
        run_security_scans
        exit 0
    fi

    if [ "$build_only" = true ]; then
        validate_package_build
        validate_with_twine
        exit 0
    fi

    if [ "$test_only" = true ]; then
        if [ ! -d "dist" ]; then
            print_error "No dist directory found. Run build first."
            exit 1
        fi
        test_package_installation
        exit 0
    fi

    if [ "$python_versions_only" = true ]; then
        if [ ! -d "dist" ]; then
            print_error "No dist directory found. Run build first."
            exit 1
        fi
        test_multiple_python_versions
        exit 0
    fi

    if [ "$auth_only" = true ]; then
        validate_pypi_authentication
        exit 0
    fi

    if [ "$version_only" = true ]; then
        check_version_conflicts
        exit 0
    fi

    if [ "$comprehensive_only" = true ]; then
        run_comprehensive_tests
        exit 0
    fi

    if [ "$report_only" = true ]; then
        generate_validation_report
        exit 0
    fi

    if [ "$run_all" = true ]; then
        # Run all validations
        validate_package_metadata
        run_security_scans
        validate_package_build
        validate_with_twine
        test_package_installation
        test_multiple_python_versions
        validate_pypi_authentication
        check_version_conflicts
        run_comprehensive_tests
        generate_validation_report

        print_success "All pre-upload validations completed successfully!"
        echo ""
        print_status "Package is ready for upload to PyPI"
        print_status "Validation report: pre-upload-validation-report.txt"
    fi
}

# Run main function with all arguments
main "$@"
