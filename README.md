# KTU Engineering Graphics AI Solver 📐🚀

An advanced CAD-like vector drawing solver built specifically for the **APJ Abdul Kalam Technological University (KTU)** Engineering Graphics curriculum (Course Code: EST 110 / GMEST 103). 

This application parses natural language engineering drawing questions (e.g. projections of points, lines, planes, solids, section views, lateral developments, and isometric projections) and dynamically generates step-by-step orthographic and isometric vector projections (SVG).

---

## 🌟 Core Features

- **📍 Projection of Points**: Supports 1st, 2nd, 3rd, and 4th quadrant point projections with automatic reference line placement.
- **📏 Projection of Lines**: Solves lines parallel/inclined to HP, VP, or both reference planes. Computes true lengths, apparent lengths (plan/elevation), and apparent angles ($\alpha, \beta$) with locus lines.
- **📐 Projection of Planes**: Dynamically calculates and renders projections for regular polygons (Triangle, Square, Rectangle, Pentagon, Hexagon, Circle) resting on edge/corner under dual inclinations.
- **📦 Projection of Solids**: Computes orthographic projections of simple solids (Prisms, Pyramids, Cylinder, Cone) with axis inclined to HP/VP, detailing visible and hidden (dashed) edges.
- **✂️ Sections of Solids**: Projects section cuts by Auxiliary Inclined Planes (AIP) at custom heights/angles. Renders the Sectional Top View and projects the True Shape of the Section onto an auxiliary $X_1 Y_1$ plane.
- **🗺️ Development of Surfaces**: Computes flat layouts using Parallel Line Development (prisms/cylinders) or Radial Line Development (pyramids/cones) with mapped section cut curves.
- **🌐 Isometric Projections**: Generates 30-degree isometric views (true scale) and isometric projections (isometric scale 0.82) of regular solids.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.x), Uvicorn (Asynchronous server).
- **Frontend**: Modern vanilla HTML5, CSS3 (dark-mode glassmorphic theme), and ES6+ JavaScript.
- **Drawing Engine**: Dynamic math coordinate solvers exporting pure SVG vectors with interactive step-by-step playback transitions.

---

## 🚀 How to Run the Project Locally

### 1. Start the Backend Server
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
3. Install dependencies (if not done):
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   python app.py
   ```
   *The server will start running on `http://127.0.0.1:8000`.*

### 2. View the Frontend
Simply open the `frontend/index.html` file in any modern web browser:
- You can double-click `index.html` inside the `frontend/` folder.
- Or open it directly as a file URI: `file:///path/to/frontend/index.html`.

---

## 🎥 Interactive Player & Controls

- **Interactive Sliders**: Adjust dimensions, height, and inclination angles dynamically; the natural language problem statement adapts automatically.
- **Step-by-Step Player**: Play, pause, or skip through the drafting steps. Each step highlights the matching instruction in the procedure panel and animates the corresponding vectors on the canvas.
