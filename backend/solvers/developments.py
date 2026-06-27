import math

def solve(params: dict) -> dict:
    solid_type = params.get("solid_type", "square_prism")
    side = params.get("side_len", 30)
    axis_len = params.get("length", 65)
    cut_angle = params.get("hp_angle", 30)
    
    if not solid_type:
        solid_type = "square_prism"
        
    is_prism = "prism" in solid_type or "cylinder" in solid_type
    is_pyramid = "pyramid" in solid_type or "cone" in solid_type
    
    shape = "square"
    if "triangle" in solid_type or "triangular" in solid_type:
        shape = "triangle"
    elif "pentagon" in solid_type or "pentagonal" in solid_type:
        shape = "pentagon"
    elif "hexagon" in solid_type or "hexagonal" in solid_type:
        shape = "hexagon"
    elif "cylinder" in solid_type or "cone" in solid_type:
        shape = "circle"

    scale = 1.5
    svg_elements = ""
    
    dev_x = 60
    dev_y = 120
    
    # 3D Base Radius
    if shape == "circle":
        r_base = side / 2
    elif shape == "triangle":
        r_base = side / math.sqrt(3)
    elif shape == "square":
        r_base = side / math.sqrt(2)
    elif shape == "hexagon":
        r_base = side
    else:  # pentagon
        r_base = side / 1.175

    # Cutting plane setup (AIP inclined at cut_angle to HP, passing through axis center)
    beta_rad = math.radians(cut_angle)
    B_normal = math.sin(beta_rad)
    C_normal = math.cos(beta_rad)
    h_cut = axis_len / 2.0
    D_const = - B_normal * h_cut

    if is_prism:
        # Parallel Line Development
        if shape == "circle":
            num_sides = 12
            segment_w = (math.pi * side) / 12
            labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "A"]
        else:
            if shape == "triangle":
                num_sides = 3
            elif shape == "square":
                num_sides = 4
            elif shape == "hexagon":
                num_sides = 6
            else:  # pentagon
                num_sides = 5
            segment_w = side
            labels = [chr(65 + i) for i in range(num_sides)] + ["A"]
            
        total_w = num_sides * segment_w
        
        # Base rectangle of development
        svg_elements += f'<rect data-step="2" x="{dev_x}" y="{dev_y}" width="{int(total_w * scale)}" height="{int(axis_len * scale)}" fill="none" stroke="blue" stroke-width="2.5" />'
        
        # Draw vertical lines for segments
        for i in range(num_sides + 1):
            x_pos = dev_x + i * segment_w * scale
            svg_elements += f'<line data-step="2" x1="{int(x_pos)}" y1="{dev_y}" x2="{int(x_pos)}" y2="{int(dev_y + axis_len*scale)}" stroke="blue" stroke-width="1.2" stroke-dasharray="2" />'
            svg_elements += f'<text data-step="2" x="{int(x_pos) - 4}" y="{dev_y - 8}" font-family="Arial" font-size="11" fill="blue" font-weight="bold">{labels[i]}</text>'
            svg_elements += f'<text data-step="2" x="{int(x_pos) - 4}" y="{int(dev_y + axis_len*scale) + 16}" font-family="Arial" font-size="11" fill="blue" font-weight="bold">{labels[i].lower()}</text>'

        # Draw cut curve (Parallel line development cut shape using true 3D intersection heights)
        cut_pts = []
        for i in range(num_sides + 1):
            # Calculate base point Z depth
            if shape == "circle":
                ang = i * (2 * math.pi / 12)
            else:
                ang = math.pi / num_sides + i * (2 * math.pi / num_sides)
            zi = r_base * math.sin(ang)
            
            # Intersection with B*y + C*z + D = 0 on vertical edge
            # B*h_i + C*z_i + D = 0 => h_i = -(C*z_i + D)/B
            if abs(B_normal) > 1e-4:
                h_i = -(C_normal * zi + D_const) / B_normal
            else:
                h_i = h_cut
                
            cut_h = max(5.0, min(axis_len - 5.0, h_i))
            cx = dev_x + i * segment_w * scale
            cy = dev_y + (axis_len - cut_h) * scale
            cut_pts.append((cx, cy))
            
        poly_points = " ".join([f"{int(p[0])},{int(p[1])}" for p in cut_pts])
        svg_elements += f'<path data-step="3" d="M {poly_points}" fill="none" stroke="red" stroke-width="3" />'
        svg_elements += f'<polygon data-step="4" points="{poly_points} {int(dev_x + total_w*scale)},{int(dev_y + axis_len*scale)} {dev_x},{int(dev_y + axis_len*scale)}" fill="rgba(231, 76, 60, 0.15)" stroke="none" />'
        
    else:
        # Radial Line Development
        if shape == "circle":
            r_base = side / 2
            labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "A"]
            num_sides = 12
        else:
            if shape == "triangle":
                num_sides = 3
            elif shape == "square":
                num_sides = 4
            elif shape == "hexagon":
                num_sides = 6
            else:  # pentagon
                num_sides = 5
            labels = [chr(65 + i) for i in range(num_sides)] + ["A"]
            
        # Radial unrolling: L = sqrt(R^2 + H^2)
        slant_height = math.hypot(r_base, axis_len)
        sector_angle = (r_base / slant_height) * 360.0
        
        scx = dev_x + 180 * scale
        scy = dev_y
        sector_rad = slant_height * scale * 1.1
        
        # Sector center apex
        svg_elements += f'<circle data-step="2" cx="{int(scx)}" cy="{int(scy)}" r="4" fill="blue" />'
        svg_elements += f'<text data-step="2" x="{int(scx) - 15}" y="{int(scy) - 5}" font-family="Arial" font-size="12" fill="blue" font-weight="bold">O</text>'
        
        start_ang = 90 - sector_angle/2
        
        pts_arc = []
        for i in range(num_sides + 1):
            ang = start_ang + i * (sector_angle / num_sides)
            ang_rad = math.radians(ang)
            px = scx + sector_rad * math.cos(ang_rad)
            py = scy + sector_rad * math.sin(ang_rad)
            pts_arc.append((px, py))
            
            # Radial generators
            svg_elements += f'<line data-step="2" x1="{int(scx)}" y1="{int(scy)}" x2="{int(px)}" y2="{int(py)}" stroke="blue" stroke-width="1.2" stroke-dasharray="2" />'
            svg_elements += f'<text data-step="2" x="{int(px) + (5 if px >= scx else -12)}" y="{int(py) + 12}" font-family="Arial" font-size="11" fill="blue" font-weight="bold">{labels[i]}</text>'

        # Draw base boundary
        if shape == "circle":
            svg_elements += f'<path data-step="2" d="M {int(pts_arc[0][0])} {int(pts_arc[0][1])} A {int(sector_rad)} {int(sector_rad)} 0 0 1 {int(pts_arc[-1][0])} {int(pts_arc[-1][1])}" fill="none" stroke="blue" stroke-width="2.5" />'
        else:
            svg_elements += f'<polygon data-step="2" points="{" ".join([f"{int(p[0])},{int(p[1])}" for p in pts_arc])} {int(scx)},{int(scy)}" fill="none" stroke="blue" stroke-width="2.5" />'

        # Radial Development Cut Shape using exact 3D slant edge intersections
        cut_pts = []
        for i in range(num_sides + 1):
            ang_deg = start_ang + i * (sector_angle / num_sides)
            
            # Find base vertex Z depth
            if shape == "circle":
                shape_ang = i * (2 * math.pi / 12)
            else:
                shape_ang = math.pi / num_sides + i * (2 * math.pi / num_sides)
            zi = r_base * math.sin(shape_ang)
            
            # Slant edge intersection parameter t
            # V1=(R*cos, 0, R*sin), V2=(0, H, 0)
            # t = -(C*zi + D) / (B*H - C*zi)
            denom = B_normal * axis_len - C_normal * zi
            if abs(denom) > 1e-4:
                t = -(C_normal * zi + D_const) / denom
            else:
                t = 0.5
            t = max(0.05, min(0.95, t))
            
            # Radial distance from apex O: d = (1 - t) * L
            ratio = 1.0 - t
            cut_r = sector_rad * ratio
            
            ang_rad = math.radians(ang_deg)
            px = scx + cut_r * math.cos(ang_rad)
            py = scy + cut_r * math.sin(ang_rad)
            cut_pts.append((px, py))
            svg_elements += f'<circle data-step="3" cx="{int(px)}" cy="{int(py)}" r="3" fill="red" />'

        poly_points = " ".join([f"{int(p[0])},{int(p[1])}" for p in cut_pts])
        if shape == "circle":
            svg_elements += f'<path data-step="3" d="M {poly_points}" fill="none" stroke="red" stroke-width="3" />'
        else:
            svg_elements += f'<path data-step="3" d="M {poly_points}" fill="none" stroke="red" stroke-width="3" />'

    case_title = f"Development of Lateral Surface of {solid_type.replace('_',' ').capitalize()}"
    
    steps = [
        f"STAGE 1: Draw the simple Front and Top Views of the solid (base side/diameter {side}mm, height {axis_len}mm) using a thin 2H pencil and make the final outlines dark with an HB pencil.",
        "STAGE 2: " + (f"Calculate the perimeter of the base: P = {num_sides} × {side} = {int(total_w)}mm. Draw a thin horizontal stretch-out line of length {int(total_w)}mm using a 2H pencil, and divide it into {num_sides} equal parts of width {side}mm. Erect vertical generator lines of height {axis_len}mm at each division using a thin 2H pencil." if is_prism else f"Calculate the True Slant Height L = √({r_base:.1f}² + {axis_len}²) = {int(slant_height)}mm. Calculate the development sector angle θ_dev = ({r_base:.1f} / {slant_height:.1f}) × 360° = {int(sector_angle)}°. Draw a radial generator line of length {int(slant_height)}mm, and draw an arc of radius L subtending the angle {int(sector_angle)}° using a thin 2H pencil. Divide the arc into {num_sides} equal parts and draw radial generator lines using a 2H pencil."),
        f"STAGE 3: Draw the cutting plane line in the Front View inclined at {cut_angle}° using a section line (thin chain-dotted 2H line in the middle, thick HB lines at the ends). Mark the points where the cutting plane cuts the various generators of the solid.",
        "STAGE 4: Transfer the heights of the cut points from the Front View horizontally (for prisms/cylinders) or radially (for pyramids/cones) onto the corresponding generator lines in the development layout using a thin 2H pencil.",
        "STAGE 5: Join the cut points in the development layout using a dark HB pencil with " + ("straight lines (since the solid has flat faces)." if is_prism else "a smooth, continuous curve (since the solid is a cylinder/cone)."),
        "STAGE 6: Complete the boundary of the developed lateral surface by drawing the top and bottom base outlines with a dark HB pencil. Add dimensions and labels using a medium H pencil."
    ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 430" width="100%" height="400" style="background-color: #ffffff; border: 1px solid #cccccc;">
        {svg_elements}
    </svg>
    """

    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Solid = {solid_type.replace('_',' ').capitalize()}<br>Base Side = {side}mm | Height = {axis_len}mm<br>Method = " + ("Parallel Line Development" if is_prism else "Radial Line Development"),
        "found_values": ("Unrolled Perimeter = " + f"{int(total_w)}mm" if is_prism else f"True Slant Height L = {int(slant_height)}mm<br>Subtended Angle θ = {int(sector_angle)}°")
    }
