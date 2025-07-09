#!/bin/bash

# Quick Build Script for SMK React App (Development)
# This script only builds the React app without deploying

set -e  # Exit on any error

echo "🔨 Quick building SMK React App..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}[ERROR]${NC} Please run this script from the Website directory"
    exit 1
fi

# Navigate to React app directory and build
echo -e "${BLUE}[INFO]${NC} Building React app..."
cd react-pages/smk

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}[INFO]${NC} Installing dependencies..."
    npm install
fi

# Build the React app
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} ✅ React app built successfully!"
    echo -e "${BLUE}[INFO]${NC} Build files are ready in react-pages/smk/build/"
    echo -e "${BLUE}[INFO]${NC} Run './build-and-deploy.sh' to deploy to Railway"
else
    echo -e "${RED}[ERROR]${NC} React build failed!"
    exit 1
fi 