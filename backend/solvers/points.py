def solve(params: dict) -> dict:
    hp_dist = params.get("above_hp", 20)
    vp_dist = params.get("in_front_vp", 30)
    question = params.get("raw_question", "")
    
    return solve_point_projections(hp_dist, vp_dist, question)

def solve_point_projections(hp_dist: int, vp_dist: int, question: str) -> dict:
    q_lower = question.lower()
    
    # Defaults
    is_above_hp = True
    is_below_hp = False
    is_in_front_vp = True
    is_behind_vp = False
    
    if "below hp" in q_lower or "below the hp" in q_lower:
        is_above_hp = False
        is_below_hp = True
    if "behind vp" in q_lower or "behind the vp" in q_lower:
        is_in_front_vp = False
        is_behind_vp = True
        
    y_ref = 180
    scale = 1.8 
    x_a = 200 # horizontal placement position Xa
    
    # Apply the Syllabus Point Coordinate Mapping Matrix:
    if is_above_hp and is_in_front_vp:
        quadrant = "First Quadrant (1st)"
        front_view_y = y_ref - (hp_dist * scale)
        top_view_y = y_ref + (vp_dist * scale)
        steps = [
            "Draw a horizontal reference line and label its endpoints as X and Y using a thin 2H pencil.",
            f"Draw a thin vertical projector line perpendicular to the XY line using a 2H pencil.",
            f"Measure {hp_dist}mm above the XY line along the projector and mark the Front View point as a' using a dark HB pencil.",
            f"Measure {vp_dist}mm below the XY line along the projector and mark the Top View point as a using a dark HB pencil.",
            "Draw thin dimension lines with arrowheads and label the distances using a medium H pencil."
        ]
    elif is_above_hp and is_behind_vp:
        quadrant = "Second Quadrant (2nd)"
        front_view_y = y_ref - (hp_dist * scale)
        top_view_y = y_ref - (vp_dist * scale)
        steps = [
            "Draw a horizontal reference line and label its endpoints as X and Y using a thin 2H pencil.",
            f"Draw a thin vertical projector line perpendicular to the XY line using a 2H pencil.",
            f"Measure {hp_dist}mm above the XY line along the projector and mark the Front View point as a' using a dark HB pencil.",
            f"Measure {vp_dist}mm above the XY line along the same projector and mark the Top View point as a using a dark HB pencil.",
            "Draw thin dimension lines with arrowheads and label the distances using a medium H pencil."
        ]
    elif is_below_hp and is_behind_vp:
        quadrant = "Third Quadrant (3rd)"
        front_view_y = y_ref + (hp_dist * scale)
        top_view_y = y_ref - (vp_dist * scale)
        steps = [
            "Draw a horizontal reference line and label its endpoints as X and Y using a thin 2H pencil.",
            f"Draw a thin vertical projector line perpendicular to the XY line using a 2H pencil.",
            f"Measure {hp_dist}mm below the XY line along the projector and mark the Front View point as a' using a dark HB pencil.",
            f"Measure {vp_dist}mm above the XY line along the projector and mark the Top View point as a using a dark HB pencil.",
            "Draw thin dimension lines with arrowheads and label the distances using a medium H pencil."
        ]
    elif is_below_hp and is_in_front_vp:
        quadrant = "Fourth Quadrant (4th)"
        front_view_y = y_ref + (hp_dist * scale)
        top_view_y = y_ref + (vp_dist * scale)
        steps = [
            "Draw a horizontal reference line and label its endpoints as X and Y using a thin 2H pencil.",
            f"Draw a thin vertical projector line perpendicular to the XY line using a 2H pencil.",
            f"Measure {hp_dist}mm below the XY line along the projector and mark the Front View point as a' using a dark HB pencil.",
            f"Measure {vp_dist}mm below the XY line along the same projector and mark the Top View point as a using a dark HB pencil.",
            "Draw thin dimension lines with arrowheads and label the distances using a medium H pencil."
        ]
    else:
        quadrant = "First Quadrant (1st)"
        front_view_y = y_ref - (hp_dist * scale)
        top_view_y = y_ref + (vp_dist * scale)
        steps = [
            "Draw a horizontal reference line and label its endpoints as X and Y using a thin 2H pencil.",
            "Draw a thin vertical projector line using a 2H pencil.",
            f"Mark the Front View a' {hp_dist}mm above the XY line using a dark HB pencil.",
            f"Mark the Top View a {vp_dist}mm below the XY line using a dark HB pencil.",
            "Draw thin dimension lines with arrowheads using a medium H pencil."
        ]
        
    svg_template = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 350" width="100%" height="350" style="background-color: #ffffff; border: 1px solid #cccccc;">
        <!-- Ground XY Reference Line -->
        <line data-step="1" x1="30" y1="{y_ref}" x2="370" y2="{y_ref}" stroke="black" stroke-width="1.5" />
        <text data-step="1" x="15" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
        <text data-step="1" x="375" y="{y_ref + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
        
        <!-- Projector line linking views -->
        <line data-step="2" x1="{x_a}" y1="{front_view_y}" x2="{x_a}" y2="{top_view_y}" stroke="#7f8c8d" stroke-width="0.75" stroke-dasharray="2" />
        
        <!-- Front view node -->
        <circle data-step="3" cx="{x_a}" cy="{front_view_y}" r="4" fill="black" />
        <text data-step="3" x="{x_a + 12}" y="{front_view_y + 4}" font-family="Arial" font-size="12" fill="black" font-weight="bold">a'</text>
        
        <!-- Top view node -->
        <circle data-step="4" cx="{x_a}" cy="{top_view_y}" r="4" fill="black" />
        <text data-step="4" x="{x_a + 12}" y="{top_view_y + 4}" font-family="Arial" font-size="12" fill="black" font-weight="bold">a</text>
    </svg>
    """
    
    return {
        "type": f"Projection of Point ({quadrant})",
        "steps": steps,
        "svg": svg_template.strip(),
        "given_data": f"Point distance to HP = {hp_dist}mm<br>Point distance to VP = {vp_dist}mm",
        "found_values": f"Location: {quadrant}<br>Front View (a'): [{x_a}, Yref - {hp_dist}mm]<br>Top View (a): [{x_a}, Yref + {vp_dist}mm]"
    }
