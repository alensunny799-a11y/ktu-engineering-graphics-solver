import re

def parse_robust(q_lower):
    # 1. Detect if it's a DEP problem
    is_dep_problem = False
    dep = 50
    # Search for distance between projectors
    dep_match = re.search(r'distance\s+between\s+(?:the\s+|their\s+)?(?:end\s+)?projectors\s+(?:of\s+the\s+line\s+)?(?:is|are)\s*(\d+)', q_lower)
    if not dep_match:
        # try a more relaxed search
        dep_match = re.search(r'projectors\s+.*?(\d+)\s*mm\s+apart', q_lower)
    if not dep_match:
        # just look for distance between projectors and any number after it
        dep_match = re.search(r'distance\s+between\s+(?:the\s+|their\s+)?(?:end\s+)?projectors.*?\b(\d+)\b', q_lower)

    if dep_match:
        is_dep_problem = True
        dep = int(dep_match.group(1))

    # Helper to find HP and VP coordinates in a substring
    def extract_coords(text):
        # Find something like: 10mm above HP and 15mm in front of VP
        # Let's search for HP offset:
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

    # Let's split the string or find coordinates associated with A and B
    # Let's find positions of 'a' and 'b' (as words)
    pos_a = [m.start() for m in re.finditer(r'\b(a|end a|point a)\b', q_lower)]
    pos_b = [m.start() for m in re.finditer(r'\b(b|end b|point b)\b', q_lower)]
    
    ha, da = None, None
    hb, db = None, None

    if pos_a and pos_b:
        # We can extract substrings
        # Substring for A: from pos_a[0] to pos_b[0] (or end of string if b is before a)
        first_a = pos_a[0]
        first_b = pos_b[0]
        if first_a < first_b:
            sub_a = q_lower[first_a:first_b]
            sub_b = q_lower[first_b:]
        else:
            sub_b = q_lower[first_b:first_a]
            sub_a = q_lower[first_a:]
        ha, da = extract_coords(sub_a)
        hb, db = extract_coords(sub_b)
    
    # Fallback to general coordinate extraction if not found
    if ha is None or da is None or hb is None or db is None:
        # Just find all HP/VP coordinate pairs in order
        all_hp = re.findall(r'(\d+)\s*mm\s*(?:above|below)\s*(?:the\s+)?hp', q_lower)
        all_vp = re.findall(r'(\d+)\s*mm\s*(?:in\s+front\s+of|behind)\s*(?:the\s+)?vp', q_lower)
        if len(all_hp) >= 2 and len(all_vp) >= 2:
            if ha is None: ha = int(all_hp[0])
            if da is None: da = int(all_vp[0])
            if hb is None: hb = int(all_hp[1])
            if db is None: db = int(all_vp[1])

    # Defaults if still None
    if ha is None: ha = 10
    if da is None: da = 15
    if hb is None: hb = 50
    if db is None: db = 50

    print(f"is_dep={is_dep_problem}, dep={dep}, A=({ha}, {da}), B=({hb}, {db})")

questions = [
    "End A of a line AB is 10mm above HP & 15mm in front of VP while its end B is 50mm above HP and 50mm in front of VP. The distance between end projectors of the line is 50mm.",
    "A line AB has its end A 10 mm above HP and 15 mm in front of VP. The end B is 50 mm above HP and 50 mm in front of VP. The distance between the end projectors is 50 mm.",
    "A line AB 80mm long has its end A 20mm above HP and 25mm in front of VP. But this is not a DEP problem.",
    "Line AB has end A 15mm above HP and 20mm in front of VP. End B is 60mm above HP and 65mm in front of VP. The projectors are 60mm apart."
]

for q in questions:
    print(q[:60] + "...")
    parse_robust(q.lower())
