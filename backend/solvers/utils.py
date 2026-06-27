import re
import math

def parse_question(question: str) -> dict:
    """
    Parses a natural language question statement to extract engineering graphics parameters semantically.
    """
    q_lower = question.lower()
    
    # Classify topic
    topic = "point"
    if "isometric" in q_lower:
        topic = "isometric"
    elif "development" in q_lower or "lateral surface" in q_lower:
        topic = "development"
    elif "section" in q_lower or "sectional" in q_lower or "cut by" in q_lower:
        topic = "section"
    elif "prism" in q_lower or "pyramid" in q_lower or "cone" in q_lower or "cylinder" in q_lower:
        topic = "solid"
    elif "plane" in q_lower or "lamina" in q_lower or "plate" in q_lower or "pentagon" in q_lower or "hexagon" in q_lower or "triangle" in q_lower or "square" in q_lower or "rectangle" in q_lower or "circle" in q_lower or "circular" in q_lower:
        topic = "plane"
    elif "line" in q_lower:
        topic = "line"
    else:
        topic = "point"

    # Specific shape identification
    shape = "pentagon"
    if "triangle" in q_lower or "triangular" in q_lower:
        shape = "triangle"
    elif "square" in q_lower:
        shape = "square"
    elif "rectangle" in q_lower or "rectangular" in q_lower:
        shape = "rectangle"
    elif "pentagon" in q_lower or "pentagonal" in q_lower:
        shape = "pentagon"
    elif "hexagon" in q_lower or "hexagonal" in q_lower:
        shape = "hexagon"
    elif "circle" in q_lower or "circular" in q_lower:
        shape = "circle"

    # Specific solid type
    solid_type = None
    if "prism" in q_lower:
        solid_type = f"{shape}_prism" if shape else "square_prism"
    elif "pyramid" in q_lower:
        solid_type = f"{shape}_pyramid" if shape else "square_pyramid"
    elif "cylinder" in q_lower:
        solid_type = "cylinder"
    elif "cone" in q_lower:
        solid_type = "cone"

    # Defaults
    side_len = 30
    length = 70
    above_hp = 20
    in_front_vp = 25
    hp_angle = 30
    vp_angle = 45

    # Extract angles (inclination to HP and VP)
    hp_matches = re.findall(r'(\d+)\s*(?:degrees|degree|°)?\s*(?:inclined\s+)?to\s+(?:the\s+)?hp', q_lower)
    if not hp_matches:
        hp_matches = re.findall(r'inclined\s+at\s*(\d+)\s*(?:degrees|degree|°)?\s*(?:with|to)\s+(?:the\s+)?hp', q_lower)
    if hp_matches:
        hp_angle = int(hp_matches[0])
        
    vp_matches = re.findall(r'(\d+)\s*(?:degrees|degree|°)?\s*(?:inclined\s+)?to\s+(?:the\s+)?vp', q_lower)
    if not vp_matches:
        vp_matches = re.findall(r'inclined\s+at\s*(\d+)\s*(?:degrees|degree|°)?\s*(?:with|to)\s+(?:the\s+)?vp', q_lower)
    if vp_matches:
        vp_angle = int(vp_matches[0])

    # Dynamic distance parsing using context regexes
    hp_dist_match = re.search(r'(\d+)\s*mm\s*(?:above|below)\s*(?:the\s+)?hp', q_lower)
    if not hp_dist_match:
        hp_dist_match = re.search(r'(?:above|below)\s*(?:the\s+)?hp\s*(?:by\s+)?(\d+)\s*mm', q_lower)
    if hp_dist_match:
        above_hp = int(hp_dist_match.group(1))

    vp_dist_match = re.search(r'(\d+)\s*mm\s*(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp', q_lower)
    if not vp_dist_match:
        vp_dist_match = re.search(r'(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp\s*(?:by\s+)?(\d+)\s*mm', q_lower)
    if vp_dist_match:
        in_front_vp = int(vp_dist_match.group(1))

    # Base Side / Edge / Diameter
    side_match = re.search(r'(\d+)\s*mm\s*(?:side|edge|diameter|radius|base)', q_lower)
    if not side_match:
        side_match = re.search(r'(?:side|edge|diameter|base)\s*(?:of\s+)?(\d+)\s*mm', q_lower)
    if side_match:
        side_len = int(side_match.group(1))

    # Axis Length / Long / Height
    len_match = re.search(r'(\d+)\s*mm\s*(?:long|axis|height|length)', q_lower)
    if not len_match:
        len_match = re.search(r'(?:axis|height|length)\s*(?:of\s+)?(\d+)\s*mm', q_lower)
    if len_match:
        length = int(len_match.group(1))

    # Fallbacks and overrides
    numbers = [int(num) for num in re.findall(r'\d+', question)]
    
    # Override for Point coordinates explicitly
    if topic == "point" and len(numbers) >= 2:
        above_hp = numbers[0]
        in_front_vp = numbers[1]
    # Override for Line coordinates explicitly
    elif topic == "line" and len(numbers) >= 3:
        length = numbers[0]
        above_hp = numbers[1]
        in_front_vp = numbers[2]
        
    inclined_to_both = ("hp" in q_lower and "vp" in q_lower)

    # Detect Distance between End Projectors (DEP) line problem
    is_dep_problem = False
    ha, da, hb, db, dep = 10, 20, 50, 70, 50  # defaults
    dep_match = re.search(r'distance\s+between\s+(?:the\s+|their\s+)?(?:end\s+)?projectors\s+(?:of\s+the\s+line\s+)?(?:is|are)\s*(\d+)', q_lower)
    if not dep_match:
        dep_match = re.search(r'projectors\s+.*?(\d+)\s*mm\s+apart', q_lower)
    if not dep_match:
        dep_match = re.search(r'distance\s+between\s+(?:the\s+|their\s+)?(?:end\s+)?projectors.*?\b(\d+)\b', q_lower)

    if dep_match:
        is_dep_problem = True
        dep = int(dep_match.group(1))

        # Helper to find HP and VP coordinates in a substring
        def extract_coords(text):
            hp_val = None
            hp_match = re.search(r'(\d+)\s*mm\s*(?:above|below)\s*(?:the\s+)?hp', text)
            if not hp_match:
                hp_match = re.search(r'(?:above|below)\s*(?:the\s+)?hp\s*(?:by\s+)?(\d+)\s*mm', text)
            if hp_match:
                hp_val = int(hp_match.group(1))
                
            vp_val = None
            vp_match = re.search(r'(\d+)\s*mm\s*(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp', text)
            if not vp_match:
                vp_match = re.search(r'(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp\s*(?:by\s+)?(\d+)\s*mm', text)
            if vp_match:
                vp_val = int(vp_match.group(1))
                
            return hp_val, vp_val

        # Locate positions of 'a' and 'b' (as words) to split context
        pos_a = [m.start() for m in re.finditer(r'\b(a|end a|point a)\b', q_lower)]
        pos_b = [m.start() for m in re.finditer(r'\b(b|end b|point b)\b', q_lower)]
        
        extracted_ha, extracted_da = None, None
        extracted_hb, extracted_db = None, None

        if pos_a and pos_b:
            first_a = pos_a[0]
            first_b = pos_b[0]
            if first_a < first_b:
                sub_a = q_lower[first_a:first_b]
                sub_b = q_lower[first_b:]
            else:
                sub_b = q_lower[first_b:first_a]
                sub_a = q_lower[first_a:]
            extracted_ha, extracted_da = extract_coords(sub_a)
            extracted_hb, extracted_db = extract_coords(sub_b)
        
        # Fallback to general coordinate extraction if not found in substrings
        if extracted_ha is None or extracted_da is None or extracted_hb is None or extracted_db is None:
            all_hp = re.findall(r'(\d+)\s*mm\s*(?:above|below)\s*(?:the\s+)?hp', q_lower)
            all_vp = re.findall(r'(\d+)\s*mm\s*(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp', q_lower)
            if len(all_hp) >= 2 and len(all_vp) >= 2:
                if extracted_ha is None: extracted_ha = int(all_hp[0])
                if extracted_da is None: extracted_da = int(all_vp[0])
                if extracted_hb is None: extracted_hb = int(all_hp[1])
                if extracted_db is None: extracted_db = int(all_vp[1])

        if extracted_ha is not None: ha = extracted_ha
        if extracted_da is not None: da = extracted_da
        if extracted_hb is not None: hb = extracted_hb
        if extracted_db is not None: db = extracted_db

    return {
        "topic": topic,
        "shape": shape,
        "solid_type": solid_type,
        "side_len": side_len,
        "length": length,
        "hp_angle": hp_angle,
        "vp_angle": vp_angle,
        "above_hp": above_hp,
        "in_front_vp": in_front_vp,
        "inclined_to_both": inclined_to_both,
        "is_dep_problem": is_dep_problem,
        "ha": ha,
        "da": da,
        "hb": hb,
        "db": db,
        "dep": dep,
        "raw_numbers": numbers
    }

