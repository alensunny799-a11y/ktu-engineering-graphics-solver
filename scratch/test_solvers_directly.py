import sys
import os

# Reconfigure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Add backend folder to path
sys.path.append(r"c:\Users\reena\Desktop\engineering-graphics-ai\backend")

from solvers import utils, lines

# Test questions
questions = [
    "End A of a line AB is 10mm above HP & 20mm in front of VP while its end B is 50mm above HP and 70mm in front of VP. The distance between end projectors of the line is 50mm. Draw projections and find true length, inclinations and traces.",
    "A line AB has its end A 10 mm above HP and 15 mm in front of VP. The end B is 50 mm above HP and 50 mm in front of VP. The distance between the end projectors is 50 mm."
]

for idx, q in enumerate(questions):
    print(f"\n--- Testing Question {idx+1} ---")
    print(q)
    params = utils.parse_question(q)
    params["raw_question"] = q
    print("Parsed Parameters:", {k: v for k, v in params.items() if k not in ["raw_numbers"]})
    result = lines.solve(params)
    print("Result Type:", result["type"])
    print("Given Data:", result["given_data"])
    print("Found Values:", result["found_values"])
    print("Steps count:", len(result["steps"]))
    print("SVG lines count:", len(result["svg"].splitlines()))
