# Post-Release Documentation & Security Improvements

This PR includes post-release documentation for v2.0.0 and critical security improvements to our GitHub Actions workflows.

## 📝 Post-Release Documentation

### Added Files:
- **`RELEASE_ANNOUNCEMENT.md`** - Public announcement for v2.0.0 release
- **`social_media_announcement.txt`** - Templates for social media posts
- **`POST_RELEASE_CHECKLIST.md`** - Checklist for post-release tasks

These documents help ensure a smooth release process and effective communication about the new version.

## 🔒 Security Improvements

### GitHub Actions SHA Pinning
All GitHub Actions have been pinned to specific commit SHAs instead of mutable version tags. This prevents supply chain attacks where a compromised action could be injected via tag manipulation.

**Updated Workflows:**
- `.github/workflows/ci.yml` - 10 actions pinned
- `.github/workflows/release.yml` - 3 actions pinned  
- `.github/workflows/docs.yml` - 5 actions pinned
- `.github/workflows/docker-deploy.yml` - 6 actions pinned

**Example:**
```yaml
# Before (vulnerable):
- uses: actions/checkout@v3

# After (secure):
- uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744 # v3.6.0
```

### Additional Security Enhancements:
- **`SECURITY.md`** - Security policy documenting our practices
- **`scripts/get-action-hashes.sh`** - Helper script to find action commit hashes
- **Updated `.github/dependabot.yml`** - Now monitors GitHub Actions for updates

## ✅ Checklist
- [x] All GitHub Actions pinned to SHA hashes
- [x] Security policy documented
- [x] Post-release documentation created
- [x] Dependabot configured for automated updates
- [x] Helper scripts added

## 🚀 Impact
These changes improve the security posture of our CI/CD pipeline and provide clear documentation for future releases.

Closes #N/A