def rotate_point(x, y, cx, cy, angle_deg):
    """
    Rotate a 2D point (x, y) around (cx, cy) by angle_deg.
    """
    rad = math.radians(angle_deg)
    dx = x - cx
    dy = y - cy
    rx = dx * math.cos(rad) - dy * math.sin(rad)
    ry = dx * math.sin(rad) + dy * math.cos(rad)
    return cx + rx, cy + ry

# =====================================================================
# SYLLABUS SPECIFIC 3D GRAPHICS PIPELINE
# =====================================================================

def rotate_x_3d(v, alpha_deg):
    """
    Apply rotation matrix Rx(alpha) to 3D vertex v = (x, y, z).
    Rx = [
       [1,  0,          0],
       [0,  cos(alpha), -sin(alpha)],
       [0,  sin(alpha),  cos(alpha)]
    ]
    """
    x, y, z = v
    alpha_rad = math.radians(alpha_deg)
    cos_a = math.cos(alpha_rad)
    sin_a = math.sin(alpha_rad)
    
    rx = x
    ry = y * cos_a - z * sin_a
    rz = y * sin_a + z * cos_a
    return (rx, ry, rz)

def rotate_y_3d(v, beta_deg):
    """
    Apply rotation matrix Ry(beta) to 3D vertex v = (x, y, z).
    """
    x, y, z = v
    beta_rad = math.radians(beta_deg)
    cos_b = math.cos(beta_rad)
    sin_b = math.sin(beta_rad)
    
    rx = x * cos_b + z * sin_b
    ry = y
    rz = -x * sin_b + z * cos_b
    return (rx, ry, rz)

