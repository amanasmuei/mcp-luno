---
layout: default
title: GitHub Pages Fix Guide
---

# GitHub Pages Configuration Fix

This guide provides the complete solution to resolve the `actions/configure-pages@v4` error.

## Immediate Fix Required

The workflow error occurs because GitHub Pages is not enabled in your repository settings. Follow these steps:

### 1. Enable GitHub Pages (CRITICAL)

**You must do this manually in GitHub repository settings:**

1. Go to your repository on GitHub: `https://github.com/amanasmuei/mcp-luno`
2. Click the **Settings** tab
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions** (not "Deploy from a branch")
5. Click **Save**

### 2. Verify Repository Permissions

1. In Settings, go to **Actions** > **General**
2. Under **Workflow permissions**:
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**

### 3. Updated Configuration Files

The following files have been updated to fix the issue:

#### `.github/workflows/pages.yml`
- Added `enablement: true` parameter to auto-enable Pages if possible
- Configured proper permissions and artifact handling

#### `docs/Gemfile`
- Switched to `github-pages` gem for better compatibility
- Commented out individual Jekyll gems

#### `docs/_config.yml`
- Fixed baseurl to match repository name: `/mcp-luno`
- Updated URL structure for GitHub Pages

### 4. Deploy the Changes

After enabling Pages in repository settings:

```bash
git add -A
git commit -m "Fix GitHub Pages configuration"
git push origin main
```

### 5. Monitor Deployment

1. Go to **Actions** tab in your repository
2. The workflow should now run successfully
3. Once complete, your site will be available at: `https://amanasmuei.github.io/mcp-luno`

## Common Issues and Solutions

### Error: "Get Pages site failed"
- **Cause**: Pages not enabled in repository settings
- **Solution**: Follow step 1 above - enable Pages with GitHub Actions as source

### Error: "HttpError: Not Found"
- **Cause**: Repository visibility or permissions issue
- **Solution**: Ensure repository is public and workflow has write permissions

### Error: "Permission denied"
- **Cause**: Insufficient workflow permissions
- **Solution**: Follow step 2 above - enable read/write permissions

### Workflow doesn't trigger
- **Cause**: Wrong branch or file path
- **Solution**: Ensure you're pushing to `main` branch and files are in correct paths

## Manual Trigger (If Needed)

If the workflow still doesn't trigger automatically:

1. Go to **Actions** tab
2. Select "Deploy Jekyll site to Pages"
3. Click **Run workflow**
4. Select `main` branch
5. Click **Run workflow**

## Verification Steps

After successful deployment:

1. ✅ Repository Settings > Pages shows "GitHub Actions" as source
2. ✅ Actions tab shows successful workflow runs
3. ✅ Site accessible at `https://amanasmuei.github.io/mcp-luno`
4. ✅ No more "configure-pages" errors

## Important Notes

- **Repository must be public** for free GitHub Pages (or have GitHub Pro/Enterprise)
- **Default branch** should be `main` (workflow is configured for this)
- **File structure** must remain as configured (docs/ directory with Jekyll files)

## Next Steps After Fix

1. Customize the Jekyll theme and content
2. Add custom domain (optional)
3. Set up branch protection rules
4. Monitor site analytics

---

**Need help?** Check the [GitHub Pages documentation](https://docs.github.com/en/pages) or create an issue in the repository.