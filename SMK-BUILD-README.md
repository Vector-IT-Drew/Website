# SMK React App Build & Deploy Scripts

This directory contains automated scripts to build and deploy the SMK React app to Railway.

## Scripts Available

### 1. `./build-and-deploy.sh` - Full Build & Deploy
**Use this for production deployments**

This script handles the complete build and deployment process:
- ✅ Builds the React app (`npm run build`)
- ✅ Installs dependencies if needed
- ✅ Adds Flask app changes to git
- ✅ Force-adds React build files (overrides .gitignore)
- ✅ Commits changes with timestamp
- ✅ Pushes to Railway for deployment
- ✅ Shows deployment status

**Usage:**
```bash
cd Website
./build-and-deploy.sh
```

### 2. `./quick-build.sh` - Development Build Only
**Use this for development/testing**

This script only builds the React app without deploying:
- ✅ Builds the React app (`npm run build`)
- ✅ Installs dependencies if needed
- ❌ Does not commit or deploy

**Usage:**
```bash
cd Website
./quick-build.sh
```

## Why These Scripts Are Needed

The SMK React app has a unique deployment challenge:
- React's `.gitignore` ignores the `/build` directory by default
- Railway needs the build files to serve the app
- We need to force-add (`git add -f`) the build files to include them in deployments

## Typical Workflow

### For Development:
1. Make changes to React app in `react-pages/smk/src/`
2. Run `./quick-build.sh` to test locally
3. Test at `http://localhost:5000/smk` (if running Flask locally)

### For Production Deployment:
1. Make changes to React app in `react-pages/smk/src/`
2. Run `./build-and-deploy.sh` to build and deploy
3. Check deployment at `https://vectorny.com/smk`

## Troubleshooting

### Script Permission Issues
If you get permission denied:
```bash
chmod +x build-and-deploy.sh
chmod +x quick-build.sh
```

### Build Failures
- Check that you're in the `Website` directory
- Ensure Node.js and npm are installed
- Check the React app for compilation errors

### Deployment Issues
- Verify git repository is clean before running
- Check Railway dashboard for deployment logs
- Ensure you have push permissions to the repository

## Files Managed by Scripts

The scripts automatically handle these files:
- `react-pages/smk/build/static/js/*` - JavaScript bundles
- `react-pages/smk/build/static/css/*` - CSS bundles  
- `react-pages/smk/build/index.html` - Main HTML file
- `react-pages/smk/build/asset-manifest.json` - Asset manifest
- `react-pages/smk/build/manifest.json` - Web app manifest
- `app.py` - Flask application changes

## Important Notes

⚠️ **Always run scripts from the `Website` directory**
⚠️ **The scripts will commit and push automatically - make sure your changes are ready**
⚠️ **Build files are force-added to git despite .gitignore** 