def solve_projection_of_line(question: str):
    q_lower = question.lower()
    numbers = [int(num) for num in re.findall(r'\d+', question)]
    
    # KTU Exam Defaults: TL=70, theta=30 to HP, phi=45 to VP, End A: 15 above HP, 20 in front of VP
    tl = numbers[0] if len(numbers) >= 1 else 70
    above_hp = numbers[1] if len(numbers) >= 2 else 15
    in_front_vp = numbers[2] if len(numbers) >= 3 else 20
    
    # Catch both angles if they exist
    angle1 = numbers[3] if len(numbers) >= 4 else 30  # usually theta (HP)
    angle2 = numbers[4] if len(numbers) >= 5 else 45  # usually phi (VP)

    # Simple routing flag check
    is_inclined_to_both = ("inclined to hp" in q_lower and "to vp" in q_lower) or len(numbers) >= 5

    xy_line_y = 150  
    scale = 3.5      # Slightly increased scale for visual clarity
    start_x = 120    

    start_fv_y = xy_line_y - (above_hp * scale)
    start_tv_y = xy_line_y + (in_front_vp * scale)

    if is_inclined_to_both:
        # --- THE MASTER LOCUS CALCULATIONS ---
        theta_rad = math.radians(angle1)
        phi_rad = math.radians(angle2)

        # 1. Component projection lengths (True lengths projected horizontally first)
        fv_component = tl * math.cos(theta_rad)  # Length of top view true length projection
        tv_component = tl * math.cos(phi_rad)    # Length of front view true length projection

        # 2. Locate Locus Depths from XY line
        locus_b_fv_y = start_fv_y - (tl * math.sin(theta_rad) * scale)
        locus_b_tv_y = start_tv_y + (tl * math.sin(phi_rad) * scale)

        # 3. Use Apparent Angle equations to find actual front/top view endpoint coordinates
        # Math trick: Apparent angles alpha and beta can be derived through projection alignment
        # Distance between projectors (d) calculation:
        try:
            # Solving for the visual convergence point along the X axis
            d = math.sqrt(abs((tv_component)**2 - (tl * math.sin(theta_rad))**2))
        except ValueError:
            d = tv_component * 0.8  # Safe fallback layout offset

        end_x = start_x + int(d * scale)
        end_fv_y = locus_b_fv_y
        end_tv_y = locus_b_tv_y

        # Calculated real view lengths
        fv_length = int(math.sqrt((end_x - start_x)**2 + (end_fv_y - start_fv_y)**2) / scale)
        tv_length = int(math.sqrt((end_x - start_x)**2 + (end_tv_y - start_tv_y)**2) / scale)

        case_title = "Projection of Line (Inclined to BOTH HP and VP - KTU Style)"
        steps = [
            "Draw the XY ground line.",
            f"Locate End A projections: a' ({above_hp}mm above XY) and a ({in_front_vp}mm below XY).",
            f"Draw the true inclination lines from a' ({angle1}° to HP) and a ({angle2}° to VP) to locate the Locus lines of B.",
            f"Draw horizontal Locus lines at Top View depth and Front View height.",
            f"Rotate true length projection lengths down using arcs to find final points b' and b on their respective Locus lines.",
            f"Connect a'b' for the Front View (Measured Apparent Length: {fv_length}mm).",
            f"Connect ab for the Top View (Measured Apparent Length: {tv_length}mm).",
            "Verify that b' and b lie perfectly on the same vertical projector line."
        ]

        # Dynamic SVG with Locus Lines
        svg_template = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="400" style="background-color: #ffffff; border: 1px solid #cccccc;">
            <line x1="40" y1="{locus_b_fv_y}" x2="540" y2="{locus_b_fv_y}" stroke="purple" stroke-dasharray="3" stroke-width="1" />
            <text x="545" y="{locus_b_fv_y + 4}" font-family="Arial" font-size="10" fill="purple">Locus of b'</text>
            <line x1="40" y1="{locus_b_tv_y}" x2="540" y2="{locus_b_tv_y}" stroke="purple" stroke-dasharray="3" stroke-width="1" />
            <text x="545" y="{locus_b_tv_y + 4}" font-family="Arial" font-size="10" fill="purple">Locus of b</text>
            
            <line x1="30" y1="{xy_line_y}" x2="550" y2="{xy_line_y}" stroke="black" stroke-width="2" />
            <text x="15" y="{xy_line_y + 5}" font-family="Arial" font-size="14" font-weight="bold">X</text>
            <text x="560" y="{xy_line_y + 5}" font-family="Arial" font-size="14" font-weight="bold">Y</text>
            
            <line x1="{start_x}" y1="{start_fv_y}" x2="{start_x}" y2="{start_tv_y}" stroke="gray" stroke-dasharray="4" />
            
            <line x1="{start_x}" y1="{start_fv_y}" x2="{end_x}" y2="{end_fv_y}" stroke="red" stroke-width="3" />
            <circle cx="{start_x}" cy="{start_fv_y}" r="4" fill="red" />
            <circle cx="{end_x}" cy="{end_fv_y}" r="4" fill="red" />
            <text x="{start_x - 18}" y="{start_fv_y - 5}" font-family="Arial" font-size="12" fill="red" font-weight="bold">a'</text>
            <text x="{end_x + 8}" y="{end_fv_y - 5}" font-family="Arial" font-size="12" fill="red" font-weight="bold">b'</text>
            
            <line x1="{start_x}" y1="{start_tv_y}" x2="{end_x}" y2="{end_tv_y}" stroke="blue" stroke-width="3" />
            <circle cx="{start_x}" cy="{start_tv_y}" r="4" fill="blue" />
            <circle cx="{end_x}" cy="{end_tv_y}" r="4" fill="blue" />
            <text x="{start_x - 15}" y="{start_tv_y + 15}" font-family="Arial" font-size="12" fill="blue" font-weight="bold">a</text>
            <text x="{end_x + 8}" y="{end_tv_y + 15}" font-family="Arial" font-size="12" fill="blue" font-weight="bold">b</text>
            
            <line x1="{end_x}" y1="{end_fv_y}" x2="{end_x}" y2="{end_tv_y}" stroke="gray" stroke-dasharray="4" />
        </svg>
        """
        
        return {
            "type": case_title,
            "parsed_dimensions": {
                "true_length_mm": tl,
                "theta_degrees": angle1,
                "phi_degrees": angle2,
                "end_A_above_HP_mm": above_hp,
                "end_A_in_front_VP_mm": in_front_vp
            },
            "calculated_data": {
                "apparent_front_view_length_mm": fv_length,
                "apparent_top_view_length_mm": tv_length
            },
            "steps": steps,
            "svg": svg_template.strip()
        }

    else:
        # --- Fallback: 1-Plane Inclination Code ---
        angle = angle1
        rad = math.radians(angle)
        if "to vp" in q_lower:
            fv_length = int(tl * math.cos(rad))
            tv_length = tl
            end_fv_x = start_x + fv_length * scale
            end_fv_y = start_fv_y
            end_tv_x = start_x + int(tl * math.cos(rad)) * scale
            end_tv_y = start_tv_y + int(tl * math.sin(rad)) * scale
            case_title = "Projection of Line (Inclined to VP)"
            steps = ["Draw XY line.", f"Locate a' and a.", f"Draw Top View (ab) at {angle}°."]
        else:
            fv_length = tl  
            tv_length = int(tl * math.cos(rad))  
            end_fv_x = start_x + int(tl * math.cos(rad)) * scale
            end_fv_y = start_fv_y - int(tl * math.sin(rad)) * scale  
            end_tv_x = start_x + tv_length * scale
            end_tv_y = start_tv_y  
            case_title = "Projection of Line (Inclined to HP)"
            steps = ["Draw XY line.", f"Locate a' and a.", f"Draw Front View (a'b') at {angle}°."]

        svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 550 350" width="100%" height="350" style="background-color: #ffffff; border: 1px solid #cccccc;"><line x1="30" y1="{xy_line_y}" x2="520" y2="{xy_line_y}" stroke="black" stroke-width="2" /><line x1="{start_x}" y1="{start_fv_y}" x2="{end_fv_x}" y2="{end_fv_y}" stroke="red" stroke-width="3" /><circle cx="{start_x}" cy="{start_fv_y}" r="4" fill="red" /><circle cx="{end_fv_x}" cy="{end_fv_y}" r="4" fill="red" /><line x1="{start_x}" y1="{start_tv_y}" x2="{end_tv_x}" y2="{end_tv_y}" stroke="blue" stroke-width="3" /><circle cx="{start_x}" cy="{start_tv_y}" r="4" fill="blue" /><circle cx="{end_tv_x}" cy="{end_tv_y}" r="4" fill="blue" /><line x1="{end_fv_x}" y1="{end_fv_y}" x2="{end_tv_x}" y2="{end_tv_y}" stroke="gray" stroke-dasharray="4" /></svg>"""
        return {"type": case_title, "parsed_dimensions": {"true_length_mm": tl, "angle_deg": angle}, "calculated_data": {"front_view_length_mm": fv_length, "top_view_length_mm": tv_length}, "steps": steps, "svg": svg_template.strip()} 