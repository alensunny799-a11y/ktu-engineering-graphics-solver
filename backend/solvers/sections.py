import re
import math
from solvers import utils

def solve(params: dict) -> dict:
    solid_type = params.get("solid_type", "square_pyramid")
    side = params.get("side_len", 35)
    axis_len = params.get("length", 65)
    cut_angle = params.get("hp_angle", 45) # cut plane inclination to HP
    cut_height = 30 # default height of cutting point on axis from base
    
    question = params.get("raw_question", "")
    q_lower = question.lower()
    height_matches = [int(n) for n in re_find_all_numbers_near_axis(q_lower)]
    if height_matches:
        cut_height = height_matches[0]
        
    scale = 1.6
    y_ref = 190
    cx_fv = 150
    cy_tv = y_ref + 80
    
    # 1. Base points (Top View) & 3D Vertices
    # Generate 3D coordinates for a square pyramid
    # Base: Y = 0. Apex: Y = axis_len
    # R base circumradius = side / sqrt(2)
    r_base = side / math.sqrt(2)
    base_3d = []
    for i in range(4):
        angle = math.pi/4 + i * (2 * math.pi / 4)
        base_3d.append((r_base * math.cos(angle), 0.0, r_base * math.sin(angle)))
    apex_3d = (0.0, axis_len, 0.0)

    # 2. Section Plane normal and plane constant D calculation (Module 3.1)
    beta_rad = math.radians(cut_angle)
    # Normals: A=0, B=sin(beta), C=cos(beta)
    B_normal = math.sin(beta_rad)
    C_normal = math.cos(beta_rad)
    
    # Passes through the axis at height 'cut_height'
    # P_axis = (0, cut_height, 0)
    # B * y_axis + C * z_axis + D = 0 => D = - B * cut_height
    D_const = - B_normal * cut_height
    
    # 3. Edge intersection loop
    # Edges are: Base edges (0-1, 1-2, 2-3, 3-0) and Slant edges (0-apex, 1-apex, 2-apex, 3-apex)
    slant_edges = [
        (base_3d[0], apex_3d),
        (base_3d[1], apex_3d),
        (base_3d[2], apex_3d),
        (base_3d[3], apex_3d)
    ]
    
    intersection_pts_3d = []
    
    # We solve for intersection on slant edges using the syllabus equation:
    # t = -(B*V1y + C*V1z + D) / (B*(V2y - V1y) + C*(V2z - V1z))
    for V1, V2 in slant_edges:
        denom = B_normal * (V2[1] - V1[1]) + C_normal * (V2[2] - V1[2])
        if abs(denom) > 1e-6:
            t = -(B_normal * V1[1] + C_normal * V1[2] + D_const) / denom
            if 0.0 <= t <= 1.0:
                # P_intersection = V1 + t*(V2 - V1)
                px = V1[0] + t * (V2[0] - V1[0])
                py = V1[1] + t * (V2[1] - V1[1])
                pz = V1[2] + t * (V2[2] - V1[2])
                intersection_pts_3d.append((px, py, pz))

    # Project Stage 1 FV and TV (Module 4.1)
    fv_base = [utils.project_orthographic(v, cx_fv, y_ref, scale)[0] for v in base_3d]
    tv_base = [utils.project_orthographic(v, cx_fv, y_ref, scale)[1] for v in base_3d]
    fv_apex, tv_apex = utils.project_orthographic(apex_3d, cx_fv, y_ref, scale)
    
    # Project intersection points
    fv_cuts = []
    tv_cuts = []
    for v in intersection_pts_3d:
        fv_c, tv_c = utils.project_orthographic(v, cx_fv, y_ref, scale)
        fv_cuts.append(fv_c)
        tv_cuts.append(tv_c)

    # 4. True Shape of the Section
    # Auxiliary plane X1Y1 parallel to cutting plane
    aux_x0 = 420
    aux_y0 = 120
    
    # True Shape calculations
    # Transferred widths come from Z coordinates: width = z * scale
    # Lengths along cutting plane are mapped from X coordinate projections
    ts_pts = []
    for i, v in enumerate(intersection_pts_3d):
        # Local offset along cutting plane based on X projection:
        # Distance = x_coord * cos(beta) + y_coord * sin(beta)
        lx = v[0] * math.cos(beta_rad) + v[1] * math.sin(beta_rad)
        ly = v[2] # Z coordinate represents the actual width perpendicular to VP
        
        # Transform local coordinates to auxiliary coordinate system rotated by cut_angle
        rx = lx * math.cos(beta_rad) - ly * math.sin(beta_rad)
        ry = lx * math.sin(beta_rad) + ly * math.cos(beta_rad)
        ts_pts.append((aux_x0 + rx * scale, aux_y0 + ry * scale))

    # SVG rendering
    svg_elements = ""
    
    # Format functions
    def format_pts(pts):
        return " ".join([f"{int(p[0])},{int(p[1])}" for p in pts])

    # Draw Stage 1 Top View (Square and diagonals)
    svg_elements += f'<polygon data-step="2" points="{format_pts(tv_base)}" fill="none" stroke="blue" stroke-width="2" />'
    for i in range(4):
        svg_elements += f'<line data-step="2" x1="{int(tv_base[i][0])}" y1="{int(tv_base[i][1])}" x2="{int(tv_apex[0])}" y2="{int(tv_apex[1])}" stroke="blue" stroke-width="1" />'
        svg_elements += f'<text data-step="2" x="{int(tv_base[i][0]) - 10}" y="{int(tv_base[i][1]) + 15}" font-family="Arial" font-size="11" fill="blue">{chr(97+i)}</text>'
        # Projectors
        svg_elements += f'<line data-step="2" x1="{int(tv_base[i][0])}" y1="{int(tv_base[i][1])}" x2="{int(tv_base[i][0])}" y2="{y_ref}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
        
    svg_elements += f'<text data-step="2" x="{int(tv_apex[0]) + 6}" y="{int(tv_apex[1]) - 4}" font-family="Arial" font-size="11" fill="blue">o</text>'

    # Draw Front View (Outline and axis)
    svg_elements += f'<line data-step="2" x1="{int(fv_base[0][0])}" y1="{y_ref}" x2="{int(fv_base[2][0])}" y2="{y_ref}" stroke="red" stroke-width="2" />'
    svg_elements += f'<line data-step="2" x1="{int(fv_base[0][0])}" y1="{y_ref}" x2="{int(fv_apex[0])}" y2="{int(fv_apex[1])}" stroke="red" stroke-width="2" />'
    svg_elements += f'<line data-step="2" x1="{int(fv_base[2][0])}" y1="{y_ref}" x2="{int(fv_apex[0])}" y2="{int(fv_apex[1])}" stroke="red" stroke-width="2" />'
    svg_elements += f'<line data-step="2" x1="{int(cx_fv)}" y1="{y_ref}" x2="{int(cx_fv)}" y2="{int(fv_apex[1])}" stroke="black" stroke-width="1.2" stroke-dasharray="15,5,3,5" />'

    # Draw Cutting Plane in FV
    cut_x1 = cx_fv - 65 * scale
    cut_y1 = y_ref - cut_height * scale - math.tan(beta_rad) * (cut_x1 - cx_fv)
    cut_x2 = cx_fv + 65 * scale
    cut_y2 = y_ref - cut_height * scale - math.tan(beta_rad) * (cut_x2 - cx_fv)
    
    svg_elements += f'<line data-step="3" x1="{int(cut_x1)}" y1="{int(cut_y1)}" x2="{int(cut_x2)}" y2="{int(cut_y2)}" stroke="purple" stroke-width="1.5" stroke-dasharray="15,5,3,5" />'
    # Thick ends
    svg_elements += f'<line data-step="3" x1="{int(cut_x1)}" y1="{int(cut_y1)}" x2="{int(cut_x1 + 8*math.cos(beta_rad))}" y2="{int(cut_y1 + 8*math.sin(beta_rad))}" stroke="purple" stroke-width="3.5" />'
    svg_elements += f'<line data-step="3" x1="{int(cut_x2)}" y1="{int(cut_y2)}" x2="{int(cut_x2 - 8*math.cos(beta_rad))}" y2="{int(cut_y2 - 8*math.sin(beta_rad))}" stroke="purple" stroke-width="3.5" />'

    # Draw Projectors and Hatching in TV
    if tv_cuts:
        svg_elements += f'<polygon data-step="4" points="{format_pts(tv_cuts)}" fill="url(#hatch-purple)" stroke="purple" stroke-width="2" />'
        for i, p in enumerate(tv_cuts):
            svg_elements += f'<circle data-step="4" cx="{int(p[0])}" cy="{int(p[1])}" r="3" fill="purple" />'
            svg_elements += f'<line data-step="4" x1="{int(fv_cuts[i][0])}" y1="{int(fv_cuts[i][1])}" x2="{int(p[0])}" y2="{int(p[1])}" stroke="purple" stroke-width="0.5" stroke-dasharray="2" />'

    # Draw Auxiliary plane X1Y1 and True Shape
    aux_line_x1 = aux_x0 - 70 * math.cos(beta_rad) * scale
    aux_line_y1 = aux_y0 - 70 * math.sin(beta_rad) * scale
    aux_line_x2 = aux_x0 + 130 * math.cos(beta_rad) * scale
    aux_line_y2 = aux_y0 + 130 * math.sin(beta_rad) * scale
    
    svg_elements += f'<line data-step="5" x1="{int(aux_line_x1)}" y1="{int(aux_line_y1)}" x2="{int(aux_line_x2)}" y2="{int(aux_line_y2)}" stroke="black" stroke-width="1.2" />'
    svg_elements += f'<text data-step="5" x="{int(aux_line_x1) - 15}" y="{int(aux_line_y1) - 5}" font-family="Arial" font-size="12" font-weight="bold">X₁</text>'
    svg_elements += f'<text data-step="5" x="{int(aux_line_x2) + 8}" y="{int(aux_line_y2) - 5}" font-family="Arial" font-size="12" font-weight="bold">Y₁</text>'

    if ts_pts:
        svg_elements += f'<polygon data-step="6" points="{format_pts(ts_pts)}" fill="url(#hatch-green)" stroke="green" stroke-width="2.5" />'
        for i, p in enumerate(ts_pts):
            svg_elements += f'<circle data-step="6" cx="{int(p[0])}" cy="{int(p[1])}" r="3" fill="green" />'
            # Projectors to True Shape
            svg_elements += f'<line data-step="5" x1="{int(fv_cuts[i%len(fv_cuts)][0])}" y1="{int(fv_cuts[i%len(fv_cuts)][1])}" x2="{int(p[0])}" y2="{int(p[1])}" stroke="purple" stroke-width="0.5" stroke-dasharray="2" />'

    case_title = f"Section of {solid_type.replace('_',' ').capitalize()} (Cut Plane inclined at {cut_angle}° to HP)"
    
    steps = [
        "Draw the reference line XY using a thin 2H pencil. Label the endpoints as X and Y using a medium H pencil.",
        f"Draw the simple projections (Front View and Top View) of the solid of base side {side}mm and axis length {axis_len}mm using a dark HB pencil for final outlines and a thin 2H pencil for projector lines.",
        f"Draw the cutting plane line in the Front View representing the Auxiliary Inclined Plane (AIP). The cutting plane is inclined at {cut_angle}° to the XY line and passes through the axis at a height of {cut_height}mm from the base. Represent it by a section line (thin chain-dotted 2H line in the middle, thick HB lines at the ends).",
        "Identify and mark the cut points (1', 2', 3'...) where the cutting plane intersects the slant/lateral edges in the Front View.",
        "Project these cut points vertically downwards onto the corresponding slant edges in the Top View using thin vertical projector lines drawn with a 2H pencil. Mark these points as 1, 2, 3...",
        "Connect the cut points in the Top View with a dark HB pencil to show the sectional boundary. Fill this sectional area with thin hatching lines (inclined at 45° and spaced 2-3mm apart) using a medium H pencil to complete the Sectional Top View.",
        f"Draw an auxiliary reference line X₁Y₁ parallel to the cutting plane line at a convenient distance using a thin 2H pencil.",
        "Draw thin projector lines perpendicular to the cutting plane from each cut point in the Front View, extending past the X₁Y₁ line, using a thin 2H pencil.",
        "Measure the perpendicular distances of the cut points (1, 2, 3...) in the Top View from the XY line. Transfer these distances onto the corresponding auxiliary projector lines, measuring from the X₁Y₁ line.",
        "Mark the transferred points (1₁, 2₁, 3₁...) and join them using a dark HB pencil to obtain the True Shape of the Section. Hatch this True Shape area at 45° using a medium H pencil."
    ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 430" width="100%" height="400" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <defs>
            <pattern id="hatch-purple" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="8" stroke="purple" stroke-width="0.8" />
            </pattern>
            <pattern id="hatch-green" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="8" stroke="green" stroke-width="0.8" />
            </pattern>
        </defs>
        <!-- Reference Line XY -->
        <line data-step="1" x1="20" y1="{y_ref}" x2="630" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="10" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="635" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        {svg_elements}
    </svg>
    """

    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Solid = {solid_type.replace('_',' ').capitalize()}<br>Base = {side}mm | Height = {axis_len}mm<br>Cut Plane Normal = [0, {B_normal:.2f}, {C_normal:.2f}] at Y={cut_height}mm",
        "found_values": "t-value edge intersections computed.<br>Sectional Top View: Hatching drawn.<br>True Shape of Section: Projected onto X₁Y₁ plane."
    }

def re_find_all_numbers_near_axis(q_lower):
    matches = re.findall(r'(\d+)\s*mm\s*(?:from|above)\s*(?:base|the base)', q_lower)
    if not matches:
        matches = re.findall(r'distance\s*(\d+)', q_lower)
    return matches
