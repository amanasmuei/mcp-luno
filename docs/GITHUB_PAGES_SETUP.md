---
layout: default
title: GitHub Pages Setup Guide
---

# GitHub Pages Setup Guide

This guide will help you resolve the `actions/configure-pages@v4` error and properly configure GitHub Pages for your repository.

## Prerequisites

Before starting, ensure you have:
- Admin access to your GitHub repository
- The repository is public (or you have GitHub Pro/Enterprise for private repos)

## Step-by-Step Configuration

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Scroll down to **Pages** section in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### 2. Configure Repository Settings

Ensure your repository has the correct settings:

- **Repository name**: Should match the URL in `_config.yml` (currently set to `luno-mcp`)
- **Visibility**: Public (required for free GitHub Pages)
- **Actions permissions**: Enabled in Settings > Actions > General

### 3. Verify Workflow Permissions

1. Go to **Settings** > **Actions** > **General**
2. Under **Workflow permissions**, select:
   - "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**

### 4. Push Changes

After creating the workflow file (`.github/workflows/pages.yml`), commit and push:

```bash
git add .github/workflows/pages.yml docs/Gemfile docs/index.md
git commit -m "Add GitHub Pages workflow and Jekyll setup"
git push origin main
```

### 5. Monitor Deployment

1. Go to **Actions** tab in your repository
2. You should see the "Deploy Jekyll site to Pages" workflow running
3. Once complete, your site will be available at: `https://amanasmuei.github.io/luno-mcp`

## Troubleshooting

### Common Issues

**Error**: "Get Pages site failed"
- **Solution**: Ensure GitHub Pages is enabled with "GitHub Actions" as source

**Error**: "HttpError: Not Found"
- **Solution**: Verify repository is public and Pages is enabled

**Error**: "Permission denied"
- **Solution**: Check workflow permissions in repository settings

**Error**: "Jekyll build failed"
- **Solution**: Verify `Gemfile` and `_config.yml` syntax

### Workflow Not Triggering

If the workflow doesn't trigger automatically:

1. Check the workflow file is in `.github/workflows/pages.yml`
2. Ensure you're pushing to the main/master branch
3. Verify the workflow has proper permissions
4. Try triggering manually from Actions tab

### Branch Configuration

The workflow is configured to trigger on pushes to:
- `main` branch
- `master` branch

If your default branch has a different name, update the workflow file:

```yaml
on:
  push:
    branches: ["your-branch-name"]
```

## Manual Trigger

You can manually trigger the deployment:

1. Go to **Actions** tab
2. Select "Deploy Jekyll site to Pages"
3. Click **Run workflow**
4. Select your branch and click **Run workflow**

## Verification

Once deployed successfully:

1. Your site should be accessible at the configured URL
2. Check the **Pages** section in repository settings for the live URL
3. The **Actions** tab should show successful workflow runs

## Next Steps

After successful deployment:

- Customize the Jekyll theme and content
- Add custom domain (optional)
- Set up automated updates
- Monitor site analytics

---

For additional help, consult the [GitHub Pages documentation](https://docs.github.com/en/pages) or open an issue in the repository.