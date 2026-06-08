# core/engines/sticker.py
from PIL import Image, ImageDraw, ImageFont

def draw_marketplace_box_sticker(draw, font, x_anchor, y_anchor, text, bg_color, border_color, uniform_width=None):
    """
    Renders a strict square marketplace promo badge featuring a clear 'box-inside-a-box' 
    structural wireframe. The interior gaps are left unfilled, and text is centered.
    """
    text_lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not text_lines:
        return 0, 0  # Returns (height_consumed, width_consumed)

    max_line_w = 0
    total_text_h = 0
    line_metrics = []
    
    # Calculate text layout bounding shapes
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        max_line_w = max(max_line_w, line_w)
        line_metrics.append((line_w, line_h))
        total_text_h += line_h + 4

    # Core marketplace layout structural padding parameters
    padding = 14
    inner_gap = 6  # The clear hollow gap between outer shell and inner frame
    
    if uniform_width is not None:
        # Enforce identical width scaling across the cascade block pipeline
        box_side = uniform_width
    else:
        # Core geometry logic: force content height and width into a strict mathematical square
        content_size = max(max_line_w, total_text_h)
        box_side = content_size + (padding * 2) + (inner_gap * 2)

    # Calculate outer boundary square coordinates anchored on the top-right
    x2 = x_anchor
    x1 = x_anchor - box_side
    y1 = y_anchor
    y2 = y_anchor + box_side
    
    # 1. Draw Outer Structural Box Shell
    draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color, width=2)
    
    # 2. Draw Inner Hollow Framing Wirebox (No fill, just outline creating the gap look)
    ix1 = x1 + inner_gap
    iy1 = y1 + inner_gap
    ix2 = x2 - inner_gap
    iy2 = y2 - inner_gap
    draw.rectangle([ix1, iy1, ix2, iy2], fill=None, outline=border_color, width=2)
    
    # 3. Render Perfectly Centered Multiline Typography
    inner_box_h = iy2 - iy1
    start_y = iy1 + (inner_box_h - total_text_h) // 2
    
    current_y = start_y
    for i, line in enumerate(text_lines):
        line_w, line_h = line_metrics[i]
        # Calculate localized center X anchor offset
        text_x = ix1 + ((ix2 - ix1) - line_w) // 2
        
        draw.text((text_x, current_y), line, fill="white", font=font)
        current_y += line_h + 4
        
    return box_side, box_side

def apply_promo_sticker(canvas, stickers_list, font_style="arial.ttf"):
    """
    Composites a uniform vertical stack of strict square e-commerce promo badges
    with consistent bounding widths down the top-right catalog frame boundaries.
    """
    if not stickers_list:
        return canvas
        
    canvas_w, canvas_h = canvas.size
    draw = ImageDraw.Draw(canvas)
    
    # Text sizing scaled to production frame resolution
    font_size = max(13, int(canvas_h * 0.028))
    try:
        font = ImageFont.truetype(font_style, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    margin_top = 30
    margin_right = 30
    spacing = 15
    
    # PASS 1: Pre-calculate text strings to find the largest side required for uniform width alignment
    max_uniform_side = 0
    for sticker_data in stickers_list[:3]:
        text_lines = [line.strip() for line in sticker_data["text"].split("\n") if line.strip()]
        if not text_lines: continue
        
        max_line_w = 0
        total_text_h = 0
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            max_line_w = max(max_line_w, bbox[2] - bbox[0])
            total_text_h += (bbox[3] - bbox[1]) + 4
            
        badge_square_side = max(max_line_w, total_text_h) + 40  # Unified padding threshold constant
        max_uniform_side = max(max_uniform_side, badge_square_side)
        
    # PASS 2: Render each sticker as a uniform square stack block
    current_y_anchor = margin_top
    x_anchor_right = canvas_w - margin_right
    
    for sticker_data in stickers_list[:3]:
        h_consumed, _ = draw_marketplace_box_sticker(
            draw=draw,
            font=font,
            x_anchor=x_anchor_right,
            y_anchor=current_y_anchor,
            text=sticker_data["text"],
            bg_color=sticker_data.get("bg_color", "#000000"),
            border_color=sticker_data.get("border_color", "#ffffff"),
            uniform_width=max_uniform_side
        )
        if h_consumed > 0:
            current_y_anchor += h_consumed + spacing
            
    return canvas