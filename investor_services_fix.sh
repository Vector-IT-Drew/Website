#!/bin/bash

# Create a temporary file
cp templates/investor_services.html templates/investor_services.html.bak

# First, fix the issue at line 471
sed -i '470d' templates/investor_services.html

# Check for any other issues
grep -n -A 2 -B 2 "scroll-down-indicator" templates/investor_services.html
