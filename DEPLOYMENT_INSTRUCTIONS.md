# GitHub Pages Deployment Instructions

## Automatic Deployment Setup

This project is configured for automatic deployment to GitHub Pages at:
**https://arvind-55555.github.io/S.I.E.M**

## Prerequisites

1. GitHub account with repository access
2. Repository: `S.I.E.M` or `Arvind-55555/S.I.E.M`
3. Git installed locally

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# Navigate to project directory
cd /home/arvind/Downloads/projects/Working/S.I.E.M

# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/Arvind-55555/S.I.E.M.git

# Add all files
git add .

# Commit changes
git commit -m "Production release v2.0: ML integration, 50+ rules, real-time data collection"

# Push to GitHub
git push -u origin main
```

**Note:** If the default branch is `master` instead of `main`, use:
```bash
git push -u origin master
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/Arvind-55555/S.I.E.M
2. Click **Settings** (gear icon)
3. Scroll down to **Pages** section in the left sidebar
4. Under **Build and deployment**:
   - **Source**: Select "GitHub Actions"
   - This will use the workflow file `.github/workflows/deploy.yml`

### 3. Verify Deployment

1. Go to **Actions** tab in your repository
2. You should see "Deploy to GitHub Pages" workflow running
3. Wait for the green checkmark (usually 1-2 minutes)
4. Click on the workflow to see deployment details

### 4. Access Your Site

Once deployed, your site will be available at:
**https://arvind-55555.github.io/S.I.E.M**

The site includes:
- Feature showcase
- System architecture
- ML and detection capabilities
- Installation instructions
- Performance metrics
- Links to documentation

## Workflow Details

The deployment workflow (`.github/workflows/deploy.yml`) automatically:

1. Triggers on push to `main` or `master` branch
2. Checks out the code
3. Configures GitHub Pages
4. Uploads the `docs/` folder as an artifact
5. Deploys to GitHub Pages

## Manual Workflow Trigger

You can also manually trigger deployment:

1. Go to **Actions** tab
2. Select "Deploy to GitHub Pages"
3. Click **Run workflow** button
4. Select branch (main/master)
5. Click **Run workflow**

## Updating the Site

To update the deployed site:

1. Edit `docs/index.html` with your changes
2. Commit and push:
```bash
git add docs/index.html
git commit -m "Updated documentation"
git push origin main
```
3. GitHub Actions will automatically redeploy within 2 minutes

## Troubleshooting

### Deployment Not Starting

**Issue:** No workflow visible in Actions tab

**Solution:**
1. Ensure `.github/workflows/deploy.yml` exists
2. Check file is committed: `git ls-files .github/`
3. Verify branch name matches workflow trigger (main vs master)

### Deployment Failed

**Issue:** Red X on workflow

**Solution:**
1. Click on failed workflow
2. Review error logs
3. Common issues:
   - Pages not enabled in Settings
   - Permissions not set correctly
   - Invalid YAML syntax

### 404 Error on Site

**Issue:** Site shows 404 Not Found

**Solution:**
1. Wait 2-3 minutes after deployment
2. Clear browser cache
3. Verify `docs/index.html` exists in repository
4. Check Pages settings: Source should be "GitHub Actions"

### Wrong URL

**Issue:** Site URL is different

**Solution:**
- GitHub Pages URL format: `https://USERNAME.github.io/REPOSITORY`
- For `Arvind-55555/S.I.E.M`: https://arvind-55555.github.io/S.I.E.M
- For custom domain, configure in Settings → Pages → Custom domain

## Custom Domain Setup (Optional)

To use a custom domain like `siem.example.com`:

1. Add `CNAME` file in `docs/` folder:
```bash
echo "siem.example.com" > docs/CNAME
git add docs/CNAME
git commit -m "Add custom domain"
git push
```

2. Configure DNS records:
   - Type: `CNAME`
   - Name: `siem` (or `@` for apex domain)
   - Value: `arvind-55555.github.io`

3. Enable HTTPS in Settings → Pages

## Workflow Permissions

Ensure the workflow has proper permissions:

1. Go to Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click **Save**

## Monitoring Deployments

Track deployment status:

```bash
# Using GitHub CLI (if installed)
gh workflow view "Deploy to GitHub Pages"
gh run list --workflow=deploy.yml

# View latest deployment
gh run view --log
```

## Security Notes

- The deployment workflow uses official GitHub Actions
- No secrets required for basic deployment
- `docs/index.html` is a static site (no server-side code)
- All dependencies loaded from CDNs (Bootstrap, Chart.js)

## Support

If deployment issues persist:

1. Check GitHub Status: https://www.githubstatus.com/
2. Review documentation: https://docs.github.com/pages
3. Open issue: https://github.com/Arvind-55555/S.I.E.M/issues

---

**Last Updated:** December 12, 2025
**Version:** 2.0 (Production Release)
