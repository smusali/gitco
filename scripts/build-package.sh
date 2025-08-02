#!/bin/bash

# GitCo Package Building Script
# This script helps build and test the GitCo package locally

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
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

# Function to install build dependencies
install_build_deps() {
    print_status "Installing build dependencies..."

    if ! command_exists pip; then
        print_error "pip is not installed"
        exit 1
    fi

    pip install --upgrade pip
    pip install build twine check-manifest pip-audit

    print_success "Build dependencies installed"
}

# Function to clean build environment
clean_build() {
    print_status "Cleaning build environment..."

    rm -rf dist/ build/ *.egg-info/

    print_success "Build environment cleaned"
}

# Function to validate package metadata
validate_metadata() {
    print_status "Validating package metadata..."

    # Check manifest completeness
    if command_exists check-manifest; then
        check-manifest
    else
        print_warning "check-manifest not found, skipping manifest check"
    fi

    # Validate pyproject.toml
    python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

    print_success "Package metadata validation passed"
}

# Function to build package
build_package() {
    print_status "Building package..."

    # Build both wheel and source distribution
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

    print_success "Package build completed"
}

# Function to validate package security
validate_security() {
    print_status "Validating package security..."

    # Check for security issues
    pip-audit --format json --output pip-audit.json || true

    # Validate package with twine
    twine check dist/*

    # Check package size
    for file in dist/*; do
        size=$(du -h "$file" | cut -f1)
        print_status "$file: $size"
    done

    print_success "Package security validation completed"
}

# Function to test package installation
test_installation() {
    print_status "Testing package installation..."

    # Create test environment
    python3 -m venv test-env
    source test-env/bin/activate

    # Test wheel installation
    print_status "Testing wheel installation..."
    pip install dist/*.whl
    python3 -c "import gitco; print(f'✅ Wheel installation successful: {gitco.__version__}')"

    # Test CLI command
    gitco --help

    # Test source distribution
    print_status "Testing source distribution installation..."
    pip uninstall gitco -y
    pip install dist/*.tar.gz
    python3 -c "import gitco; print(f'✅ Source distribution installation successful: {gitco.__version__}')"

    # Test CLI functionality
    gitco --help

    # Cleanup
    deactivate
    rm -rf test-env

    print_success "Package installation test completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -c, --clean         Clean build environment only"
    echo "  -v, --validate      Validate package metadata only"
    echo "  -b, --build         Build package only"
    echo "  -s, --security      Validate package security only"
    echo "  -t, --test          Test package installation only"
    echo "  -a, --all           Run all steps (default)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Run all steps"
    echo "  $0 --clean          # Clean build environment"
    echo "  $0 --build --test   # Build and test package"
}

# Main function
main() {
    local clean_only=false
    local validate_only=false
    local build_only=false
    local security_only=false
    local test_only=false
    local run_all=true

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--clean)
                clean_only=true
                run_all=false
                shift
                ;;
            -v|--validate)
                validate_only=true
                run_all=false
                shift
                ;;
            -b|--build)
                build_only=true
                run_all=false
                shift
                ;;
            -s|--security)
                security_only=true
                run_all=false
                shift
                ;;
            -t|--test)
                test_only=true
                run_all=false
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_status "Starting GitCo package build process..."

    # Check Python version
    check_python_version

    # Install build dependencies
    install_build_deps

    if [ "$clean_only" = true ]; then
        clean_build
        exit 0
    fi

    if [ "$validate_only" = true ]; then
        validate_metadata
        exit 0
    fi

    if [ "$build_only" = true ]; then
        clean_build
        build_package
        exit 0
    fi

    if [ "$security_only" = true ]; then
        if [ ! -d "dist" ]; then
            print_error "No dist directory found. Run build first."
            exit 1
        fi
        validate_security
        exit 0
    fi

    if [ "$test_only" = true ]; then
        if [ ! -d "dist" ]; then
            print_error "No dist directory found. Run build first."
            exit 1
        fi
        test_installation
        exit 0
    fi

    if [ "$run_all" = true ]; then
        # Run all steps
        clean_build
        validate_metadata
        build_package
        validate_security
        test_installation

        print_success "All package build steps completed successfully!"
        echo ""
        print_status "Package files are ready in the dist/ directory"
        print_status "To publish to PyPI, use: twine upload dist/*"
    fi
}

# Run main function with all arguments
main "$@"
