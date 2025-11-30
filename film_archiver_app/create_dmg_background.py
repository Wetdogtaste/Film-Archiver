#!/usr/bin/env python3
"""
Create a DMG background image with drag-to-Applications visual instruction.
Maintains cohesive macOS visual design.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_dmg_background(output_path, width=660, height=400):
    """Create a professional DMG background image with drag-to-Applications instruction."""
    
    # Create base image with a gradient-like macOS style background
    # Using a sophisticated gray that matches macOS Finder aesthetic
    img = Image.new('RGB', (width, height), color='#F6F6F6')
    draw = ImageDraw.Draw(img)
    
    # Add a subtle gradient effect (lighter at top, slightly darker at bottom)
    for y in range(height):
        # Calculate gradient shade
        lightness = int(246 - (y / height) * 10)
        color = (lightness, lightness, lightness)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Icon positions (matching the DMG layout)
    # App icon will be on the left, Applications folder on the right
    app_x = 165  # Left position for app
    apps_x = 495  # Right position for Applications folder
    icon_y = 180  # Vertical center for icons
    
    # Draw a stylish arrow pointing from app to Applications
    arrow_y = icon_y
    arrow_start_x = app_x + 60  # Start after app icon
    arrow_end_x = apps_x - 60   # End before Applications icon
    arrow_color = '#007AFF'  # macOS blue
    
    # Draw arrow body (thicker line)
    for offset in range(-3, 4):
        draw.line([(arrow_start_x, arrow_y + offset), (arrow_end_x - 20, arrow_y + offset)], 
                  fill=arrow_color, width=1)
    
    # Draw arrow head
    arrow_points = [
        (arrow_end_x - 20, arrow_y - 15),  # Top
        (arrow_end_x, arrow_y),             # Point
        (arrow_end_x - 20, arrow_y + 15),   # Bottom
    ]
    draw.polygon(arrow_points, fill=arrow_color)
    
    # Try to use system font, fall back to default if not available
    try:
        # Try SF Pro Display (macOS system font)
        title_font = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 18)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 13)
    except:
        try:
            # Try Helvetica Neue
            title_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 18)
            subtitle_font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 13)
        except:
            # Use default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    
    # Draw labels under icon positions
    text_color = '#333333'
    
    # "Film Archiver" label (under app position)
    app_text = "Film Archiver"
    app_bbox = draw.textbbox((0, 0), app_text, font=title_font)
    app_text_width = app_bbox[2] - app_bbox[0]
    draw.text((app_x - app_text_width // 2, icon_y + 70), app_text, fill=text_color, font=title_font)
    
    # "Applications" label (under Applications folder position)
    apps_text = "Applications"
    apps_bbox = draw.textbbox((0, 0), apps_text, font=title_font)
    apps_text_width = apps_bbox[2] - apps_bbox[0]
    draw.text((apps_x - apps_text_width // 2, icon_y + 70), apps_text, fill=text_color, font=title_font)
    
    # Instruction text at bottom
    instruction = "Drag Film Archiver to Applications to install"
    instr_bbox = draw.textbbox((0, 0), instruction, font=subtitle_font)
    instr_width = instr_bbox[2] - instr_bbox[0]
    draw.text((width // 2 - instr_width // 2, height - 50), instruction, 
              fill='#666666', font=subtitle_font)
    
    # Draw icon placeholder circles with subtle shadows (optional visual guide)
    # These help indicate where the icons will appear
    circle_radius = 45
    
    # App icon circle (subtle dotted outline)
    for angle in range(0, 360, 15):
        import math
        x = app_x + circle_radius * math.cos(math.radians(angle))
        y = icon_y + circle_radius * math.sin(math.radians(angle))
        draw.ellipse([(x-1, y-1), (x+1, y+1)], fill='#CCCCCC')
    
    # Applications folder circle (subtle dotted outline)
    for angle in range(0, 360, 15):
        import math
        x = apps_x + circle_radius * math.cos(math.radians(angle))
        y = icon_y + circle_radius * math.sin(math.radians(angle))
        draw.ellipse([(x-1, y-1), (x+1, y+1)], fill='#CCCCCC')
    
    # Save the image
    img.save(output_path, 'PNG', quality=95)
    print(f"DMG background created: {output_path}")

if __name__ == "__main__":
    # Create the background image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'dmg_background.png')
    create_dmg_background(output_path)
