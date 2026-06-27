from fastapi import APIRouter
from solvers import utils, points, lines, planes, solids, sections, developments, isometric

router = APIRouter()

@router.post("/solve")
def solve_question(data: dict):
    question = data.get("question", "")
    
    # Parse parameters from natural language question
    params = utils.parse_question(question)
    params["raw_question"] = question # Pass raw text for advanced matching
    
    topic = params["topic"]
    
    # Route to the appropriate solver engine
    if topic == "isometric":
        result = isometric.solve(params)
    elif topic == "development":
        result = developments.solve(params)
    elif topic == "section":
        result = sections.solve(params)
    elif topic == "solid":
        result = solids.solve(params)
    elif topic == "plane":
        result = planes.solve(params)
    elif topic == "line":
        result = lines.solve(params)
    else:
        result = points.solve(params)
        
    return {
        "message": "Solution generated successfully",
        "result": result,
        "parsed_parameters": {
            "topic": params["topic"],
            "shape": params["shape"],
            "solid_type": params["solid_type"],
            "side_len_mm": params["side_len"],
            "length_mm": params["length"],
            "hp_angle_deg": params["hp_angle"],
            "vp_angle_deg": params["vp_angle"],
            "above_hp_mm": params["above_hp"],
            "in_front_vp_mm": params["in_front_vp"]
        }
    }