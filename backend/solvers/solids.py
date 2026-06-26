import math
from solvers import utils

def solve(params: dict) -> dict:
    solid_type = params.get("solid_type", "square_prism")
    side = params.get("side_len", 30)
    axis_len = params.get("length", 65)
    theta = params.get("hp_angle", 45)  # axis inclination to HP
    phi = params.get("vp_angle", 0)     # inclination to VP
    
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
        
    # Check if we should draw 3 stages
    has_three_stages = phi > 0
    
    if has_three_stages:
        scale = 1.15
        y_ref = 190
        cx_s1 = 110  # X placement for stage 1
        cx_s2 = 290  # X placement for stage 2
        cx_s3 = 490  # X placement for stage 3
        canvas_width = 680
    else:
        scale = 1.3
        y_ref = 200
        cx_s1 = 160  # X placement for stage 1
        cx_s2 = 400  # X placement for stage 2
        cx_s3 = 0
        canvas_width = 600
        
    # Radius of bounding circle of base
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
        
    # Generate 3D point cloud centered at (0,0,0) (Module 2.1)
    if is_prism:
        if shape == "circle":
            base_3d, top_3d = utils.generate_cylinder_vertices(r_base, axis_len, n=12)
        elif shape == "triangle":
            base_3d, top_3d = utils.generate_prism_vertices(3, r_base, axis_len)
        elif shape == "square":
            base_3d, top_3d = utils.generate_prism_vertices(4, r_base, axis_len)
        elif shape == "hexagon":
            base_3d, top_3d = utils.generate_prism_vertices(6, r_base, axis_len)
        else:  # pentagon
            base_3d, top_3d = utils.generate_prism_vertices(5, r_base, axis_len)
    else:
        if shape == "circle":
            base_3d, apex_3d = utils.generate_cone_vertices(r_base, axis_len, n=12)
        elif shape == "triangle":
            base_3d, apex_3d = utils.generate_pyramid_vertices(3, r_base, axis_len)
        elif shape == "square":
            base_3d, apex_3d = utils.generate_pyramid_vertices(4, r_base, axis_len)
        elif shape == "hexagon":
            base_3d, apex_3d = utils.generate_pyramid_vertices(6, r_base, axis_len)
        else:  # pentagon
            base_3d, apex_3d = utils.generate_pyramid_vertices(5, r_base, axis_len)

    num_pts = len(base_3d)

    # Move center up so bottom base sits on HP (y = 0) in 3D:
    base_3d = [(v[0], v[1] + axis_len/2, v[2]) for v in base_3d]
    if is_prism:
        top_3d = [(v[0], v[1] + axis_len/2, v[2]) for v in top_3d]
    else:
        apex_3d = (apex_3d[0], apex_3d[1] + axis_len/2, apex_3d[2])

    # STAGE 1 PROJECTIONS (Orthographic multi-view extractor)
    s1_fv_base = []
    s1_tv_base = []
    s1_fv_top = []
    s1_tv_top = []
    s1_fv_apex = None
    s1_tv_apex = None
    
    for v in base_3d:
        fv, tv = utils.project_orthographic(v, cx_s1, y_ref, scale)
        s1_fv_base.append(fv)
        s1_tv_base.append(tv)
        
    if is_prism:
        for v in top_3d:
            fv, tv = utils.project_orthographic(v, cx_s1, y_ref, scale)
            s1_fv_top.append(fv)
            s1_tv_top.append(tv)
    else:
        s1_fv_apex, s1_tv_apex = utils.project_orthographic(apex_3d, cx_s1, y_ref, scale)

    # STAGE 2 PROJECTIONS (Axis inclined to HP)
    # Rotate Rx(alpha) where alpha = 90 - theta
    alpha_deg = 90 - theta
    
    s2_base_3d = [utils.rotate_x_3d(v, alpha_deg) for v in base_3d]
    s2_top_3d = [utils.rotate_x_3d(v, alpha_deg) for v in top_3d] if is_prism else []
    s2_apex_3d = utils.rotate_x_3d(apex_3d, alpha_deg) if is_pyramid else None

    # Project Stage 2 Orthographic views
    s2_fv_base = []
    s2_tv_base = []
    s2_fv_top = []
    s2_tv_top = []
    s2_fv_apex = None
    s2_tv_apex = None

    for v in s2_base_3d:
        fv, tv = utils.project_orthographic(v, cx_s2, y_ref, scale)
        s2_fv_base.append(fv)
        s2_tv_base.append(tv)
        
    if is_prism:
        for v in s2_top_3d:
            fv, tv = utils.project_orthographic(v, cx_s2, y_ref, scale)
            s2_fv_top.append(fv)
            s2_tv_top.append(tv)
    else:
        s2_fv_apex, s2_tv_apex = utils.project_orthographic(s2_apex_3d, cx_s2, y_ref, scale)

    # STAGE 3 PROJECTIONS (Rotated Top View - Inclined to VP)
    s3_fv_base = []
    s3_tv_base = []
    s3_fv_top = []
    s3_tv_top = []
    s3_fv_apex = None
    s3_tv_apex = None
    
    if has_three_stages:
        # Rotate Stage 2 coordinates around Y-axis by phi
        s3_base_3d = [utils.rotate_y_3d(v, phi) for v in s2_base_3d]
        s3_top_3d = [utils.rotate_y_3d(v, phi) for v in s2_top_3d] if is_prism else []
        s3_apex_3d = utils.rotate_y_3d(s2_apex_3d, phi) if is_pyramid else None
        
        # Project to Stage 3 Canvas
        for v in s3_base_3d:
            fv, tv = utils.project_orthographic(v, cx_s3, y_ref, scale)
            s3_fv_base.append(fv)
            s3_tv_base.append(tv)
            
        if is_prism:
            for v in s3_top_3d:
                fv, tv = utils.project_orthographic(v, cx_s3, y_ref, scale)
                s3_fv_top.append(fv)
                s3_tv_top.append(tv)
        else:
            s3_fv_apex, s3_tv_apex = utils.project_orthographic(s3_apex_3d, cx_s3, y_ref, scale)

    # SVG Building
    svg_elements = ""

    def format_pts(pts):
        return " ".join([f"{int(p[0])},{int(p[1])}" for p in pts])

    # 1. DRAW STAGE 1
    # Base (Top View)
    svg_elements += f'<polygon data-step="2" points="{format_pts(s1_tv_base)}" fill="none" stroke="blue" stroke-width="2" />'
    
    # Front View
    if is_prism:
        svg_elements += f'<polygon data-step="2" points="{int(s1_fv_base[0][0])},{int(s1_fv_base[0][1])} {int(s1_fv_base[-1][0])},{int(s1_fv_base[-1][1])} {int(s1_fv_top[-1][0])},{int(s1_fv_top[-1][1])} {int(s1_fv_top[0][0])},{int(s1_fv_top[0][1])}" fill="none" stroke="red" stroke-width="2" />'
        for i in range(num_pts):
            svg_elements += f'<line data-step="2" x1="{int(s1_fv_base[i][0])}" y1="{int(s1_fv_base[i][1])}" x2="{int(s1_fv_top[i][0])}" y2="{int(s1_fv_top[i][1])}" stroke="red" stroke-width="1.2" stroke-dasharray="2" />'
    else:
        svg_elements += f'<line data-step="2" x1="{int(s1_fv_base[0][0])}" y1="{int(s1_fv_base[0][1])}" x2="{int(s1_fv_base[-1][0])}" y2="{int(s1_fv_base[-1][1])}" stroke="red" stroke-width="2" />'
        for i in range(num_pts):
            svg_elements += f'<line data-step="2" x1="{int(s1_fv_base[i][0])}" y1="{int(s1_fv_base[i][1])}" x2="{int(s1_fv_apex[0])}" y2="{int(s1_fv_apex[1])}" stroke="red" stroke-width="1.2" />'

    # Projectors Stage 1
    for i in range(num_pts):
        svg_elements += f'<line data-step="2" x1="{int(s1_fv_base[i][0])}" y1="{int(s1_fv_base[i][1])}" x2="{int(s1_tv_base[i][0])}" y2="{int(s1_tv_base[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    # 2. DRAW STAGE 2
    # Front View (Tilted)
    if is_prism:
        svg_elements += f'<polygon data-step="3" points="{format_pts(s2_fv_base)}" fill="none" stroke="red" stroke-width="2.5" />'
        svg_elements += f'<polygon data-step="3" points="{format_pts(s2_fv_top)}" fill="none" stroke="red" stroke-width="2.5" />'
        for i in range(num_pts):
            svg_elements += f'<line data-step="3" x1="{int(s2_fv_base[i][0])}" y1="{int(s2_fv_base[i][1])}" x2="{int(s2_fv_top[i][0])}" y2="{int(s2_fv_top[i][1])}" stroke="red" stroke-width="1.5" />'
    else:
        svg_elements += f'<polygon data-step="3" points="{" ".join([f"{int(p[0])},{int(p[1])}" for p in s2_fv_base])}" fill="none" stroke="red" stroke-width="2" />'
        for i in range(num_pts):
            svg_elements += f'<line data-step="3" x1="{int(s2_fv_base[i][0])}" y1="{int(s2_fv_base[i][1])}" x2="{int(s2_fv_apex[0])}" y2="{int(s2_fv_apex[1])}" stroke="red" stroke-width="1.5" />'

    # Stage 2 Top View
    svg_elements += f'<polygon data-step="4" points="{format_pts(s2_tv_base)}" fill="none" stroke="blue" stroke-width="2" />'
    if is_prism:
        svg_elements += f'<polygon data-step="4" points="{format_pts(s2_tv_top)}" fill="none" stroke="blue" stroke-width="2" />'
        for i in range(num_pts):
            is_hidden = s2_base_3d[i][2] < 0
            stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2"'
            svg_elements += f'<line data-step="4" x1="{int(s2_tv_base[i][0])}" y1="{int(s2_tv_base[i][1])}" x2="{int(s2_tv_top[i][0])}" y2="{int(s2_tv_top[i][1])}" stroke="blue"{stroke_dash} />'
    else:
        for i in range(num_pts):
            is_hidden = s2_base_3d[i][2] < 0
            stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2"'
            svg_elements += f'<line data-step="4" x1="{int(s2_tv_base[i][0])}" y1="{int(s2_tv_base[i][1])}" x2="{int(s2_tv_apex[0])}" y2="{int(s2_tv_apex[1])}" stroke="blue"{stroke_dash} />'

    # Projectors Stage 2 down
    for i in range(num_pts):
        svg_elements += f'<line data-step="4" x1="{int(s2_fv_base[i][0])}" y1="{int(s2_fv_base[i][1])}" x2="{int(s2_fv_base[i][0])}" y2="{int(s2_tv_base[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
        if is_prism:
            svg_elements += f'<line data-step="4" x1="{int(s2_fv_top[i][0])}" y1="{int(s2_fv_top[i][1])}" x2="{int(s2_fv_top[i][0])}" y2="{int(s2_tv_top[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
            
    if is_pyramid:
        svg_elements += f'<line data-step="4" x1="{int(s2_fv_apex[0])}" y1="{int(s2_fv_apex[1])}" x2="{int(s2_fv_apex[0])}" y2="{int(s2_tv_apex[1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    # 3. DRAW STAGE 3 (If inclined to both)
    if has_three_stages:
        # Rotated Top View
        svg_elements += f'<polygon data-step="5" points="{format_pts(s3_tv_base)}" fill="none" stroke="blue" stroke-width="2" />'
        if is_prism:
            svg_elements += f'<polygon data-step="5" points="{format_pts(s3_tv_top)}" fill="none" stroke="blue" stroke-width="2" />'
            for i in range(num_pts):
                is_hidden = s3_base_3d[i][2] < 0
                stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2"'
                svg_elements += f'<line data-step="5" x1="{int(s3_tv_base[i][0])}" y1="{int(s3_tv_base[i][1])}" x2="{int(s3_tv_top[i][0])}" y2="{int(s3_tv_top[i][1])}" stroke="blue"{stroke_dash} />'
        else:
            for i in range(num_pts):
                is_hidden = s3_base_3d[i][2] < 0
                stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2"'
                svg_elements += f'<line data-step="5" x1="{int(s3_tv_base[i][0])}" y1="{int(s3_tv_base[i][1])}" x2="{int(s3_tv_apex[0])}" y2="{int(s3_tv_apex[1])}" stroke="blue"{stroke_dash} />'

        # Final Front View (Projected)
        if is_prism:
            svg_elements += f'<polygon data-step="6" points="{format_pts(s3_fv_base)}" fill="none" stroke="red" stroke-width="2.5" />'
            svg_elements += f'<polygon data-step="6" points="{format_pts(s3_fv_top)}" fill="none" stroke="red" stroke-width="2.5" />'
            for i in range(num_pts):
                is_hidden = s3_base_3d[i][2] < 0
                stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2.5"'
                svg_elements += f'<line data-step="6" x1="{int(s3_fv_base[i][0])}" y1="{int(s3_fv_base[i][1])}" x2="{int(s3_fv_top[i][0])}" y2="{int(s3_fv_top[i][1])}" stroke="red"{stroke_dash} />'
        else:
            svg_elements += f'<polygon data-step="6" points="{" ".join([f"{int(p[0])},{int(p[1])}" for p in s3_fv_base])}" fill="none" stroke="red" stroke-width="2.5" />'
            for i in range(num_pts):
                is_hidden = s3_base_3d[i][2] < 0
                stroke_dash = ' stroke-dasharray="6,4" stroke-width="1.2"' if is_hidden else ' stroke-width="2.5"'
                svg_elements += f'<line data-step="6" x1="{int(s3_fv_base[i][0])}" y1="{int(s3_fv_base[i][1])}" x2="{int(s3_fv_apex[0])}" y2="{int(s3_fv_apex[1])}" stroke="red"{stroke_dash} />'

        # Projectors between Stage 2 and 3 FV (Horizontal height transfers)
        for i in range(num_pts):
            svg_elements += f'<line data-step="6" x1="{int(s2_fv_base[i][0])}" y1="{int(s2_fv_base[i][1])}" x2="{int(s3_fv_base[i][0])}" y2="{int(s3_fv_base[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
            if is_prism:
                svg_elements += f'<line data-step="6" x1="{int(s2_fv_top[i][0])}" y1="{int(s2_fv_top[i][1])}" x2="{int(s3_fv_top[i][0])}" y2="{int(s3_fv_top[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
        
        if is_pyramid:
            svg_elements += f'<line data-step="6" x1="{int(s2_fv_apex[0])}" y1="{int(s2_fv_apex[1])}" x2="{int(s3_fv_apex[0])}" y2="{int(s3_fv_apex[1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

        # Projectors from Stage 3 TV to Stage 3 FV (Vertical line constraints)
        for i in range(num_pts):
            svg_elements += f'<line data-step="6" x1="{int(s3_tv_base[i][0])}" y1="{int(s3_tv_base[i][1])}" x2="{int(s3_fv_base[i][0])}" y2="{int(s3_fv_base[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'
            if is_prism:
                svg_elements += f'<line data-step="6" x1="{int(s3_tv_top[i][0])}" y1="{int(s3_tv_top[i][1])}" x2="{int(s3_fv_top[i][0])}" y2="{int(s3_fv_top[i][1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

        if is_pyramid:
            svg_elements += f'<line data-step="6" x1="{int(s3_tv_apex[0])}" y1="{int(s3_tv_apex[1])}" x2="{int(s3_fv_apex[0])}" y2="{int(s3_fv_apex[1])}" stroke="#bdc3c7" stroke-width="0.5" stroke-dasharray="2" />'

    # Build Case Title
    case_title = f"Projection of {solid_type.replace('_',' ').capitalize()}"
    if has_three_stages:
        case_title += f" (Inclined to both HP at {theta}° and VP at {phi}°)"
    else:
        case_title += f" (Axis inclined at {theta}° to HP)"

    # Build steps list K. Venugopal style
    if has_three_stages:
        steps = [
            "Draw the horizontal reference line XY using a thin 2H pencil. Label the endpoints X and Y using a medium H pencil.",
            f"STAGE 1: Draw the true shape of the base ({shape} of side/diameter {side}mm) in the Top View (below the XY line) using a dark HB pencil. Draw thin vertical projector lines from all base corners up to the XY line using a thin 2H pencil. Complete the initial Front View of the solid of height {axis_len}mm (resting vertically on HP) using a dark HB pencil.",
            f"STAGE 2: Draw the tilted Front View in the next position, keeping the base/axis inclined at θ = {theta}° to HP (which makes the base inclined at {90-theta}° to the XY line) using a dark HB pencil for outlines and a thin 2H pencil for base/axis lines.",
            "Draw thin vertical projector lines downwards from all corners of the tilted Front View using a thin 2H pencil.",
            "Draw thin horizontal projector lines from the Stage 1 Top View base points to intersect the corresponding vertical projector lines from Stage 2.",
            "Mark the intersection points and connect them using a dark HB pencil for visible boundaries, and dashed lines (1.2px) using a medium H/HB pencil for hidden edges to complete the Stage 2 Top View.",
            f"STAGE 3: Redraw the Stage 2 Top View in the right-hand margin, rotating its axis/resting edge at the given inclination angle φ = {phi}° to the VP (XY line) using a dark HB pencil. Use a thin 2H pencil for rotated construction details.",
            "Draw thin vertical projector lines upwards from all corners of the rotated Top View (Stage 3) and draw horizontal projector lines across from the tilted Front View (Stage 2) using a thin 2H pencil.",
            "Mark the intersection points and connect them using a dark HB pencil for visible boundaries and dashed lines for hidden edges to complete the final Front View.",
            "Draw dimension lines and write labels/values using a medium H pencil."
        ]
    else:
        steps = [
            "Draw the horizontal reference line XY using a thin 2H pencil. Label the endpoints X and Y using a medium H pencil.",
            f"STAGE 1: Draw the true shape of the base ({shape} of side/diameter {side}mm) in the Top View (below the XY line) using a dark HB pencil. Draw thin vertical projector lines from all base corners up to the XY line using a thin 2H pencil. Complete the initial Front View of the solid of height {axis_len}mm (resting vertically on HP) using a dark HB pencil.",
            f"STAGE 2: Draw the tilted Front View in the next position, keeping the base/axis inclined at θ = {theta}° to HP (which makes the base inclined at {90-theta}° to the XY line) using a dark HB pencil for outlines and a thin 2H pencil for base/axis lines.",
            "Draw thin vertical projector lines downwards from all corners of the tilted Front View using a thin 2H pencil.",
            "Draw thin horizontal projector lines from the Stage 1 Top View base points to intersect the corresponding vertical projector lines from Stage 2.",
            "Mark the intersection points and connect them using a dark HB pencil for visible boundaries, and dashed lines (1.2px) using a medium H/HB pencil for hidden edges to complete the final Top View.",
            "Draw dimension lines and write labels/values using a medium H pencil."
        ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width} 430" width="100%" height="400" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <!-- Reference Line XY -->
        <line data-step="1" x1="20" y1="{y_ref}" x2="{canvas_width - 20}" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="10" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="{canvas_width - 15}" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        {svg_elements}
    </svg>
    """

    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Solid = {solid_type.replace('_',' ').capitalize()}<br>Base Side = {side}mm | Axis = {axis_len}mm<br>Axis Inclination = {theta}° to HP" + (f"<br>VP Inclination = {phi}°" if has_three_stages else ""),
        "found_values": f"Rotation Rx({90-theta}°)" + (f"<br>Rotation Ry({phi}°)" if has_three_stages else "") + "<br>All 6 views resolved using First-Angle multi-view coordinates."
    }
