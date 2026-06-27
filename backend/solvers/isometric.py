import math
from solvers import utils

def solve(params: dict) -> dict:
    solid_type = params.get("solid_type", "square_prism")
    side = params.get("side_len", 40)
    axis_len = params.get("length", 60)
    
    question = params.get("raw_question", "")
    q_lower = question.lower()
    
    is_projection = "projection" in q_lower
    # Foreshortening factor of 0.816 for Isometric Projection, 1.0 for Isometric View
    foreshortening = is_projection
    
    scale = 1.6
    cx = 250
    cy = 320 # bottom center of canvas placement
    
    shape = "square"
    if "triangle" in solid_type or "triangular" in solid_type:
        shape = "triangle"
    elif "pentagon" in solid_type or "pentagonal" in solid_type:
        shape = "pentagon"
    elif "hexagon" in solid_type or "hexagonal" in solid_type:
        shape = "hexagon"
    elif "cylinder" in solid_type or "cone" in solid_type:
        shape = "circle"
        
    is_prism = "prism" in solid_type or "cylinder" in solid_type or "cube" in q_lower
    is_pyramid = "pyramid" in solid_type or "cone" in solid_type
    
    if "cube" in q_lower:
        side = 40
        axis_len = 40
        shape = "square"
        
    # Generate bottom base vertices in 3D centered on XZ plane (Y = 0)
    base_3d = []
    if shape == "square":
        half = side / 2
        base_3d = [
            (-half, 0.0, -half),
            (half, 0.0, -half),
            (half, 0.0, half),
            (-half, 0.0, half)
        ]
    elif shape == "triangle":
        h = side * math.sqrt(3) / 2
        base_3d = [
            (-side/2, 0.0, -h/3),
            (side/2, 0.0, -h/3),
            (0.0, 0.0, 2*h/3)
        ]
    elif shape == "circle":
        r = side / 2
        for i in range(12):
            ang = i * (2 * math.pi / 12)
            base_3d.append((r * math.cos(ang), 0.0, r * math.sin(ang)))
    else: # hexagon
        r = side
        for i in range(6):
            ang = i * (2 * math.pi / 6)
            base_3d.append((r * math.cos(ang), 0.0, r * math.sin(ang)))

    num_pts = len(base_3d)

    # 1. Transform bottom base using Syllabus Isometric Projection Matrix
    bottom_screen = [utils.project_isometric(v, cx, cy, scale, foreshortening) for v in base_3d]
    
    # 2. Transform top base (prism) or apex (pyramid)
    top_screen = []
    if is_prism:
        top_screen = [utils.project_isometric((v[0], axis_len, v[2]), cx, cy, scale, foreshortening) for v in base_3d]
    else:
        apex_screen = utils.project_isometric((0.0, axis_len, 0.0), cx, cy, scale, foreshortening)

    # SVG rendering
    svg_elements = ""
    
    # Draw reference ground line and 30-degree axes lines
    axis_end_r = utils.project_isometric((120, 0, 0), cx, cy, scale, foreshortening)
    axis_end_l = utils.project_isometric((0, 0, 120), cx, cy, scale, foreshortening)
    
    svg_elements += f'<line data-step="1" x1="{cx}" y1="{cy}" x2="{int(axis_end_r[0])}" y2="{int(axis_end_r[1])}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2,2" />'
    svg_elements += f'<line data-step="1" x1="{cx}" y1="{cy}" x2="{int(axis_end_l[0])}" y2="{int(axis_end_l[1])}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2,2" />'
    
    svg_elements += f'<text data-step="1" x="{cx + 50}" y="{cy - 12}" font-family="Arial" font-size="10" fill="#64748b">30°</text>'
    svg_elements += f'<text data-step="1" x="{cx - 75}" y="{cy - 12}" font-family="Arial" font-size="10" fill="#64748b">30°</text>'
    svg_elements += f'<line data-step="1" x1="{cx - 150}" y1="{cy}" x2="{cx + 150}" y2="{cy}" stroke="black" stroke-width="1" />'

    # Draw base edges
    if shape == "circle":
        svg_elements += f'<polygon data-step="2" points="{" ".join([f"{int(p[0])},{int(p[1])}" for p in bottom_screen])}" fill="none" stroke="blue" stroke-width="1.2" stroke-dasharray="2,2" />'
    else:
        for i in range(num_pts):
            next_idx = (i + 1) % num_pts
            # Hidden base lines detection (back facing edges in XZ plane)
            p1 = base_3d[i]
            p2 = base_3d[next_idx]
            is_hidden = (p1[2] < 0 and p2[2] < 0) or (p1[0] < 0 and p2[0] < 0 and p1[2] <= 0)
            stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2.5"'
            svg_elements += f'<line data-step="2" x1="{int(bottom_screen[i][0])}" y1="{int(bottom_screen[i][1])}" x2="{int(bottom_screen[next_idx][0])}" y2="{int(bottom_screen[next_idx][1])}" stroke="blue"{stroke_dash} />'

    # Draw top edges or apex slant lines
    if is_prism:
        svg_elements += f'<polygon data-step="3" points="{" ".join([f"{int(p[0])},{int(p[1])}" for p in top_screen])}" fill="none" stroke="blue" stroke-width="2.5" />'
        
        # Connect vertical edges
        for i in range(num_pts):
            p = base_3d[i]
            is_hidden = (p[0] < 0 and p[2] < 0)
            stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2.5"'
            svg_elements += f'<line data-step="4" x1="{int(bottom_screen[i][0])}" y1="{int(bottom_screen[i][1])}" x2="{int(top_screen[i][0])}" y2="{int(top_screen[i][1])}" stroke="blue"{stroke_dash} />'
            
    elif is_pyramid:
        svg_elements += f'<circle data-step="3" cx="{int(apex_screen[0])}" cy="{int(apex_screen[1])}" r="3" fill="blue" />'
        svg_elements += f'<text data-step="3" x="{int(apex_screen[0]) - 5}" y="{int(apex_screen[1]) - 8}" font-family="Arial" font-size="12" fill="blue" font-weight="bold">O</text>'
        
        # Slant edges
        for i in range(num_pts):
            p = base_3d[i]
            is_hidden = (p[0] < 0 and p[2] < 0)
            stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2.5"'
            svg_elements += f'<line data-step="4" x1="{int(bottom_screen[i][0])}" y1="{int(bottom_screen[i][1])}" x2="{int(apex_screen[0])}" y2="{int(apex_screen[1])}" stroke="blue"{stroke_dash} />'

    case_title = "Isometric " + ("Projection" if is_projection else "View") + f" of {solid_type.replace('_',' ').capitalize()}"
    
    steps = [
        "Draw a horizontal reference line and mark a starting point on it using a thin 2H pencil.",
        "From the starting point, draw three isometric axes: two lines inclined at 30° to the horizontal on both sides, and one vertical axis line pointing upwards, using a thin 2H pencil.",
        "Set up the drawing scale: " + (f"Construct an Isometric Scale on the side by projecting true length measurements (side = {side}mm, height = {axis_len}mm) onto the 30° isometric line to find the foreshortened measurements: side = {int(side * 0.816)}mm, height = {int(axis_len * 0.816)}mm (isometric scale factor 0.816)." if is_projection else f"Use True Scale (1.0 factor). Measure the actual dimensions directly: base side = {side}mm, axis height = {axis_len}mm."),
        f"Construct the isometric view of the base {shape} on the horizontal isometric plane (aligned along the two 30° axes) using a thin 2H pencil.",
        "Erect the vertical heights: " + (f"From each base corner, draw vertical lines of height {int(axis_len * 0.816 if is_projection else axis_len)}mm parallel to the vertical isometric axis using a thin 2H pencil to locate the top corners." if is_prism else f"Locate the base center. Erect a vertical centerline of height {int(axis_len * 0.816 if is_projection else axis_len)}mm using a thin chain-dotted line to find the apex point O."),
        "Connect all corners to complete the solid structure. Outline all visible edges and boundaries with a dark HB pencil (thickness 2.5px) to make the drawing stand out.",
        "Draw any necessary hidden lines as thin dashed lines (1.2px) using a medium H pencil only if required for internal details (in general, hidden lines are omitted in isometric drawings unless critical).",
        "Add dimensions and labels using a medium H pencil."
    ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400" width="100%" height="380" style="background-color: #ffffff; border: 1px solid #cccccc;">
        {svg_elements}
    </svg>
    """

    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Solid = {solid_type.replace('_',' ').capitalize()}<br>Base Side = {side}mm | Axis = {axis_len}mm<br>Method = " + ("Isometric Projection (Scale 0.816)" if is_projection else "Isometric View (Scale 1.0)"),
        "found_values": "Syllabus Isometric Matrix applied.<br>X-axis: 30° rightward<br>Z-axis: 30° leftward<br>Y-axis: 90° vertical"
    }
