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

# Step 3: Copy static files from main Vector directory
print_status "Step 2: Copying static files from main Vector directory..."
VECTOR_ROOT="/Users/drewwood/Desktop/Vector"

# Copy CSS files
if [ -f "$VECTOR_ROOT/css/custom.css" ]; then
    cp "$VECTOR_ROOT/css/custom.css" static/css/
    print_success "Copied custom.css"
else
    print_warning "custom.css not found in $VECTOR_ROOT/css/"
fi

if [ -f "$VECTOR_ROOT/css/vector_assistant.css" ]; then
    cp "$VECTOR_ROOT/css/vector_assistant.css" static/css/
    print_success "Copied vector_assistant.css"
else
    print_warning "vector_assistant.css not found in $VECTOR_ROOT/css/"
fi

# Copy JS files
if [ -f "$VECTOR_ROOT/js/main.js" ]; then
    cp "$VECTOR_ROOT/js/main.js" static/js/
    print_success "Copied main.js"
else
    print_warning "main.js not found in $VECTOR_ROOT/js/"
fi

if [ -f "$VECTOR_ROOT/js/vector_assistant.js" ]; then
    cp "$VECTOR_ROOT/js/vector_assistant.js" static/js/
    print_success "Copied vector_assistant.js"
else
    print_warning "vector_assistant.js not found in $VECTOR_ROOT/js/"
fi

# Step 4: Copy React build static files to Website static directory
print_status "Step 3: Copying React build static files to Website static directory..."

# Copy React build CSS files
if [ -d "react-pages/smk/build/static/css" ]; then
    cp react-pages/smk/build/static/css/* static/css/
    print_success "Copied React build CSS files"
else
    print_warning "React build CSS directory not found"
fi

# Copy React build JS files
if [ -d "react-pages/smk/build/static/js" ]; then
    cp react-pages/smk/build/static/js/* static/js/
    print_success "Copied React build JS files"
else
    print_warning "React build JS directory not found"
fi

# Copy React build media files (only if they exist)
if [ -d "react-pages/smk/build/static/media" ]; then
    mkdir -p static/media
    cp react-pages/smk/build/static/media/* static/media/
    print_success "Copied React build media files"
else
    print_status "No media files to copy (this is normal)"
fi

# Step 5: Check git status
print_status "Step 4: Checking git status..."
git status

# Step 6: Add Flask app changes
print_status "Step 5: Adding Flask app changes..."
git add app.py database.py

# Step 7: Force add React build files (override .gitignore)
print_status "Step 6: Adding React build files..."

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
# Use git add -f to force add build files
cd react-pages/smk/build
git add -f .
cd ../../../

# Add React source code changes
print_status "Adding React source code changes..."
git add react-pages/smk/src/

# Add static files (only add directories that exist)
print_status "Adding static files..."
if [ -d "static/css" ]; then
    git add static/css/
fi
if [ -d "static/js" ]; then
    git add static/js/
fi
if [ -d "static/media" ]; then
    git add static/media/
fi

# Add build script
git add build-and-deploy.sh

print_success "All build files added to git successfully!"

# Step 8: Show what's been staged
print_status "Step 7: Showing what's been added to git..."
git status

echo ""
print_success "✅ Build and git add process completed successfully!"
print_status "Files are now staged and ready for commit"
print_status "To commit and push, run:"
print_status "  git commit -m \"Deploy SMK React app - Build and update static files\""
print_status "  git push origin main"
echo "" 
