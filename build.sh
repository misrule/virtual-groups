#!/bin/bash
# Build script for Virtual Groups Blender extension
# Usage: ./build.sh [command] [options]

set -e  # Exit on error

# Configuration
BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/blender"
SOURCE_DIR="./virtual_groups"
OUTPUT_DIR="./dist"
MANIFEST_FILE="$SOURCE_DIR/blender_manifest.toml"
INIT_FILE="$SOURCE_DIR/__init__.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Get current version from manifest
get_version() {
    grep '^version = ' "$MANIFEST_FILE" | cut -d'"' -f2
}

# Update version in manifest
update_manifest_version() {
    local new_version=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^version = \".*\"/version = \"$new_version\"/" "$MANIFEST_FILE"
    else
        sed -i "s/^version = \".*\"/version = \"$new_version\"/" "$MANIFEST_FILE"
    fi
}

# Update version in __init__.py bl_info
update_init_version() {
    local new_version=$1
    local major=$(echo "$new_version" | cut -d. -f1)
    local minor=$(echo "$new_version" | cut -d. -f2)
    local patch=$(echo "$new_version" | cut -d. -f3)

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/\"version\": ([0-9]*, [0-9]*, [0-9]*)/\"version\": ($major, $minor, $patch)/" "$INIT_FILE"
    else
        sed -i "s/\"version\": ([0-9]*, [0-9]*, [0-9]*)/\"version\": ($major, $minor, $patch)/" "$INIT_FILE"
    fi
}

# Increment version
bump_version() {
    local current_version=$1
    local bump_type=$2

    local major=$(echo "$current_version" | cut -d. -f1)
    local minor=$(echo "$current_version" | cut -d. -f2)
    local patch=$(echo "$current_version" | cut -d. -f3)

    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type: $bump_type (use: major, minor, or patch)"
            exit 1
            ;;
    esac

    echo "$major.$minor.$patch"
}

# Check if Blender exists
check_blender() {
    if [ ! -f "$BLENDER_PATH" ]; then
        print_error "Blender not found at: $BLENDER_PATH"
        print_info "Please update BLENDER_PATH in this script"
        exit 1
    fi
}

# Clean build artifacts
cmd_clean() {
    print_header "Cleaning build artifacts"

    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"
        print_success "Removed $OUTPUT_DIR"
    else
        print_info "Nothing to clean"
    fi

    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    print_success "Cleaned Python cache"
}

# Validate manifest
cmd_validate() {
    print_header "Validating extension manifest"
    check_blender

    cd "$(dirname "$0")"

    # Simple validation - check required fields exist
    local required_fields=("schema_version" "id" "version" "name" "type" "blender_version_min")
    local valid=true

    for field in "${required_fields[@]}"; do
        if ! grep -q "^$field = " "$MANIFEST_FILE"; then
            print_error "Missing required field: $field"
            valid=false
        fi
    done

    if [ "$valid" = true ]; then
        print_success "Manifest validation passed"
        local version=$(get_version)
        print_info "Current version: $version"
    else
        print_error "Manifest validation failed"
        exit 1
    fi
}

# Build extension package
cmd_build() {
    print_header "Building extension package"
    check_blender

    cd "$(dirname "$0")"

    # Validate first
    cmd_validate

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    local version=$(get_version)
    print_info "Building version: $version"

    # Build with Blender
    "$BLENDER_PATH" --command extension build \
        --source-dir "$SOURCE_DIR" \
        --output-dir "$OUTPUT_DIR" \
        2>&1 | grep -E "(building|created|Error|FATAL)" || true

    local package_name="virtual_groups-$version.zip"

    if [ -f "$OUTPUT_DIR/$package_name" ]; then
        local size=$(du -h "$OUTPUT_DIR/$package_name" | cut -f1)
        print_success "Built: $OUTPUT_DIR/$package_name ($size)"
        return 0
    else
        print_error "Build failed - package not created"
        exit 1
    fi
}

