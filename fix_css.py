
path = 'static/css/style.css'

old_css = """.club-category {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent-primary-light);
    background: rgba(99,102,241,0.1);
    border-radius: var(--radius-full);
    margin-bottom: 0.75rem;
}"""

new_css = """.club-category {
    display: inline-block;
    padding: 0.35em 0.8em;
    background: rgba(99, 102, 241, 0.1);
    color: var(--accent-primary-light);
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(99, 102, 241, 0.2);
}"""

# Read as binary to avoid encoding errors during read
with open(path, 'rb') as f:
    content = f.read()

# Normalize line endings for search
content_str = content.decode('utf-8', errors='ignore')
old_css_normalized = old_css.replace('\r\n', '\n').strip()

# We need to be careful about whitespace. 
# The Get-Content output might have different whitespace than the file.
# Let's try to match by structure or use a regex if strict match fails.
# But for now, let's try strict match but robust to whitespace.

import re

# Construct regex from old_css, escaping special chars and allowing variable whitespace
regex_pattern = re.escape(old_css).replace(r'\ ', r'\s*').replace(r'\r\n', r'\s*').replace(r'\n', r'\s*')
# Actually, re.escape escapes space too.
# Let's do it manually.
parts = [re.escape(x.strip()) for x in old_css.split()]
pattern = r'\s*'.join(parts)

# Simple replacement if exact match works (it might not due to crlf)
# Let's try to find the start of the block and end of the block in the file string.
# ".club-category {" is unique enough?
start_marker = ".club-category {"
end_marker = "}"

# Find start
idx = content_str.find(start_marker)
if idx != -1:
    # Find the matching closing brace
    # Simple search for next } might be enough if no nested braces (CSS rules usually don't have nested braces inside properties)
    end_idx = content_str.find("}", idx)
    if end_idx != -1:
        # Check if the content inside matches roughly what we expect or just replace it blind?
        # Blind replacement of the block is risky if we match the wrong thing.
        # But ".club-category" selector is unique.
        
        original_block = content_str[idx:end_idx+1]
        print(f"Found block:\n{original_block}")
        
        # Replace
        new_content_str = content_str[:idx] + new_css + content_str[end_idx+1:]
        
        with open(path, 'wb') as f:
            f.write(new_content_str.encode('utf-8'))
        print("Replaced successfully.")
    else:
        print("Could not find closing brace.")
else:
    print("Could not find .club-category start.")
