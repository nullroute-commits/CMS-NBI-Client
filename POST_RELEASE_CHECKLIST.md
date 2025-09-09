# Post-Release Checklist for v2.0.0

## Immediate Tasks (Within 1 hour)

- [ ] Verify GitHub Release was created automatically
- [ ] Check PyPI package upload: https://pypi.org/project/cmsnbiclient/
- [ ] Verify Docker images on Docker Hub: https://hub.docker.com/r/nullroute-commits/cms-nbi-client
- [ ] Confirm GitHub Pages documentation deployed
- [ ] Test pip install: `pip install cmsnbiclient==2.0.0`
- [ ] Test Docker pull: `docker pull ghcr.io/nullroute-commits/cms-nbi-client:2.0.0`

## Communication (Within 24 hours)

- [ ] Post release announcement on project wiki/discussions
- [ ] Share on relevant social media channels
- [ ] Update any internal documentation
- [ ] Notify key stakeholders/users about the release

## Monitoring (First week)

- [ ] Monitor GitHub Issues for any v2.0.0-specific problems
- [ ] Check PyPI download statistics
- [ ] Review Docker Hub pull counts
- [ ] Collect user feedback

## Follow-up Tasks

- [ ] Plan v2.1.0 features based on user feedback
- [ ] Update roadmap documentation
- [ ] Consider writing a blog post about the modernization journey
- [ ] Schedule team retrospective on the release process

## Emergency Procedures

If critical issues are found:

1. **Hotfix Process**:
   ```bash
   git checkout -b hotfix/v2.0.1 v2.0.0
   # Make fixes
   git tag -a v2.0.1 -m "Hotfix: [description]"
   git push origin v2.0.1
   ```

2. **PyPI Yanking** (if necessary):
   ```bash
   pip install twine
   twine yank cmsnbiclient==2.0.0
   ```

3. **Docker Image Removal**:
   - Remove from Docker Hub via web interface
   - Update latest tag to previous stable version

## Success Metrics

Track these metrics over the next 30 days:

- PyPI downloads
- Docker pulls
- GitHub stars/forks
- Issue resolution time
- User feedback sentiment
- Documentation page views

---

Remember: A successful release isn't just about pushing code—it's about ensuring users can adopt and benefit from the improvements!