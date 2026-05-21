with open('templates/base.html.fixed', 'r') as f:
    content = f.readlines()

# Find the start and end of the navbar section
nav_start = 0
nav_end = 0
for i, line in enumerate(content):
    if '<ul class="navbar-nav me-auto">' in line:
        nav_start = i
    if nav_start > 0 and '</ul>' in line and '<ul class="navbar-nav ms-auto">' not in content[i+1]:
        nav_end = i
        break

# Build new navbar without HOME and CONTACT
new_navbar = []
skip_next_lines = 0
for i in range(nav_start, nav_end + 1):
    line = content[i]
    
    # Skip the HOME nav item (3 lines)
    if 'href="{{ url_for(\'index\') }}">HOME' in line:
        skip_next_lines = 2  # Skip the current line, </li>, and the next </li>
        continue
    
    # Skip the CONTACT nav item (3 lines)
    if 'href="{{ url_for(\'contact\') }}">CONTACT' in line:
        skip_next_lines = 2  # Skip the current line, </li>, and the next </li>
        continue
    
    if skip_next_lines > 0:
        skip_next_lines -= 1
        continue
        
    new_navbar.append(line)

# Replace the navbar section in the content
modified_content = content[:nav_start] + new_navbar + content[nav_end + 1:]

# Write the modified content back to the file
with open('templates/base.html', 'w') as f:
    f.writelines(modified_content)
