#!/usr/bin/env python3
"""
Script to wrap Arabic text in Settings.js with t() function
"""
import re

# Read the file
with open('/app/frontend/src/pages/Settings.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Arabic text pattern - matches strings in JSX that contain Arabic
# Pattern 1: Text directly in JSX elements like >النص<
pattern1 = r'>([^<>{}]*[\u0600-\u06FF][^<>{}]*)<'

# Pattern 2: String literals with Arabic
pattern2 = r'"([^"]*[\u0600-\u06FF][^"]*)"'
pattern3 = r"'([^']*[\u0600-\u06FF][^']*)'"

# Replacements done
count = 0

# Pattern for JSX text content (between > and <)
def replace_jsx_text(match):
    global count
    text = match.group(1).strip()
    if not text or text.startswith('{') or 't(' in text:
        return match.group(0)
    count += 1
    return f">{{t('{text}')}}<"

# Pattern for placeholder attributes
def replace_placeholder(match):
    global count
    text = match.group(1)
    count += 1
    return f"placeholder={{t('{text}')}}"

# Pattern for title attributes  
def replace_title(match):
    global count
    text = match.group(1)
    count += 1
    return f"title={{t('{text}')}}"

# Pattern for alt attributes
def replace_alt(match):
    global count
    text = match.group(1)
    count += 1
    return f"alt={{t('{text}')}}"

# Apply replacements
# 1. Replace JSX text content
content = re.sub(r'>([^<>{}]+[\u0600-\u06FF][^<>{}]+)<', replace_jsx_text, content)

# 2. Replace placeholder attributes with Arabic
content = re.sub(r'placeholder="([^"]*[\u0600-\u06FF][^"]*)"', replace_placeholder, content)

# 3. Replace title attributes with Arabic  
content = re.sub(r'title="([^"]*[\u0600-\u06FF][^"]*)"', replace_title, content)

# 4. Replace alt attributes with Arabic
content = re.sub(r'alt="([^"]*[\u0600-\u06FF][^"]*)"', replace_alt, content)

# Write the file back
with open('/app/frontend/src/pages/Settings.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Replaced {count} Arabic text instances with t() wrapper")