# Install extension for testing
cmd_install() {
    print_header "Installing extension for testing"
    check_blender

    cd "$(dirname "$0")"

    local version=$(get_version)
    local package_name="virtual_groups-$version.zip"
    local package_path="$OUTPUT_DIR/$package_name"

    if [ ! -f "$package_path" ]; then
        print_warning "Package not found - building first"
        cmd_build
    fi

    print_info "Installing: $package_name"

    "$BLENDER_PATH" --command extension install-file \
        -r "user_default" \
        --enable "$package_path" \
        2>&1 | grep -E "(STATUS|Installed|Error)" || true

    print_success "Installation complete"
    print_info "Restart Blender to see changes"
}

# Bump version
cmd_version() {
    local bump_type=$1

    if [ -z "$bump_type" ]; then
        print_error "Usage: ./build.sh version [major|minor|patch]"
        exit 1
    fi

    print_header "Bumping version ($bump_type)"

    local current_version=$(get_version)
    local new_version=$(bump_version "$current_version" "$bump_type")

    print_info "Current version: $current_version"
    print_info "New version: $new_version"

    # Update manifest
    update_manifest_version "$new_version"
    print_success "Updated $MANIFEST_FILE"

    # Update __init__.py
    update_init_version "$new_version"
    print_success "Updated $INIT_FILE"

    print_success "Version bumped to $new_version"
    print_warning "Don't forget to commit these changes!"
}

# Run tests
cmd_test() {
    print_header "Running tests"

    cd "$(dirname "$0")"

    if [ -f "tests/run_tests.py" ]; then
        python3 tests/run_tests.py
        print_success "All tests passed"
    else
        print_error "Test runner not found"
        exit 1
    fi
}

# Full release workflow
cmd_release() {
    local bump_type=$1

    if [ -z "$bump_type" ]; then
        print_error "Usage: ./build.sh release [major|minor|patch]"
        exit 1
    fi

    print_header "Release Workflow"

    # Run tests
    print_info "Step 1: Running tests..."
    cmd_test

    # Bump version
    print_info "Step 2: Bumping version..."
    cmd_version "$bump_type"

    local new_version=$(get_version)

    # Clean and build
    print_info "Step 3: Building package..."
    cmd_clean
    cmd_build

    # Git operations
    print_info "Step 4: Git operations..."
    git add "$MANIFEST_FILE" "$INIT_FILE"
    git commit -m "Bump version to $new_version"
    git tag -a "v$new_version" -m "Release v$new_version"

    print_success "Release prepared: v$new_version"
    print_warning "Review the changes, then run:"
    echo "  git push origin main"
    echo "  git push origin v$new_version"
    echo ""
    print_info "To create GitHub release:"
    echo "  gh release create v$new_version \\"
    echo "    --title \"Virtual Groups v$new_version\" \\"
    echo "    --generate-notes \\"
    echo "    ./dist/virtual_groups-$new_version.zip"
}

# Show help
cmd_help() {
    cat << EOF
Virtual Groups Build Script

Usage:
  ./build.sh [command] [options]

Commands:
  clean              Clean build artifacts and Python cache
  validate           Validate the extension manifest
  build              Build the extension package
  install            Install the extension to Blender for testing
  test               Run the test suite
  version <type>     Bump version (major|minor|patch)
  release <type>     Full release workflow (test, bump, build, git)
  help               Show this help message

Examples:
  ./build.sh build              # Build the current version
  ./build.sh version patch      # Bump patch version (0.1.0 -> 0.1.1)
  ./build.sh release minor      # Full release workflow (bump minor)
  ./build.sh clean build        # Clean and build

Configuration:
  BLENDER_PATH: $BLENDER_PATH
  SOURCE_DIR:   $SOURCE_DIR
  OUTPUT_DIR:   $OUTPUT_DIR

EOF
}

# Main command dispatcher
main() {
    local command=${1:-help}
    shift || true

    case $command in
        clean)
            cmd_clean
            ;;
        validate)
            cmd_validate
            ;;
        build)
            cmd_build
            ;;
        install)
            cmd_install
            ;;
        test)
            cmd_test
            ;;
        version)
            cmd_version "$@"
            ;;
        release)
            cmd_release "$@"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main
main "$@"
