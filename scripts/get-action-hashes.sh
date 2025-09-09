#!/bin/bash
# Script to get commit hashes for GitHub Actions

echo "Getting commit hashes for GitHub Actions..."
echo ""

# Function to get commit hash for a specific action and tag
get_commit_hash() {
    local repo=$1
    local tag=$2
    
    echo "Fetching commit hash for $repo@$tag..."
    
    # Use GitHub API to get the commit hash
    commit_hash=$(curl -s "https://api.github.com/repos/$repo/git/refs/tags/$tag" | grep '"sha"' | head -1 | cut -d'"' -f4)
    
    if [ -z "$commit_hash" ]; then
        echo "  ERROR: Could not find commit hash for $repo@$tag"
    else
        echo "  - uses: $repo@$commit_hash # $tag"
    fi
    echo ""
}

# Common actions we use
echo "=== Common GitHub Actions ==="
get_commit_hash "actions/checkout" "v3.6.0"
get_commit_hash "actions/checkout" "v4.1.1"
get_commit_hash "actions/cache" "v3.3.3"
get_commit_hash "actions/cache" "v4.0.0"
get_commit_hash "actions/upload-artifact" "v3.1.3"
get_commit_hash "actions/upload-artifact" "v4.3.0"
get_commit_hash "actions/setup-python" "v4.8.0"
get_commit_hash "actions/setup-python" "v5.0.0"

echo "=== Docker Actions ==="
get_commit_hash "docker/setup-buildx-action" "v3.0.0"
get_commit_hash "docker/setup-qemu-action" "v3.0.0"
get_commit_hash "docker/login-action" "v3.0.0"
get_commit_hash "docker/build-push-action" "v5.1.0"
get_commit_hash "docker/metadata-action" "v5.5.0"

echo "=== Other Actions ==="
get_commit_hash "codecov/codecov-action" "v3.1.4"
get_commit_hash "codecov/codecov-action" "v4.0.1"
get_commit_hash "github/codeql-action" "v2.22.12"
get_commit_hash "github/codeql-action" "v3.23.0"
get_commit_hash "peaceiris/actions-gh-pages" "v3.9.3"
get_commit_hash "peaceiris/actions-gh-pages" "v4.0.0"

echo "Note: Replace version tags with commit hashes in your workflow files for better security."