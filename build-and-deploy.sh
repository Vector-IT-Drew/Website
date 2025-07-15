#!/bin/bash

# SMK React App Build and Git Add Script
# This script handles building and staging files for commit (you handle commit/push)

set -e  # Exit on any error

echo "🚀 Starting SMK React App Build and Git Add Process..."

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

# Check if critical build files exist
if [ ! -f "react-pages/smk/build/index.html" ]; then
    print_error "index.html not found in build directory!"
    print_error "React build may have failed. Please check the build output above."
    exit 1
fi

if [ ! -d "react-pages/smk/build/static/js" ]; then
    print_error "JavaScript files not found in build directory!"
    print_error "React build may have failed. Please check the build output above."
    exit 1
fi

print_status "Adding ALL build files (including new JS files with hashes)..."
# Use git add . to catch all new files in the build directory
cd react-pages/smk/build
git add -f .
cd ../../../

# Add React source code changes
print_status "Adding React source code changes..."
git add react-pages/smk/src/

print_success "All build files added to git successfully!"

# Step 6: Show what's been staged
print_status "Step 5: Showing what's been added to git..."
git status

echo ""
print_success "✅ Build and git add process completed successfully!"
print_status "Files are now staged and ready for commit"
print_status "To commit and push, run:"
print_status "  git commit -m \"Deploy SMK React app - Build and update static files\""
print_status "  git push origin main"
echo "" 
echo "" 
