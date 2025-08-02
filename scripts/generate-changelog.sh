#!/bin/bash

# GitCo Changelog Generator
# This script generates a changelog from conventional commits for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 GitCo Changelog Generator${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if conventional-changelog-cli is installed
if ! command -v conventional-changelog &> /dev/null; then
    echo -e "${YELLOW}⚠️  conventional-changelog-cli not found. Installing...${NC}"
    npm install -g conventional-changelog-cli
fi

# Check if we're in the git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not in a git repository.${NC}"
    exit 1
fi

# Check if configuration file exists
if [ ! -f ".conventional-changelog.json" ]; then
    echo -e "${RED}❌ .conventional-changelog.json not found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Function to generate changelog
generate_changelog() {
    local output_file="$1"
    local version="$2"

    echo -e "${BLUE}📝 Generating changelog...${NC}"

    # Generate changelog from conventional commits
    conventional-changelog -c .conventional-changelog.json -i CHANGELOG.md -s -r 0 > "$output_file"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Changelog generated successfully${NC}"
        echo -e "${BLUE}📄 Output file: $output_file${NC}"

        # Show preview
        echo ""
        echo -e "${YELLOW}📋 Preview (first 20 lines):${NC}"
        echo "----------------------------------------"
        head -n 20 "$output_file"
        echo "----------------------------------------"
    else
        echo -e "${RED}❌ Failed to generate changelog${NC}"
        exit 1
    fi
}

# Function to update main changelog
update_main_changelog() {
    local temp_file="$1"

    echo -e "${BLUE}🔄 Updating main CHANGELOG.md...${NC}"

    # Create new changelog with header
    cat > CHANGELOG.md << EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

EOF

    # Append generated content
    cat "$temp_file" >> CHANGELOG.md

    echo -e "${GREEN}✅ CHANGELOG.md updated${NC}"
}

# Function to generate release notes
generate_release_notes() {
    local output_file="$1"

    echo -e "${BLUE}📝 Generating release notes...${NC}"

    # Generate release notes (first 100 lines)
    conventional-changelog -c .conventional-changelog.json -i CHANGELOG.md -s -r 0 | head -n 100 > "$output_file"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Release notes generated successfully${NC}"
        echo -e "${BLUE}📄 Output file: $output_file${NC}"
    else
        echo -e "${RED}❌ Failed to generate release notes${NC}"
        exit 1
    fi
}

# Main execution
case "${1:-preview}" in
    "preview")
        echo -e "${YELLOW}🔍 Generating preview changelog...${NC}"
        generate_changelog "CHANGELOG.preview.md"
        echo ""
        echo -e "${GREEN}✅ Preview complete. Check CHANGELOG.preview.md${NC}"
        ;;
    "update")
        echo -e "${YELLOW}🔄 Updating main changelog...${NC}"
        generate_changelog "CHANGELOG.tmp.md"
        update_main_changelog "CHANGELOG.tmp.md"
        generate_release_notes "RELEASE_NOTES.md"
        rm -f "CHANGELOG.tmp.md"
        echo ""
        echo -e "${GREEN}✅ Main changelog updated successfully${NC}"
        ;;
    "release")
        echo -e "${YELLOW}🚀 Preparing release changelog...${NC}"
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Version required for release mode${NC}"
            echo "Usage: $0 release <version>"
            echo "Example: $0 release 1.0.0"
            exit 1
        fi
        generate_changelog "CHANGELOG.tmp.md"
        update_main_changelog "CHANGELOG.tmp.md"
        generate_release_notes "RELEASE_NOTES.md"
        rm -f "CHANGELOG.tmp.md"
        echo ""
        echo -e "${GREEN}✅ Release changelog prepared for version $2${NC}"
        ;;
    "help"|"-h"|"--help")
        echo "GitCo Changelog Generator"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  preview    Generate a preview changelog (default)"
        echo "  update     Update the main CHANGELOG.md file"
        echo "  release    Prepare release changelog with version"
        echo "  help       Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Generate preview"
        echo "  $0 preview           # Generate preview"
        echo "  $0 update            # Update main changelog"
        echo "  $0 release 1.0.0     # Prepare release for v1.0.0"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Done!${NC}"
