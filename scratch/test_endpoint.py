import urllib.request
import json
import sys

def test_endpoint(question):
    url = "http://127.0.0.1:8000/solve"
    data = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode())
            print(f"PASS: {question[:40]}...")
            return True
    except Exception as e:
        print(f"FAIL: {question[:40]}... Error: {e}")
        return False

# List of test questions from each category
test_cases = [
    "Point A is 20mm above HP and 30mm in front of VP.",
    "A line AB 70mm long has its end A 15mm above HP and 20mm in front of VP. The line is inclined at 30 degrees to HP and 45 degrees to VP.",
    "End A of a line AB is 10mm above HP & 20mm in front of VP while its end B is 50mm above HP and 70mm in front of VP. The distance between end projectors of the line is 50mm. Draw projections and find true length, inclinations and traces.",
    "A regular hexagonal lamina of side 25mm has one of its edges on HP. The lamina is inclined at 45 degrees to HP and the resting edge is inclined at 30 degrees to VP.",
    "A square prism of base side 30mm and axis length 65mm rests on HP with one of its base edges, and its axis is inclined at 45 degrees to HP.",
    "A square pyramid of base side 35mm and axis length 65mm rests on HP with its base. It is cut by a section plane perpendicular to VP and inclined at 45 degrees to HP, passing through a point on the axis 30mm from the base.",
    "A square prism of base side 30mm and axis length 65mm rests on HP with its base. It is cut by a section plane inclined at 30 degrees to HP. Draw the development of its lateral surface.",
    "Draw the isometric view of a square prism of base side 40mm and height 60mm resting vertically on its base."
]

print("Running endpoint verification tests...")
all_passed = True
for tc in test_cases:
    if not test_endpoint(tc):
        all_passed = False

if all_passed:
    print("\nAll solver tests completed successfully!")
    sys.exit(0)
else:
    print("\nSome tests failed. Check backend logs.")
    sys.exit(1)
