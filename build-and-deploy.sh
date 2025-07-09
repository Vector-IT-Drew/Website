#!/bin/bash

# SMK React App Build and Deploy Script
# This script handles the complete build and deployment process

set -e  # Exit on any error

echo "🚀 Starting SMK React App Build and Deploy Process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    print_error "Please run this script from the Website directory"
    exit 1
fi

# Step 1: Navigate to React app directory and build
print_status "Step 1: Building React app..."
cd react-pages/smk

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

# Build the React app
print_status "Building React app..."
npm run build

if [ $? -ne 0 ]; then
    print_error "React build failed!"
    exit 1
fi

print_success "React app built successfully!"

# Step 2: Go back to Website directory
cd ../../

# Step 3: Check git status
print_status "Step 2: Checking git status..."
git status

# Step 4: Add Flask app changes
print_status "Step 3: Adding Flask app changes..."
git add app.py

# Step 5: Force add React build files (override .gitignore)
print_status "Step 4: Adding React build files..."
git add -f react-pages/smk/build/static/js/
git add -f react-pages/smk/build/static/css/
git add -f react-pages/smk/build/index.html
git add -f react-pages/smk/build/asset-manifest.json
git add -f react-pages/smk/build/manifest.json

# Step 6: Check if there are any changes to commit
if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    # Step 7: Commit changes
    print_status "Step 5: Committing changes..."
    
    # Get current timestamp for commit message
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    COMMIT_MSG="Deploy SMK React app - Build and update static files ($TIMESTAMP)"
    
    git commit -m "$COMMIT_MSG"
    print_success "Changes committed successfully!"
    
    # Step 8: Push to Railway
    print_status "Step 6: Pushing to Railway..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        print_success "Successfully pushed to Railway!"
        print_success "🎉 Deployment complete! Your app should be live shortly."
        print_status "Check deployment status at: https://railway.app"
    else
        print_error "Failed to push to Railway"
        exit 1
    fi
fi

# Step 9: Show final status
print_status "Final git status:"
git status

echo ""
print_success "✅ Build and deploy process completed successfully!"
print_status "Your SMK React app has been deployed to Railway"
print_status "Visit: https://vectorny.com/smk"
echo "" 