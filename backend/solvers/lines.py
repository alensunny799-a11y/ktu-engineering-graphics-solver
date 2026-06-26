import math

def solve(params: dict) -> dict:
    if params.get("is_dep_problem"):
        ha = params.get("ha", 10)
        da = params.get("da", 20)
        hb = params.get("hb", 50)
        db = params.get("db", 70)
        dep = params.get("dep", 50)
        return solve_dep_problem(ha, da, hb, db, dep)

    question = params.get("raw_question", "")
    q_lower = question.lower()
    
    tl = params.get("length", 70)
    above_hp = params.get("above_hp", 15)
    in_front_vp = params.get("in_front_vp", 20)
    theta = params.get("hp_angle", 30)
    phi = params.get("vp_angle", 45)
    
    # Check if inclined to HP, VP, or both
    has_hp_inc = "hp" in q_lower or theta > 0
    has_vp_inc = "vp" in q_lower or phi > 0
    
    if has_hp_inc and has_vp_inc:
        return solve_inclined_to_both(tl, above_hp, in_front_vp, theta, phi)
    elif has_hp_inc:
        return solve_inclined_to_hp(tl, above_hp, in_front_vp, theta)
    elif has_vp_inc:
        return solve_inclined_to_vp(tl, above_hp, in_front_vp, phi)
    else:
        return solve_parallel_to_both(tl, above_hp, in_front_vp)

