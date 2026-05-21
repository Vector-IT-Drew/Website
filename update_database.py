#!/usr/bin/env python3
"""
Script to update the database.py file with improved pet policy handling
"""

# Read the file
with open('database.py', 'r') as file:
    lines = file.readlines()

# Find the lines to update
for i in range(len(lines)):
    if '"pets_policy":' in lines[i] and 'Pets Allowed' in lines[i+1]:
        # Found a match, replace the three lines
        lines[i+1] = '                    process_pet_friendly(item.get(\'pet_friendly\'), item.get(\'unit_id\')),\n'
        lines[i+2] = ''  # Clear the third line if it exists

# Write the file back
with open('database.py', 'w') as file:
    file.writelines(lines)

print("Successfully updated database.py")