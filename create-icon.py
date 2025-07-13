#!/usr/bin/env python3

import os
from pathlib import Path

# Create a simple SVG icon for OptiScaler Manager
svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <!-- Background circle -->
  <circle cx="32" cy="32" r="30" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
  
  <!-- Upscaling arrows -->
  <path d="M20 25 L32 15 L44 25 L40 25 L40 35 L24 35 L24 25 Z" fill="#60a5fa" opacity="0.8"/>
  <path d="M20 39 L32 49 L44 39 L40 39 L40 29 L24 29 L24 39 Z" fill="#93c5fd" opacity="0.6"/>
  
  <!-- Center "O" for OptiScaler -->
  <circle cx="32" cy="32" r="8" fill="none" stroke="#ffffff" stroke-width="3"/>
  
  <!-- Small enhancement dots -->
  <circle cx="16" cy="32" r="2" fill="#fbbf24"/>
  <circle cx="48" cy="32" r="2" fill="#fbbf24"/>
  <circle cx="32" cy="16" r="2" fill="#10b981"/>
  <circle cx="32" cy="48" r="2" fill="#10b981"/>
</svg>'''

# Save the icon
icon_path = Path(__file__).parent / "optiscaler-icon.svg"
with open(icon_path, 'w') as f:
    f.write(svg_content)

print(f"Created icon: {icon_path}")

# Also create a PNG version if Pillow is available
try:
    import cairosvg
    png_path = Path(__file__).parent / "optiscaler-icon.png"
    cairosvg.svg2png(url=str(icon_path), write_to=str(png_path), output_width=64, output_height=64)
    print(f"Created PNG icon: {png_path}")
except ImportError:
    print("cairosvg not available, skipping PNG generation")
    print("SVG icon created and will work fine with most desktop environments")