def solve_inclined_to_both(tl, above_hp, in_front_vp, theta, phi):
    y_ref = 180  
    scale = 2.0      
    start_x = 150    

    # Start points a' and a
    start_fv_y = y_ref - (above_hp * scale)
    start_tv_y = y_ref + (in_front_vp * scale)

    theta_rad = math.radians(theta)
    phi_rad = math.radians(phi)

    # Step 1: Compute Locus Heights (Y-axis constraints)
    locus_b_prime_y = start_fv_y - (tl * math.sin(theta_rad) * scale)
    locus_b_y = start_tv_y + (tl * math.sin(phi_rad) * scale)

    # Step 2: Calculate Apparent Lengths (Plan & Elevation lengths)
    length_top_view_plan = tl * math.cos(theta_rad)       # Plan length
    length_front_view_elevation = tl * math.cos(phi_rad) # Elevation length

    # Step 3: Solve Intersections via Arc Intercepts
    r_tv_pixel = length_top_view_plan * scale
    dy_tv_pixel = abs(locus_b_y - start_tv_y)
    
    r_fv_pixel = length_front_view_elevation * scale
    dy_fv_pixel = abs(locus_b_prime_y - start_fv_y)

    try:
        if r_tv_pixel >= dy_tv_pixel:
            dx_tv = math.sqrt(r_tv_pixel**2 - dy_tv_pixel**2)
        else:
            dx_tv = r_tv_pixel * 0.75
            
        if r_fv_pixel >= dy_fv_pixel:
            dx_fv = math.sqrt(r_fv_pixel**2 - dy_fv_pixel**2)
        else:
            dx_fv = r_fv_pixel * 0.75
            
        d_pixel = (dx_tv + dx_fv) / 2
    except Exception:
        d_pixel = r_tv_pixel * 0.7

    end_x = start_x + int(d_pixel)

    # Calculate apparent angles alpha and beta
    alpha_deg = int(math.degrees(math.atan2(abs(locus_b_prime_y - start_fv_y), (end_x - start_x))))
    beta_deg = int(math.degrees(math.atan2(abs(locus_b_y - start_tv_y), (end_x - start_x))))

    # Apparent view lengths
    fv_len = int(math.hypot(end_x - start_x, locus_b_prime_y - start_fv_y) / scale)
    tv_len = int(math.hypot(end_x - start_x, locus_b_y - start_tv_y) / scale)

    case_title = "Line Inclined to HP and VP (Rotating Line Method)"
    
    steps = [
        "Draw a horizontal reference line and label it as XY using a thin 2H pencil.",
        f"Draw a thin vertical projector line. Mark the front view end point a' ({above_hp}mm above XY) and top view end point a ({in_front_vp}mm below XY) using a dark HB pencil.",
        f"From a', draw the true length line a'b1' ({tl}mm long) at true inclination θ = {theta}° to the XY line using a 2H pencil. Draw the locus of b' as a thin horizontal line passing through b1'.",
        f"From a, draw the true length line ab2 ({tl}mm long) at true inclination φ = {phi}° to the XY line using a 2H pencil. Draw the locus of b as a thin horizontal line passing through b2.",
        "Drop a vertical projector from b1' to the level of a to find point b1. With a as center and radius ab1, swing an arc to intersect the locus of b to locate point b.",
        "Project b2 vertically up to the level of a' to find point b2'. With a' as center and radius a'b2', swing an arc to intersect the locus of b' to locate point b'.",
        f"Connect a'b' with a thick line (Front View, length = {fv_len}mm, apparent angle α = {alpha_deg}°) using a dark HB pencil.",
        f"Connect ab with a thick line (Top View, length = {tv_len}mm, apparent angle β = {beta_deg}°) using a dark HB pencil.",
        "Check that points b' and b lie on the same vertical projector line, and add dimension lines and arrows using an H pencil."
    ]

    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 450" width="100%" height="420" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <!-- Locus lines -->
        <line data-step="4" x1="40" y1="{locus_b_prime_y}" x2="560" y2="{locus_b_prime_y}" stroke="#95a5a6" stroke-width="0.75" stroke-dasharray="4" />
        <text data-step="4" x="565" y="{locus_b_prime_y + 4}" font-family="Arial" font-size="11" fill="#7f8c8d">Locus of b'</text>
        <line data-step="4" x1="40" y1="{locus_b_y}" x2="560" y2="{locus_b_y}" stroke="#95a5a6" stroke-width="0.75" stroke-dasharray="4" />
        <text data-step="4" x="565" y="{locus_b_y + 4}" font-family="Arial" font-size="11" fill="#7f8c8d">Locus of b</text>
        
        <!-- XY line -->
        <line data-step="1" x1="30" y1="{y_ref}" x2="580" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="15" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="590" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        <!-- Projector A -->
        <line data-step="2" x1="{start_x}" y1="{start_fv_y}" x2="{start_x}" y2="{start_tv_y}" stroke="#7f8c8d" stroke-width="0.75" />
        <circle data-step="2" cx="{start_x}" cy="{start_fv_y}" r="4" fill="black" />
        <circle data-step="2" cx="{start_x}" cy="{start_tv_y}" r="4" fill="black" />
        <text data-step="2" x="{start_x - 22}" y="{start_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a'</text>
        <text data-step="2" x="{start_x - 20}" y="{start_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a</text>
        
        <!-- True Lengths -->
        <line data-step="3" x1="{start_x}" y1="{start_fv_y}" x2="{start_x + int(tl*math.cos(theta_rad)*scale)}" y2="{locus_b_prime_y}" stroke="#bdc3c7" stroke-width="1.2" stroke-dasharray="3" />
        <text data-step="3" x="{start_x + int(tl*math.cos(theta_rad)*scale) + 8}" y="{locus_b_prime_y - 5}" font-family="Arial" font-size="12" font-weight="bold" fill="#7f8c8d">b1'</text>
        
        <line data-step="3" x1="{start_x}" y1="{start_tv_y}" x2="{start_x + int(tl*math.cos(phi_rad)*scale)}" y2="{locus_b_y}" stroke="#bdc3c7" stroke-width="1.2" stroke-dasharray="3" />
        <text data-step="3" x="{start_x + int(tl*math.cos(phi_rad)*scale) + 8}" y="{locus_b_y + 16}" font-family="Arial" font-size="12" font-weight="bold" fill="#7f8c8d">b2</text>
        
        <!-- Projection arcs -->
        <path data-step="5" d="M {start_x + int(tl*math.cos(theta_rad)*scale)} {start_tv_y} A {int(length_top_view_plan*scale)} {int(length_top_view_plan*scale)} 0 0 1 {end_x} {locus_b_y}" fill="none" stroke="#db2777" stroke-width="0.75" stroke-dasharray="2" />
        <path data-step="6" d="M {start_x + int(tl*math.cos(phi_rad)*scale)} {start_fv_y} A {int(length_front_view_elevation*scale)} {int(length_front_view_elevation*scale)} 0 0 0 {end_x} {locus_b_prime_y}" fill="none" stroke="#db2777" stroke-width="0.75" stroke-dasharray="2" />
        
        <!-- Top view -->
        <line data-step="8" x1="{start_x}" y1="{start_tv_y}" x2="{end_x}" y2="{locus_b_y}" stroke="blue" stroke-width="3" />
        <circle data-step="8" cx="{end_x}" cy="{locus_b_y}" r="4" fill="black" />
        <text data-step="8" x="{end_x + 10}" y="{locus_b_y + 12}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b</text>
        
        <!-- Projector B -->
        <line data-step="8" x1="{end_x}" y1="{locus_b_prime_y}" x2="{end_x}" y2="{locus_b_y}" stroke="#7f8c8d" stroke-width="0.75" stroke-dasharray="2" />
        
        <!-- Front view -->
        <line data-step="8" x1="{start_x}" y1="{start_fv_y}" x2="{end_x}" y2="{locus_b_prime_y}" stroke="red" stroke-width="3" />
        <circle data-step="8" cx="{end_x}" cy="{locus_b_prime_y}" r="4" fill="black" />
        <text data-step="8" x="{end_x + 10}" y="{locus_b_prime_y - 12}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b'</text>
    </svg>
    """
    
    return {
        "type": case_title,
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"True Length (TL) = {tl}mm<br>θ = {theta}° to HP | φ = {phi}° to VP<br>End A: {above_hp}mm above HP, {in_front_vp}mm in front of VP",
        "found_values": f"Locus b' = {above_hp + int(tl*math.sin(theta_rad))}mm | Locus b = {in_front_vp + int(tl*math.sin(phi_rad))}mm<br>Front View (a'b') Apparent Length = {fv_len}mm, α = {alpha_deg}°<br>Top View (ab) Apparent Length = {tv_len}mm, β = {beta_deg}°"
    }

def solve_inclined_to_hp(tl, above_hp, in_front_vp, theta):
    y_ref = 180
    scale = 2.0
    start_x = 150
    
    start_fv_y = y_ref - (above_hp * scale)
    start_tv_y = y_ref + (in_front_vp * scale)
    
    theta_rad = math.radians(theta)
    
    end_fv_x = start_x + int(tl * math.cos(theta_rad) * scale)
    end_fv_y = start_fv_y - int(tl * math.sin(theta_rad) * scale)
    
    end_tv_x = end_fv_x
    end_tv_y = start_tv_y
    
    steps = [
        "Draw a horizontal reference line XY using a thin 2H pencil.",
        f"Mark end points: front view a' ({above_hp}mm above XY) and top view a ({in_front_vp}mm below XY) using a dark HB pencil.",
        f"Since the line is inclined to HP only, draw Front View a'b' ({tl}mm long) at angle θ = {theta}° using an HB pencil.",
        "Draw a thin vertical projector from b' down to the horizontal level of a using a 2H pencil.",
        f"Connect ab with a thick line (Top View, length = {int(tl * math.cos(theta_rad))}mm) using an HB pencil.",
        "Draw dimension lines and label the values using an H pencil."
    ]
    
    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="380" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <line data-step="1" x1="30" y1="{y_ref}" x2="550" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="15" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="560" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        <line data-step="2" x1="{start_x}" y1="{start_fv_y}" x2="{start_x}" y2="{start_tv_y}" stroke="#7f8c8d" stroke-width="0.75" />
        <circle data-step="2" cx="{start_x}" cy="{start_fv_y}" r="4" fill="black" />
        <circle data-step="2" cx="{start_x}" cy="{start_tv_y}" r="4" fill="black" />
        <text data-step="2" x="{start_x - 22}" y="{start_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a'</text>
        <text data-step="2" x="{start_x - 20}" y="{start_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a</text>
        
        <line data-step="3" x1="{start_x}" y1="{start_fv_y}" x2="{end_fv_x}" y2="{end_fv_y}" stroke="red" stroke-width="3" />
        <circle data-step="3" cx="{end_fv_x}" cy="{end_fv_y}" r="4" fill="black" />
        <text data-step="3" x="{end_fv_x + 10}" y="{end_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b'</text>
        
        <line data-step="4" x1="{end_fv_x}" y1="{end_fv_y}" x2="{end_tv_x}" y2="{end_tv_y}" stroke="#95a5a6" stroke-width="0.75" stroke-dasharray="3" />
        
        <line data-step="5" x1="{start_x}" y1="{start_tv_y}" x2="{end_tv_x}" y2="{end_tv_y}" stroke="blue" stroke-width="3" />
        <circle data-step="5" cx="{end_tv_x}" cy="{end_tv_y}" r="4" fill="black" />
        <text data-step="5" x="{end_tv_x + 10}" y="{end_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b</text>
    </svg>
    """
    
    return {
        "type": "Line Inclined to HP, Parallel to VP",
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"True Length (TL) = {tl}mm<br>θ = {theta}° to HP | Parallel to VP<br>End A: {above_hp}mm above HP, {in_front_vp}mm in front of VP",
        "found_values": f"Front View (a'b') Length = {tl}mm, Angle α = {theta}°<br>Top View (ab) Length = {int(tl * math.cos(theta_rad))}mm, Angle β = 0°"
    }

