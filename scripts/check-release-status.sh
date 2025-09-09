#!/bin/bash
# Script to check v2.0.0 release status

echo "🔍 Checking CMS-NBI-Client v2.0.0 Release Status..."
echo "================================================="
echo ""

# Check Git tags
echo "📌 Git Tags:"
if git tag | grep -q "v2.0.0"; then
    echo "✅ v2.0.0 tag exists locally"
else
    echo "❌ v2.0.0 tag not found locally"
fi

# Check remote tags
if git ls-remote --tags origin | grep -q "v2.0.0"; then
    echo "✅ v2.0.0 tag exists on remote"
else
    echo "❌ v2.0.0 tag not found on remote"
fi
echo ""

# Check branches
echo "🌿 Branch Status:"
echo "Main branch: $(git rev-parse --short main)"
echo "Dev branch: $(git rev-parse --short dev)"
if [ "$(git rev-parse main)" = "$(git rev-parse dev)" ]; then
    echo "✅ Dev is synced with main"
else
    echo "⚠️  Dev is not synced with main"
fi
echo ""

# Check for pending changes
echo "📝 Working Directory:"
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Working directory is clean"
else
    echo "⚠️  Uncommitted changes exist"
    git status --short
fi
echo ""

# List recent releases
echo "📦 Recent Tags:"
git tag -l "v*" | sort -V | tail -5
echo ""

# Check workflow files
echo "🔒 Security Status:"
if grep -q "@[a-f0-9]\{40\}" .github/workflows/*.yml; then
    echo "✅ GitHub Actions are SHA-pinned"
else
    echo "❌ GitHub Actions are not SHA-pinned"
fi
echo ""

# External services (informational only)
echo "🌐 External Services to Check:"
echo "- GitHub Release: https://github.com/nullroute-commits/CMS-NBI-Client/releases/tag/v2.0.0"
echo "- GitHub Actions: https://github.com/nullroute-commits/CMS-NBI-Client/actions"
echo "- PyPI Package: https://pypi.org/project/cmsnbiclient/2.0.0/"
echo "- Docker Hub: https://hub.docker.com/r/nullroute-commits/cms-nbi-client/tags"
echo "- Documentation: https://nullroute-commits.github.io/CMS-NBI-Client/"
echo ""

echo "✨ Release status check complete!"