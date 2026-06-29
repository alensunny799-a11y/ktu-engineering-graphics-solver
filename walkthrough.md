# KTU Engineering Graphics Solver Walkthrough

We have successfully completed the implementation of textbook-compliant projections and drawing steps.

## What Was Refactored

### 1. 3-Stage Solid Projections
- We updated [solids.py](backend/solvers/solids.py) to support the full **three-stage orthographic projection** (6 views) when the solid's axis is inclined to both planes (HP and VP).
  - **Stage 1 (Left)**: Simple position standing vertically on HP, with base corners oriented (resting on corner or edge).
  - **Stage 2 (Middle)**: Front View and Top View with the axis inclined to HP (rotated around X-axis by $90 - \theta_{hp}$).
  - **Stage 3 (Right)**: Final Front View and Top View with the axis/resting edge inclined to VP (rotated around the vertical Y-axis by $\phi_{vp}$).
- Added projection transfer paths:
  - **Horizontal Projectors (2H)** transferring height levels from Stage 2 Front View to Stage 3 Front View.
  - **Vertical Projectors (2H)** connecting Stage 3 Top View and Stage 3 Front View.
- Configured dynamic visibility: visible boundaries use thick solid outlines (**HB**), and back-facing/hidden edges use thin dashed paths (**H/HB**).

### 2. Robust Semantic Question Parser
- We rewrote `parse_question` in [utils.py](backend/solvers/utils.py) using contextual regular expressions.
- It maps distance parameters (`above HP` / `in front of VP`) and dimensions (`base side` / `axis length`) based on semantic keyword association instead of simple sequence order.
- Corrected the Point coordinates mapping, so `20mm above HP and 30mm in front of VP` binds exactly to `above_hp = 20` and `in_front_vp = 30`.

### 3. Frontend Slider & Templates
- Enabled the **VP Inclination (φ)** slider for solids inside [script.js](frontend/script.js).
- Added a new default solid template for a prism inclined to both planes: *Inclined at 45° to HP and 30° to VP*.
- Configured the dynamic problem text generator to incorporate both inclination angles when tweaking sliders.

### 4. Distance between End Projectors (DEP) Lines & Traces
- Added a dedicated solver pathway for DEP problems in [lines.py](backend/solvers/lines.py).
- Implemented mathematically exact true length ($TL = \sqrt{dep^2 + (hb - ha)^2 + (db - da)^2}$), true inclinations ($\theta = \arcsin((hb - ha)/TL)$, $\phi = \arcsin((db - da)/TL)$), and apparent angles ($\alpha, \beta$).
- Computes vertical/horizontal traces ($VT, HT$) using collinear projection equations.
- Configured SVG output with 2H, H, HB pencil style paths:
  - Red thick Front View ($a'b'$), Blue thick Top View ($ab$) (HB pencil).
  - Gray loci ($a', a, b', b$) and projector guidelines (2H pencil).
  - Pink and Purple rotation arcs and projection lines showing the Rotating Line Method.
  - Dashed trace extensions and vertical trace projection lines (2H pencil).
  - Clear labels for points $a', a, b', b, b_1', b_1, b_2', b_2, h', v, HT, VT$.

---

## Verification Results

All 8 test cases in the verification script [test_endpoint.py](scratch/test_endpoint.py) passed successfully. The backend is running and listening on `http://127.0.0.1:8000`.