def solve_inclined_to_vp(tl, above_hp, in_front_vp, phi):
    y_ref = 180
    scale = 2.0
    start_x = 150
    
    start_fv_y = y_ref - (above_hp * scale)
    start_tv_y = y_ref + (in_front_vp * scale)
    
    phi_rad = math.radians(phi)
    
    end_tv_x = start_x + int(tl * math.cos(phi_rad) * scale)
    end_tv_y = start_tv_y + int(tl * math.sin(phi_rad) * scale)
    
    end_fv_x = end_tv_x
    end_fv_y = start_fv_y
    
    steps = [
        "Draw a horizontal reference line XY using a thin 2H pencil.",
        f"Mark end points: front view a' ({above_hp}mm above XY) and top view a ({in_front_vp}mm below XY) using a dark HB pencil.",
        f"Since the line is inclined to VP only, draw Top View ab ({tl}mm long) at angle φ = {phi}° using an HB pencil.",
        "Draw a thin vertical projector from b up to the horizontal level of a' using a 2H pencil.",
        f"Connect a'b' with a thick line (Front View, length = {int(tl * math.cos(phi_rad))}mm) using an HB pencil.",
        "Draw dimension lines and label the values using an H pencil."
    ]
    
    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="380" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <line data-step="1" x1="30" y1="{y_ref}" x2="550" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="15" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="560" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        <line data-step="2" x1="{start_x}" y1="{start_fv_y}" x2="{start_x}" y2="{start_tv_y}" stroke="#7f8c8d" stroke-width="0.75" />
        <circle data-step="2" cx="{start_x}" cy="{start_fv_y}" r="4" fill="black" />
        <circle data-step="2" cx="{start_x}" cy="{start_tv_y}" r="4" fill="black" />
        <text data-step="2" x="{start_x - 22}" y="{start_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a'</text>
        <text data-step="2" x="{start_x - 20}" y="{start_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a</text>
        
        <line data-step="3" x1="{start_x}" y1="{start_tv_y}" x2="{end_tv_x}" y2="{end_tv_y}" stroke="blue" stroke-width="3" />
        <circle data-step="3" cx="{end_tv_x}" cy="{end_tv_y}" r="4" fill="black" />
        <text data-step="3" x="{end_tv_x + 10}" y="{end_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b</text>
        
        <line data-step="4" x1="{end_tv_x}" y1="{end_tv_y}" x2="{end_fv_x}" y2="{end_fv_y}" stroke="#95a5a6" stroke-width="0.75" stroke-dasharray="3" />
        
        <line data-step="5" x1="{start_x}" y1="{start_fv_y}" x2="{end_fv_x}" y2="{end_fv_y}" stroke="red" stroke-width="3" />
        <circle data-step="5" cx="{end_fv_x}" cy="{end_fv_y}" r="4" fill="black" />
        <text data-step="5" x="{end_fv_x + 10}" y="{end_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b'</text>
    </svg>
    """
    
    return {
        "type": "Line Inclined to VP, Parallel to HP",
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"True Length (TL) = {tl}mm<br>φ = {phi}° to VP | Parallel to HP<br>End A: {above_hp}mm above HP, {in_front_vp}mm in front of VP",
        "found_values": f"Front View (a'b') Length = {int(tl * math.cos(phi_rad))}mm, Angle α = 0°<br>Top View (ab) Length = {tl}mm, Angle β = {phi}°"
    }

def solve_parallel_to_both(tl, above_hp, in_front_vp):
    y_ref = 180
    scale = 2.0
    start_x = 150
    end_x = start_x + (tl * scale)
    
    start_fv_y = y_ref - (above_hp * scale)
    start_tv_y = y_ref + (in_front_vp * scale)
    
    steps = [
        "Draw a horizontal reference line XY using a thin 2H pencil.",
        f"Mark end points: front view a' ({above_hp}mm above XY) and top view a ({in_front_vp}mm below XY) using a dark HB pencil.",
        f"Draw Front View a'b' ({tl}mm long) parallel to the XY line using an HB pencil.",
        f"Draw Top View ab ({tl}mm long) parallel to the XY line directly below a'b' using an HB pencil.",
        "Draw thin vertical projectors at start and end points using a 2H pencil."
    ]
    
    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="380" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <line data-step="1" x1="30" y1="{y_ref}" x2="550" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="15" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="560" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        <line data-step="2" x1="{start_x}" y1="{start_fv_y}" x2="{start_x}" y2="{start_tv_y}" stroke="#7f8c8d" stroke-width="0.75" />
        <circle data-step="2" cx="{start_x}" cy="{start_fv_y}" r="4" fill="black" />
        <circle data-step="2" cx="{start_x}" cy="{start_tv_y}" r="4" fill="black" />
        <text data-step="2" x="{start_x - 22}" y="{start_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a'</text>
        <text data-step="2" x="{start_x - 20}" y="{start_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">a</text>
        
        <line data-step="3" x1="{start_x}" y1="{start_fv_y}" x2="{end_x}" y2="{start_fv_y}" stroke="red" stroke-width="3" />
        <circle data-step="3" cx="{end_x}" cy="{start_fv_y}" r="4" fill="black" />
        <text data-step="3" x="{end_x + 10}" y="{start_fv_y - 8}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b'</text>
        
        <line data-step="4" x1="{start_x}" y1="{start_tv_y}" x2="{end_x}" y2="{start_tv_y}" stroke="blue" stroke-width="3" />
        <circle data-step="4" cx="{end_x}" cy="{start_tv_y}" r="4" fill="black" />
        <text data-step="4" x="{end_x + 10}" y="{start_tv_y + 20}" font-family="Arial" font-size="14" font-weight="bold" fill="black">b</text>
        
        <line data-step="4" x1="{end_x}" y1="{start_fv_y}" x2="{end_x}" y2="{start_tv_y}" stroke="#7f8c8d" stroke-width="0.75" stroke-dasharray="3" />
    </svg>
    """
    
    return {
        "type": "Line Parallel to both HP and VP",
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"True Length (TL) = {tl}mm<br>Parallel to HP | Parallel to VP<br>End A: {above_hp}mm above HP, {in_front_vp}mm in front of VP",
        "found_values": f"Front View (a'b') Length = {tl}mm, Angle α = 0°<br>Top View (ab) Length = {tl}mm, Angle β = 0°"
    }

