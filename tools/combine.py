#!/usr/bin/env python3
"""Join the briefing poster (left) and the issue poster (right) into one wide image.
Usage: python3 tools/combine.py left.png right.png out.png
Build both inputs with "page": "" in their json so no "1/2 Page" labels appear."""
import sys
from PIL import Image, ImageDraw
a = Image.open(sys.argv[1]).convert("RGB"); b = Image.open(sys.argv[2]).convert("RGB")
im = Image.new("RGB", (a.width + b.width, max(a.height, b.height)), "#0b0f1a")
im.paste(a, (0, 0)); im.paste(b, (a.width, 0))
ImageDraw.Draw(im).line([(a.width, 56), (a.width, im.height - 56)], fill="#232c44", width=2)
im.save(sys.argv[3]); print(im.size)
