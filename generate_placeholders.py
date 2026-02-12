import os
from PIL import Image, ImageDraw

def create_gradient(width, height, start_color, end_color):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            mask_data.append(int(255 * (x + y) / (width + height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def generate_assets():
    # Ensure directories exist
    os.makedirs('static/profile_pics', exist_ok=True)
    os.makedirs('static/club_logos', exist_ok=True)

    # 1. User PFP (default.jpg) - Indigo to Purple Gradient
    print("Generating User Placeholder...")
    pfp = create_gradient(500, 500, (99, 102, 241), (168, 85, 247)) # Indigo-500 to Purple-500
    
    # Add a simple initial or symbol
    draw = ImageDraw.Draw(pfp)
    # Since we can't easily rely on fonts being present, we'll draw a simple shape or leave it clean
    # Let's draw a simple "User" silhouette or just leave it as a cool gradient
    # A clean gradient is better than a bad drawing
    
    pfp.save('static/profile_pics/default.jpg', quality=95)
    print("Saved static/profile_pics/default.jpg")

    # 2. Club Logo (default.svg) - Emerald to Teal Gradient
    print("Generating Club Placeholder...")
    svg_content = '''<svg width="500" height="500" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="500" height="500" fill="url(#grad)" />
    <circle cx="250" cy="250" r="150" fill="white" fill-opacity="0.2" />
    <path d="M250 150 L350 350 L150 350 Z" fill="white" fill-opacity="0.8" />
</svg>'''
    
    with open('static/club_logos/default.svg', 'w') as f:
        f.write(svg_content)
    print("Saved static/club_logos/default.svg")

if __name__ == '__main__':
    generate_assets()