def solve_dep_problem(ha, da, hb, db, dep):
    # 1. Compute projection parameters
    tl = math.sqrt(dep**2 + (hb - ha)**2 + (db - da)**2)
    theta = math.degrees(math.asin((hb - ha) / tl))
    phi = math.degrees(math.asin((db - da) / tl))
    
    alpha = math.degrees(math.atan2(hb - ha, dep))
    beta = math.degrees(math.atan2(db - da, dep))
    
    fv_len = math.sqrt(dep**2 + (hb - ha)**2)
    tv_len = math.sqrt(dep**2 + (db - da)**2)
    
    # 2. Compute trace reference points and traces
    x_h_prime = None
    y_ht_val = None
    if hb != ha:
        x_h_prime = - (ha * dep) / (hb - ha)
        y_ht_val = da + (db - da) / dep * x_h_prime

    x_v = None
    y_vt_val = None
    if db != da:
        x_v = - (da * dep) / (db - da)
        y_vt_val = -ha - (hb - ha) / dep * x_v

    # 3. Dynamic scaling and centering layout
    x_min = min(0, dep, fv_len, tv_len)
    if x_h_prime is not None: x_min = min(x_min, x_h_prime)
    if x_v is not None: x_min = min(x_min, x_v)
    
    x_max = max(0, dep, fv_len, tv_len)
    if x_h_prime is not None: x_max = max(x_max, x_h_prime)
    if x_v is not None: x_max = max(x_max, x_v)
    
    y_min = min(-ha, -hb, 0)
    if y_vt_val is not None: y_min = min(y_min, y_vt_val)
    if y_ht_val is not None: y_min = min(y_min, y_ht_val)
    
    y_max = max(da, db, 0)
    if y_vt_val is not None: y_max = max(y_max, y_vt_val)
    if y_ht_val is not None: y_max = max(y_max, y_ht_val)
    
    width_mm = x_max - x_min
    height_mm = y_max - y_min
    
    scale_x = 420.0 / max(width_mm, 1.0)
    scale_y = 300.0 / max(height_mm, 1.0)
    scale = min(scale_x, scale_y, 3.5)
    if scale < 2.0: scale = 2.0
    
    X_start = 330 - ((x_min + x_max) / 2) * scale
    Y_ref = 230 - ((y_min + y_max) / 2) * scale

    # Screen coordinates of key projection endpoints
    a_prime_x, a_prime_y = X_start, Y_ref - ha * scale
    a_x, a_y = X_start, Y_ref + da * scale
    b_prime_x, b_prime_y = X_start + dep * scale, Y_ref - hb * scale
    b_x, b_y = X_start + dep * scale, Y_ref + db * scale

    # Rotated true length projection points
    b1_prime_x, b1_prime_y = X_start + fv_len * scale, Y_ref - ha * scale
    b1_x, b1_y = b1_prime_x, Y_ref + db * scale
    b2_x, b2_y = X_start + tv_len * scale, Y_ref + da * scale
    b2_prime_x, b2_prime_y = b2_x, Y_ref - hb * scale

    # Rotation sweep directions
    sweep_fv = 1 if b_prime_y < a_prime_y else 0
    sweep_tv = 0 if b_y > a_y else 1

    # Screen coordinates of traces
    h_prime_x = X_start + x_h_prime * scale if x_h_prime is not None else None
    h_prime_y = Y_ref
    ht_x = h_prime_x
    ht_y = Y_ref + y_ht_val * scale if y_ht_val is not None else None

    v_x = X_start + x_v * scale if x_v is not None else None
    v_y = Y_ref
    vt_x = v_x
    vt_y = Y_ref + y_vt_val * scale if y_vt_val is not None else None

    # Extension limits for drawing trace extension lines
    ext_x_mm = x_min - 15
    ext_fv_y = Y_ref - (ha + (hb - ha) / dep * ext_x_mm) * scale
    ext_tv_y = Y_ref + (da + (db - da) / dep * ext_x_mm) * scale
    ext_x = X_start + ext_x_mm * scale

    # Create step-by-step instructions
    steps = [
        "Draw a horizontal reference line XY using a thin 2H pencil.",
        f"Draw two vertical projector lines at a distance of {dep}mm apart. On the first projector, mark the front view end point a' ({ha}mm above XY) and top view end point a ({da}mm below XY) using an HB pencil.",
        f"On the second projector, mark the front view end point b' ({hb}mm above XY) and top view end point b ({db}mm below XY) using an HB pencil. Connect a'b' (Front View) and ab (Top View) with thick lines.",
        "Draw the locus of b' as a thin horizontal line passing through b', and the locus of b as a thin horizontal line passing through b (2H pencil).",
        "To find the true length and inclination with HP: Rotate the top view ab about end a to make it parallel to XY (point b2). Project b2 vertically up to intersect the locus of b' to locate b2'. Connect a'b2' with a medium line (H pencil) to obtain the true length and true angle θ.",
        "To find the true length and inclination with VP: Rotate the front view a'b' about end a' to make it parallel to XY (point b1'). Project b1' vertically down to intersect the locus of b to locate b1. Connect ab1 with a medium line (H pencil) to obtain the true length and true angle φ.",
        "To locate reference points h' and v: Extend the front view a'b' to intersect the XY line at h'. Extend the top view ab to intersect the XY line at v.",
        "To locate traces HT and VT: Draw a vertical projector from h' to intersect the extension of the top view line to locate the Horizontal Trace (HT). Draw a vertical projector from v to intersect the extension of the front view line to locate the Vertical Trace (VT)."
    ]

    # Convert values to formatted strings
    tl_str = f"{tl:.1f} mm"
    theta_str = f"{theta:.1f}°"
    phi_str = f"{phi:.1f}°"
    alpha_str = f"{alpha:.1f}°"
    beta_str = f"{beta:.1f}°"
    
    ht_str = f"HT at x={x_h_prime:.1f} mm, y={y_ht_val:.1f} mm (below XY)" if y_ht_val is not None else "HT not visible"
    vt_str = f"VT at x={x_v:.1f} mm, y={abs(y_vt_val):.1f} mm ({'above' if y_vt_val < 0 else 'below'} XY)" if y_vt_val is not None else "VT not visible"

    # SVG Construction
    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 520" width="100%" height="480" style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;">
        <!-- Locus lines -->
        <line data-step="4" x1="30" y1="{{b_prime_y}}" x2="670" y2="{{b_prime_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="4,4" />
        <text data-step="4" x="610" y="{{b_prime_y - 6}}" font-family="Arial" font-size="11" fill="#64748b" font-weight="bold">Locus of b'</text>
        
        <line data-step="4" x1="30" y1="{{b_y}}" x2="670" y2="{{b_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="4,4" />
        <text data-step="4" x="610" y="{{b_y + 14}}" font-family="Arial" font-size="11" fill="#64748b" font-weight="bold">Locus of b</text>
        
        <line data-step="4" x1="30" y1="{{a_prime_y}}" x2="670" y2="{{a_prime_y}}" stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="3,3" />
        <line data-step="4" x1="30" y1="{{a_y}}" x2="670" y2="{{a_y}}" stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="3,3" />

        <!-- XY line -->
        <line data-step="1" x1="30" y1="{{Y_ref}}" x2="670" y2="{{Y_ref}}" stroke="#0f172a" stroke-width="2" />
        <text data-step="1" x="15" y="{{Y_ref + 5}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">X</text>
        <text data-step="1" x="678" y="{{Y_ref + 5}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">Y</text>

        <!-- Projectors A and B -->
        <line data-step="2" x1="{{X_start}}" y1="{{a_prime_y}}" x2="{{X_start}}" y2="{{a_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="3,3" />
        <line data-step="2" x1="{{X_start + dep * scale}}" y1="{{b_prime_y}}" x2="{{X_start + dep * scale}}" y2="{{b_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="3,3" />

        <!-- Projector Endpoints -->
        <circle data-step="2" cx="{{X_start}}" cy="{{a_prime_y}}" r="4" fill="#0f172a" />
        <circle data-step="2" cx="{{X_start}}" cy="{{a_y}}" r="4" fill="#0f172a" />
        <circle data-step="2" cx="{{X_start + dep * scale}}" cy="{{b_prime_y}}" r="4" fill="#0f172a" />
        <circle data-step="2" cx="{{X_start + dep * scale}}" cy="{{b_y}}" r="4" fill="#0f172a" />

        <!-- Labels for Points a', a, b', b -->
        <text data-step="2" x="{{X_start - 20}}" y="{{a_prime_y - 8}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">a'</text>
        <text data-step="2" x="{{X_start - 18}}" y="{{a_y + 20}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">a</text>
        <text data-step="2" x="{{X_start + dep * scale + 8}}" y="{{b_prime_y - 8}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">b'</text>
        <text data-step="2" x="{{X_start + dep * scale + 8}}" y="{{b_y + 20}}" font-family="Arial" font-size="14" font-weight="bold" fill="#0f172a">b</text>

        <!-- Front View (a'b') and Top View (ab) -->
        <line data-step="3" x1="{{a_prime_x}}" y1="{{a_prime_y}}" x2="{{b_prime_x}}" y2="{{b_prime_y}}" stroke="#ef4444" stroke-width="3" />
        <line data-step="3" x1="{{a_x}}" y1="{{a_y}}" x2="{{b_x}}" y2="{{b_y}}" stroke="#3b82f6" stroke-width="3" />

        <!-- Rotations & Projections for True Lengths (Step 5: HP, Step 6: VP) -->
        <!-- TV to horizontal (b2) -->
        <path data-step="5" d="M {{b_x}} {{b_y}} A {{int(tv_len * scale)}} {{int(tv_len * scale)}} 0 0 {{sweep_tv}} {{b2_x}} {{b2_y}}" fill="none" stroke="#db2777" stroke-width="0.75" stroke-dasharray="2,2" />
        <line data-step="5" x1="{{a_x}}" y1="{{a_y}}" x2="{{b2_x}}" y2="{{b2_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="3,3" />
        <circle data-step="5" cx="{{b2_x}}" cy="{{b2_y}}" r="3" fill="#db2777" />
        <text data-step="5" x="{{b2_x + 5}}" y="{{b2_y + 15}}" font-family="Arial" font-size="12" font-weight="bold" fill="#db2777">b2</text>
        <line data-step="5" x1="{{b2_x}}" y1="{{b2_y}}" x2="{{b2_prime_x}}" y2="{{b2_prime_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="2,2" />
        <circle data-step="5" cx="{{b2_prime_x}}" cy="{{b2_prime_y}}" r="3" fill="#db2777" />
        <text data-step="5" x="{{b2_prime_x + 5}}" y="{{b2_prime_y - 8}}" font-family="Arial" font-size="12" font-weight="bold" fill="#db2777">b2'</text>
        <!-- FV True Length Line -->
        <line data-step="5" x1="{{a_prime_x}}" y1="{{a_prime_y}}" x2="{{b2_prime_x}}" y2="{{b2_prime_y}}" stroke="#059669" stroke-width="2.0" stroke-dasharray="8,3,2,3" />

        <!-- FV to horizontal (b1') -->
        <path data-step="6" d="M {{b_prime_x}} {{b_prime_y}} A {{int(fv_len * scale)}} {{int(fv_len * scale)}} 0 0 {{sweep_fv}} {{b1_prime_x}} {{b1_prime_y}}" fill="none" stroke="#7c3aed" stroke-width="0.75" stroke-dasharray="2,2" />
        <line data-step="6" x1="{{a_prime_x}}" y1="{{a_prime_y}}" x2="{{b1_prime_x}}" y2="{{b1_prime_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="3,3" />
        <circle data-step="6" cx="{{b1_prime_x}}" cy="{{b1_prime_y}}" r="3" fill="#7c3aed" />
        <text data-step="6" x="{{b1_prime_x + 5}}" y="{{b1_prime_y - 8}}" font-family="Arial" font-size="12" font-weight="bold" fill="#7c3aed">b1'</text>
        <line data-step="6" x1="{{b1_prime_x}}" y1="{{b1_prime_y}}" x2="{{b1_x}}" y2="{{b1_y}}" stroke="#94a3b8" stroke-width="0.75" stroke-dasharray="2,2" />
        <circle data-step="6" cx="{{b1_x}}" cy="{{b1_y}}" r="3" fill="#7c3aed" />
        <text data-step="6" x="{{b1_x + 5}}" y="{{b1_y + 15}}" font-family="Arial" font-size="12" font-weight="bold" fill="#7c3aed">b1</text>
        <!-- TV True Length Line -->
        <line data-step="6" x1="{{a_x}}" y1="{{a_y}}" x2="{{b1_x}}" y2="{{b1_y}}" stroke="#059669" stroke-width="2.0" stroke-dasharray="8,3,2,3" />

        <!-- Traces Construction (Step 7: Extensions, Step 8: Projectors & Traces) -->
        <!-- Collinear extensions -->
        <line data-step="7" x1="{{a_prime_x}}" y1="{{a_prime_y}}" x2="{{ext_x}}" y2="{{ext_fv_y}}" stroke="#64748b" stroke-width="0.75" stroke-dasharray="5,5" />
        <line data-step="7" x1="{{a_x}}" y1="{{a_y}}" x2="{{ext_x}}" y2="{{ext_tv_y}}" stroke="#64748b" stroke-width="0.75" stroke-dasharray="5,5" />

        <!-- h' and v reference points -->
        {{f'<circle data-step="7" cx="{{h_prime_x}}" cy="{{h_prime_y}}" r="3.5" fill="#0f172a" /><text data-step="7" x="{{h_prime_x + 6}}" y="{{h_prime_y - 6}}" font-family="Arial" font-size="12" font-weight="bold" fill="#0f172a">h\'</text>' if h_prime_x is not None else ''}}
        {{f'<circle data-step="7" cx="{{v_x}}" cy="{{v_y}}" r="3.5" fill="#0f172a" /><text data-step="7" x="{{v_x - 16}}" y="{{v_y + 16}}" font-family="Arial" font-size="12" font-weight="bold" fill="#0f172a">v</text>' if v_x is not None else ''}}

        <!-- HT Trace Projection -->
        {{f'<line data-step="8" x1="{{h_prime_x}}" y1="{{h_prime_y}}" x2="{{ht_x}}" y2="{{ht_y}}" stroke="#10b981" stroke-width="1" stroke-dasharray="3,3" /><circle data-step="8" cx="{{ht_x}}" cy="{{ht_y}}" r="5" fill="#10b981" /><text data-step="8" x="{{ht_x + 10}}" y="{{ht_y + 5}}" font-family="Arial" font-size="12" font-weight="bold" fill="#10b981">HT</text>' if ht_x is not None else ''}}

        <!-- VT Trace Projection -->
        {{f'<line data-step="8" x1="{{v_x}}" y1="{{v_y}}" x2="{{vt_x}}" y2="{{vt_y}}" stroke="#8b5cf6" stroke-width="1" stroke-dasharray="3,3" /><circle data-step="8" cx="{{vt_x}}" cy="{{vt_y}}" r="5" fill="#8b5cf6" /><text data-step="8" x="{{vt_x - 24}}" y="{{vt_y + 5}}" font-family="Arial" font-size="12" font-weight="bold" fill="#8b5cf6">VT</text>' if vt_x is not None else ''}}

        <!-- Angles & Annotations (Step 9) -->
        <!-- theta angle arc -->
        <path data-step="9" d="M {{a_prime_x + 25}} {{a_prime_y}} A 25 25 0 0 0 {{a_prime_x + int(25 * math.cos(math.radians(theta)))}} {{a_prime_y - int(25 * math.sin(math.radians(theta)))}}" fill="none" stroke="#0f172a" stroke-width="1" />
        <text data-step="9" x="{{a_prime_x + 32}}" y="{{a_prime_y - 6}}" font-family="Arial" font-size="11" fill="#0f172a">θ={{int(theta)}}°</text>

        <!-- alpha angle arc -->
        <path data-step="9" d="M {{a_prime_x + 40}} {{a_prime_y}} A 40 40 0 0 0 {{a_prime_x + int(40 * math.cos(math.radians(alpha)))}} {{a_prime_y - int(40 * math.sin(math.radians(alpha)))}}" fill="none" stroke="#ef4444" stroke-width="1" />
        <text data-step="9" x="{{a_prime_x + 46}}" y="{{a_prime_y - 18}}" font-family="Arial" font-size="11" fill="#ef4444">α={{int(alpha)}}°</text>

        <!-- phi angle arc -->
        <path data-step="9" d="M {{a_x + 25}} {{a_y}} A 25 25 0 0 1 {{a_x + int(25 * math.cos(math.radians(phi)))}} {{a_y + int(25 * math.sin(math.radians(phi)))}}" fill="none" stroke="#0f172a" stroke-width="1" />
        <text data-step="9" x="{{a_x + 32}}" y="{{a_y + 14}}" font-family="Arial" font-size="11" fill="#0f172a">φ={{int(phi)}}°</text>

        <!-- beta angle arc -->
        <path data-step="9" d="M {{a_x + 40}} {{a_y}} A 40 40 0 0 1 {{a_x + int(40 * math.cos(math.radians(beta)))}} {{a_y + int(40 * math.sin(math.radians(beta)))}}" fill="none" stroke="#3b82f6" stroke-width="1" />
        <text data-step="9" x="{{a_x + 46}}" y="{{a_y + 28}}" font-family="Arial" font-size="11" fill="#3b82f6">β={{int(beta)}}°</text>
    </svg>
    """

    return {
        "type": "Line projections by Distance between End Projectors (DEP)",
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"End A: {ha}mm above HP, {da}mm in front of VP<br>End B: {hb}mm above HP, {db}mm in front of VP<br>Distance between projectors (DEP) = {dep}mm",
        "found_values": f"True Length (TL) = <b>{tl_str}</b><br>θ (HP inclination) = <b>{theta_str}</b> | φ (VP inclination) = <b>{phi_str}</b><br>α = {alpha_str} | β = {beta_str}<br>{ht_str}<br>{vt_str}"
    }
