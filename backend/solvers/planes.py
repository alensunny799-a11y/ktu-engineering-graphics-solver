import math
from solvers.utils import rotate_point

def solve(params: dict) -> dict:
    shape = params.get("shape", "pentagon")
    side = params.get("side_len", 30)
    theta = params.get("hp_angle", 45) # Surface inclination to HP
    phi = params.get("vp_angle", 30)   # Resting edge inclination to VP
    
    # Scale factor
    scale = 1.6
    xy_y = 200
    
    # Define base vertices (True Shape in Top View)
    # Origin is centered in y-dir, x is at some offset (e.g. 100)
    cx1 = 110
    cy1 = xy_y + 70
    
    pts1 = []
    labels = []
    pts1_outline = []
    
    if shape == "triangle":
        # Equilateral triangle resting on vertical edge on the left
        h = side * math.sqrt(3) / 2
        pts1 = [
            (cx1, cy1 - side/2 * scale),
            (cx1, cy1 + side/2 * scale),
            (cx1 + h * scale, cy1)
        ]
        labels = ["a", "b", "c"]
    elif shape == "square":
        # Square resting on vertical edge on the left
        pts1 = [
            (cx1, cy1 - side/2 * scale),
            (cx1, cy1 + side/2 * scale),
            (cx1 + side * scale, cy1 + side/2 * scale),
            (cx1 + side * scale, cy1 - side/2 * scale)
        ]
        labels = ["a", "b", "c", "d"]
    elif shape == "rectangle":
        # Rectangle resting on shorter vertical edge on the left
        w = side
        h = side * 0.6
        pts1 = [
            (cx1, cy1 - h/2 * scale),
            (cx1, cy1 + h/2 * scale),
            (cx1 + w * scale, cy1 + h/2 * scale),
            (cx1 + w * scale, cy1 - h/2 * scale)
        ]
        labels = ["a", "b", "c", "d"]
    elif shape == "hexagon":
        # Hexagon resting on vertical edge on the left
        r = side
        h_hex = side * math.sqrt(3) / 2
        pts1 = [
            (cx1, cy1 - side/2 * scale),
            (cx1, cy1 + side/2 * scale),
            (cx1 + h_hex * scale, cy1 + side * scale),
            (cx1 + 2 * h_hex * scale, cy1 + side/2 * scale),
            (cx1 + 2 * h_hex * scale, cy1 - side/2 * scale),
            (cx1 + h_hex * scale, cy1 - side * scale)
        ]
        labels = ["a", "b", "c", "d", "e", "f"]
    elif shape == "circle":
        # Circle divided into 8 points for construction
        r = side / 2
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            pts1.append((cx1 + r * math.cos(angle) * scale, cy1 + r * math.sin(angle) * scale))
        labels = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        
        # High resolution outline (36 points) for smooth ellipse drawing
        for i in range(36):
            angle = i * (2 * math.pi / 36)
            pts1_outline.append((cx1 + r * math.cos(angle) * scale, cy1 + r * math.sin(angle) * scale))
    else: # Default: pentagon
        # Pentagon resting on vertical edge on the left
        r_geom = side / (2 * math.sin(math.pi / 5)) 
        p1_angles = [math.pi - (i * 2 * math.pi / 5) for i in range(5)]
        pts1 = [(cx1 + r_geom * math.cos(a) * scale, cy1 + r_geom * math.sin(a) * scale) for a in p1_angles]
        # Align so edge AB is vertical on the left
        dy = (pts1[1][1] - pts1[0][1]) / 2
        min_x = min(p[0] for p in pts1)
        dx = cx1 - min_x
        pts1 = [(p[0] + dx, p[1]) for p in pts1]
        labels = ["a", "b", "c", "d", "e"]

    num_pts = len(pts1)

    # STAGE 1 FRONT VIEW: Points lie on the XY line
    pts1_prime = [(p[0], xy_y) for p in pts1]

    # STAGE 2 FRONT VIEW (Tilted at theta to HP)
    min_x = min(p[0] for p in pts1)
    max_x = max(p[0] for p in pts1)
    span = max_x - min_x
    
    s2_start_x = 280
    theta_rad = math.radians(theta)
    
    pts2_prime = []
    for p in pts1:
        rel_x = p[0] - min_x
        px = s2_start_x + rel_x * math.cos(theta_rad)
        py = xy_y - rel_x * math.sin(theta_rad)
        pts2_prime.append((px, py))

    # STAGE 2 TOP VIEW (Compressed Top View)
    pts2 = [(pts2_prime[i][0], pts1[i][1]) for i in range(num_pts)]

    # STAGE 3 TOP VIEW (Rotated by phi to VP)
    cx2 = sum(p[0] for p in pts2) / num_pts
    cy2 = sum(p[1] for p in pts2) / num_pts
    
    cx3 = cx2 + 220
    cy3 = cy1
    
    pts3 = []
    for p in pts2:
        rx, ry = rotate_point(p[0], p[1], cx2, cy2, phi)
        pts3.append((rx + (cx3 - cx2), ry + (cy3 - cy2)))

    # STAGE 3 FRONT VIEW (Final Projections)
    pts3_prime = []
    for i in range(num_pts):
        pts3_prime.append((pts3[i][0], pts2_prime[i][1]))

    # --- CIRCLE OUTLINE PROJECTIONS SETUP ---
    pts2_outline_prime = []
    pts2_outline = []
    pts3_outline = []
    pts3_outline_prime = []
    
    if shape == "circle":
        # Stage 2 FV and TV
        for p in pts1_outline:
            rel_x = p[0] - min_x
            px = s2_start_x + rel_x * math.cos(theta_rad)
            py = xy_y - rel_x * math.sin(theta_rad)
            pts2_outline_prime.append((px, py))
        pts2_outline = [(pts2_outline_prime[i][0], pts1_outline[i][1]) for i in range(36)]
        
        # Stage 3 TV and FV
        for p in pts2_outline:
            rx, ry = rotate_point(p[0], p[1], cx2, cy2, phi)
            pts3_outline.append((rx + (cx3 - cx2), ry + (cy3 - cy2)))
        for i in range(36):
            pts3_outline_prime.append((pts3_outline[i][0], pts2_outline_prime[i][1]))

    # Generate labels tags and coordinates for SVG
    def format_points(pts):
        return " ".join([f"{int(p[0])},{int(p[1])}" for p in pts])

    # Build the SVG representation
    shape_elements = ""
    
    # 1. Base shape polygon
    if shape == "circle":
        shape_elements += f'<polygon data-step="2" points="{format_points(pts1_outline)}" fill="none" stroke="blue" stroke-width="2" />'
        for i in range(8):
            shape_elements += f'<circle data-step="2" cx="{int(pts1[i][0])}" cy="{int(pts1[i][1])}" r="3" fill="blue" />'
            # Draw diameters generators
            next_opp = (i + 4) % 8
            svg_elements_line = f'<line data-step="2" x1="{int(pts1[i][0])}" y1="{int(pts1[i][1])}" x2="{int(pts1[next_opp][0])}" y2="{int(pts1[next_opp][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
            shape_elements += svg_elements_line
    else:
        shape_elements += f'<polygon data-step="2" points="{format_points(pts1)}" fill="none" stroke="blue" stroke-width="2" />'

    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<text data-step="2" x="{int(pts1[i][0]) + (5 if pts1[i][0]>=cx1 else -12)}" y="{int(pts1[i][1]) + 5}" font-family="Arial" font-size="11" fill="blue">{lbl}</text>'
        shape_elements += f'<line data-step="2" x1="{int(pts1[i][0])}" y1="{int(pts1[i][1])}" x2="{int(pts1[i][0])}" y2="{xy_y}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    # 2. Stage 1 Front View (resting on XY)
    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<circle data-step="2" cx="{int(pts1_prime[i][0])}" cy="{xy_y}" r="3" fill="red" />'
        shape_elements += f'<text data-step="2" x="{int(pts1_prime[i][0]) - 5}" y="{xy_y - 8}" font-family="Arial" font-size="11" fill="red" font-weight="bold">{lbl}\'</text>'

    # 3. Stage 2 Front View (Tilted line)
    idx_min = 0
    idx_max = 0
    min_val = 9999
    max_val = -9999
    for i, p in enumerate(pts1):
        if p[0] < min_val:
            min_val = p[0]
            idx_min = i
        if p[0] > max_val:
            max_val = p[0]
            idx_max = i
            
    shape_elements += f'<line data-step="3" x1="{int(pts2_prime[idx_min][0])}" y1="{int(pts2_prime[idx_min][1])}" x2="{int(pts2_prime[idx_max][0])}" y2="{int(pts2_prime[idx_max][1])}" stroke="red" stroke-width="3" />'
    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<circle data-step="3" cx="{int(pts2_prime[i][0])}" cy="{int(pts2_prime[i][1])}" r="3" fill="black" />'
        shape_elements += f'<text data-step="3" x="{int(pts2_prime[i][0]) - 10}" y="{int(pts2_prime[i][1]) - 8}" font-family="Arial" font-size="11" fill="red">{lbl}\'</text>'
        shape_elements += f'<line data-step="4" x1="{int(pts2_prime[i][0])}" y1="{int(pts2_prime[i][1])}" x2="{int(pts2_prime[i][0])}" y2="{int(pts2[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    shape_elements += f'<text data-step="3" x="{int(pts2_prime[idx_min][0]) + 40}" y="{xy_y - 10}" font-family="Arial" font-size="11" fill="red" font-style="italic">θ={theta}°</text>'

    # 4. Stage 2 Top View (Compressed shape)
    if shape == "circle":
        shape_elements += f'<polygon data-step="4" points="{format_points(pts2_outline)}" fill="none" stroke="blue" stroke-width="2" />'
        for i in range(num_pts):
            shape_elements += f'<circle data-step="4" cx="{int(pts2[i][0])}" cy="{int(pts2[i][1])}" r="3" fill="blue" />'
    else:
        shape_elements += f'<polygon data-step="4" points="{format_points(pts2)}" fill="none" stroke="blue" stroke-width="2" />'
        
    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<text data-step="4" x="{int(pts2[i][0]) + 6}" y="{int(pts2[i][1]) + 4}" font-family="Arial" font-size="11" fill="blue">{lbl}</text>'

    # 5. Stage 3 Top View (Rotated shape)
    if shape == "circle":
        shape_elements += f'<polygon data-step="5" points="{format_points(pts3_outline)}" fill="none" stroke="blue" stroke-width="2" />'
        for i in range(num_pts):
            shape_elements += f'<circle data-step="5" cx="{int(pts3[i][0])}" cy="{int(pts3[i][1])}" r="3" fill="blue" />'
    else:
        shape_elements += f'<polygon data-step="5" points="{format_points(pts3)}" fill="none" stroke="blue" stroke-width="2" />'
        
    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<text data-step="5" x="{int(pts3[i][0]) + 6}" y="{int(pts3[i][1]) + 4}" font-family="Arial" font-size="11" fill="blue">{lbl}</text>'
        shape_elements += f'<line data-step="6" x1="{int(pts3[i][0])}" y1="{int(pts3[i][1])}" x2="{int(pts3[i][0])}" y2="{int(pts3_prime[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
        shape_elements += f'<line data-step="6" x1="{int(pts2_prime[i][0])}" y1="{int(pts2_prime[i][1])}" x2="{int(pts3_prime[i][0])}" y2="{int(pts3_prime[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    shape_elements += f'<text data-step="5" x="{int(cx3) + 20}" y="{int(cy3) - 40}" font-family="Arial" font-size="11" fill="purple" font-style="italic">φ={phi}°</text>'

    # 6. Stage 3 Front View (Final Shape)
    if shape == "circle":
        shape_elements += f'<polygon data-step="6" points="{format_points(pts3_outline_prime)}" fill="none" stroke="red" stroke-width="2.5" />'
    else:
        shape_elements += f'<polygon data-step="6" points="{format_points(pts3_prime)}" fill="none" stroke="red" stroke-width="3" />'
        
    for i in range(num_pts):
        lbl = labels[i]
        shape_elements += f'<circle data-step="6" cx="{int(pts3_prime[i][0])}" cy="{int(pts3_prime[i][1])}" r="3.5" fill="black" />'
        shape_elements += f'<text data-step="6" x="{int(pts3_prime[i][0]) - 5}" y="{int(pts3_prime[i][1]) - 8}" font-family="Arial" font-size="11" fill="red" font-weight="bold">{lbl}\'</text>'

    case_title = f"Projection of {shape.capitalize()} Plane ({side}mm Dimension)"
    
    steps = [
        "Draw the reference line XY using a thin 2H pencil. Label the endpoints as X and Y using a medium H pencil.",
        f"STAGE 1: Draw the true shape of the {shape} (side/diameter {side}mm) in the Top View (below the XY line) using a dark HB pencil, such that one edge is perpendicular to XY (resting edge). Project all its corners vertically up to the XY line using a thin 2H pencil to get the initial Front View as a line lying on the XY line. Mark the Front View points as a', b', c'... using a dark HB pencil.",
        f"STAGE 2: Draw a locus line inclined at the surface inclination angle θ = {theta}° to the XY line from the resting point using a thin 2H pencil. Measure the initial Front View length and mark it on this tilted line using a dark HB pencil.",
        f"Drop thin vertical projector lines downwards from the tilted Front View points and draw horizontal projector lines from the Stage 1 Top View points using a thin 2H pencil. Mark the intersection points (a, b, c...) and join them using a dark HB pencil to obtain the compressed/apparent Top View.",
        f"STAGE 3: Redraw the compressed Top View (Stage 2) in the right-hand side using a dark HB pencil, keeping its resting edge inclined at the angle φ = {phi}° to the VP (XY line). Use a thin 2H pencil for any construction lines.",
        "Draw thin vertical projector lines upwards from all corners of the rotated Top View (Stage 3) and draw horizontal projector lines across from the tilted Front View (Stage 2) using a thin 2H pencil. Mark the intersection points (a', b', c'...) and connect them with a dark HB pencil to get the final Front View of the inclined lamina.",
        "Draw thin dimension lines and write labels/values using a medium H pencil."
    ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 430" width="100%" height="400" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <!-- Reference Line XY -->
        <line data-step="1" x1="20" y1="{xy_y}" x2="660" y2="{xy_y}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="10" y="{xy_y + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="665" y="{xy_y + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        {shape_elements}
    </svg>
    """

    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Shape = {shape.capitalize()}<br>Side/Diameter = {side}mm<br>Inclination to HP (θ) = {theta}°<br>Inclination to VP (φ) = {phi}°",
        "found_values": f"Stage 1: True Shape in TV, Front View on XY<br>Stage 2: Surface tilted to HP (Apparent TV generated)<br>Stage 3: Completed Final Projections"
    }