def project_orthographic(v_3d, cx, cy_ref, scale=1.0):
    """
    Orthographic Multi-View Extractor:
    - Front View (FV): [cx + x*scale, cy_ref - y*scale]
    - Top View (TV): [cx + x*scale, cy_ref + 80 + z*scale]  # Shifted down by 80px to prevent overlap
    """
    x, y, z = v_3d
    fv = (cx + x * scale, cy_ref - y * scale)
    tv = (cx + x * scale, cy_ref + 80 + z * scale)
    return fv, tv

def project_isometric(v_3d, cx, cy, scale=1.0, foreshortening=True):
    """
    Syllabus Isometric Projection Matrix:
    X_iso = x * cos(30) - z * cos(30)
    Y_iso = x * sin(30) + z * sin(30) - y
    Foreshortening factor = 0.816 (if foreshortening is True)
    """
    x, y, z = v_3d
    
    # Apply foreshortening scale
    f_scale = 0.816 if foreshortening else 1.0
    xs = x * f_scale * scale
    ys = y * f_scale * scale
    zs = z * f_scale * scale
    
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))
    
    x_screen = cx + (xs * cos30 - zs * cos30)
    y_screen = cy - (xs * sin30 + zs * sin30 + ys)
    return (x_screen, y_screen)

# =====================================================================
# 3D SHAPE VERTEX SYNTHESIZERS
# =====================================================================

def generate_cylinder_vertices(r, h, n=12):
    """
    Syllabus Cylinder Generator:
    Top base: (R*cos(2pi*i/n), H/2, R*sin(2pi*i/n))
    Bottom base: (R*cos(2pi*i/n), -H/2, R*sin(2pi*i/n))
    """
    top_base = []
    bottom_base = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        cos_ang = math.cos(angle)
        sin_ang = math.sin(angle)
        
        top_base.append((r * cos_ang, h / 2, r * sin_ang))
        bottom_base.append((r * cos_ang, -h / 2, r * sin_ang))
    return top_base, bottom_base

def generate_cone_vertices(r, h, n=12):
    """
    Syllabus Cone Generator:
    Base: (R*cos(2pi*i/n), -H/2, R*sin(2pi*i/n))
    Apex: (0, H/2, 0)
    """
    base = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        cos_ang = math.cos(angle)
        sin_ang = math.sin(angle)
        base.append((r * cos_ang, -h / 2, r * sin_ang))
        
    apex = (0, h / 2, 0)
    return base, apex

def generate_prism_vertices(sides, r, h):
    """
    Regular Prism Generator:
    Top base: (R*cos(2pi*i/n), H/2, R*sin(2pi*i/n))
    Bottom base: (R*cos(2pi*i/n), -H/2, R*sin(2pi*i/n))
    """
    return generate_cylinder_vertices(r, h, n=sides)

def generate_pyramid_vertices(sides, r, h):
    """
    Regular Pyramid Generator:
    Base: (R*cos(2pi*i/n), -H/2, R*sin(2pi*i/n))
    Apex: (0, H/2, 0)
    """
    return generate_cone_vertices(r, h, n=sides)
