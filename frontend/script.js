// API Configuration
// Change DEPLOYED_API_URL to your Render web service URL (e.g. "https://your-app.onrender.com") when deployed
const DEPLOYED_API_URL = "";
const API_BASE_URL = DEPLOYED_API_URL || "http://127.0.0.1:8000";

let currentTopic = 'point';
let currentStepIndex = 1;
let totalStepsCount = 0;
let autoPlayInterval = null;

// Syllabus Templates data
const templates = {
    point: [
        { text: "Point A is 20mm above HP and 30mm in front of VP. Draw its projections.", side: 20, length: 0, hp: 20, vp: 30 },
        { text: "Point B is 35mm above HP and 25mm behind VP. Draw its projections.", side: 35, length: 0, hp: 35, vp: 25 },
        { text: "Point C is 40mm below HP and 30mm behind VP. Draw its projections.", side: 40, length: 0, hp: 40, vp: 30 },
        { text: "Point D is 25mm below HP and 45mm in front of VP. Draw its projections." , side: 25, length: 0, hp: 25, vp: 45 }
    ],
    line: [
        { text: "A line AB 70mm long has its end A 15mm above HP and 20mm in front of VP. The line is inclined at 30 degrees to HP and 45 degrees to VP. Draw its projections.", side: 0, length: 70, hp: 30, vp: 45 },
        { text: "A line PQ 80mm long is inclined at 45 degrees to HP and parallel to VP. Its end P is 20mm above HP and 25mm in front of VP.", side: 0, length: 80, hp: 45, vp: 0 },
        { text: "A line EF 75mm long has its end E 20mm above HP and 15mm in front of VP. The line is inclined at 40 degrees to VP and parallel to HP.", side: 0, length: 75, hp: 0, vp: 40 },
        { text: "A line RS 65mm long is parallel to both HP and VP. It is 25mm above HP and 30mm in front of VP.", side: 0, length: 65, hp: 0, vp: 0 }
    ],
    plane: [
        { text: "A pentagonal lamina of 30mm side has one of its edges on HP. The surface is inclined at 45 degrees to HP and the resting edge is inclined at 30 degrees to VP.", side: 30, length: 0, hp: 45, vp: 30 },
        { text: "A square plate of side 35mm rests on one of its sides on HP. The plate is inclined at 40 degrees to HP and the resting side is inclined at 30 degrees to VP.", side: 35, length: 0, hp: 40, vp: 30 },
        { text: "A regular hexagonal lamina of side 25mm has one of its edges on HP. The lamina is inclined at 45 degrees to HP and the resting edge is inclined at 30 degrees to VP.", side: 25, length: 0, hp: 45, vp: 30 },
        { text: "An equilateral triangular lamina of 30mm side rests on HP with one of its edges. The surface is inclined at 45 degrees to HP and the resting edge is inclined at 30 degrees to VP.", side: 30, length: 0, hp: 45, vp: 30 },
        { text: "A circular lamina of 40mm diameter has its surface inclined at 45 degrees to HP and its diameter is inclined at 30 degrees to VP.", side: 40, length: 0, hp: 45, vp: 30 }
    ],
    solid: [
        { text: "A square prism of base side 30mm and axis length 65mm rests on HP with one of its base edges. Its axis is inclined at 45 degrees to HP and the resting edge is inclined at 30 degrees to VP.", side: 30, length: 65, hp: 45, vp: 30 },
        { text: "A pentagonal pyramid of base side 30mm and axis length 65mm rests on HP with one of its base edges, and its axis is inclined at 45 degrees to HP.", side: 30, length: 65, hp: 45, vp: 0 },
        { text: "A cylinder of base diameter 40mm and axis length 65mm rests on HP with its base circle, with its axis inclined at 45 degrees to HP.", side: 40, length: 65, hp: 45, vp: 0 },
        { text: "A cone of base diameter 40mm and axis length 65mm rests on HP on a point of its base circle, with its axis inclined at 45 degrees to HP.", side: 40, length: 65, hp: 45, vp: 0 }
    ],
    section: [
        { text: "A square pyramid of base side 35mm and axis length 65mm rests on HP with its base. It is cut by a section plane perpendicular to VP and inclined at 45 degrees to HP, passing through a point on the axis 30mm from the base.", side: 35, length: 65, hp: 45, vp: 0 }
    ],
    development: [
        { text: "A square prism of base side 30mm and axis length 65mm rests on HP with its base. It is cut by a section plane inclined at 30 degrees to HP. Draw the development of its lateral surface.", side: 30, length: 65, hp: 30, vp: 0 },
        { text: "A square pyramid of base side 30mm and axis height 65mm rests on HP on its base. Draw the radial development of its lateral surface.", side: 30, length: 65, hp: 0, vp: 0 }
    ],
    isometric: [
        { text: "Draw the isometric view of a square prism of base side 40mm and height 60mm resting vertically on its base.", side: 40, length: 60, hp: 0, vp: 0 },
        { text: "Draw the isometric projection of a square pyramid of base side 40mm and height 60mm resting vertically on its base.", side: 40, length: 60, hp: 0, vp: 0 }
    ]
};

// Initialize app
window.addEventListener('DOMContentLoaded', () => {
    loadSelectedTemplate();
});

function loadSelectedTemplate() {
    const val = document.getElementById('template-select').value;
    const parts = val.split('-');
    const topic = parts[0];
    const index = parseInt(parts[1]) - 1;
    
    currentTopic = topic;
    
    const tpl = templates[topic][index];
    if (tpl) {
        loadTemplate(tpl);
    }
}

function loadTemplate(tpl) {
    document.getElementById('question-input').value = tpl.text;
    
    // Configure slider visibilities and limits first
    configureSlidersForTopic(currentTopic);
    
    if (tpl.side !== undefined) document.getElementById('slider-side').value = tpl.side;
    if (tpl.length !== undefined) document.getElementById('slider-length').value = tpl.length;
    if (tpl.hp !== undefined) document.getElementById('slider-hp-angle').value = tpl.hp;
    if (tpl.vp !== undefined) document.getElementById('slider-vp-angle').value = tpl.vp;

    updateSliders(false); // Update numbers without modifying the text area
}

function configureSlidersForTopic(topic) {
    const sSide = document.getElementById('slider-side');
    const sLength = document.getElementById('slider-length');
    const sHP = document.getElementById('slider-hp-angle');
    const sVP = document.getElementById('slider-vp-angle');

    const lblSide = sSide.parentElement.querySelector('.slider-label span:first-child');
    const lblLength = sLength.parentElement.querySelector('.slider-label span:first-child');
    const lblHP = sHP.parentElement.querySelector('.slider-label span:first-child');
    const lblVP = sVP.parentElement.querySelector('.slider-label span:first-child');

    // Show all by default
    sSide.parentElement.style.display = 'flex';
    sLength.parentElement.style.display = 'flex';
    sHP.parentElement.style.display = 'flex';
    sVP.parentElement.style.display = 'flex';

    if (topic === 'point') {
        lblSide.innerText = "Above/Below HP";
        lblLength.innerText = "In Front/Behind VP";
        sHP.parentElement.style.display = 'none';
        sVP.parentElement.style.display = 'none';
        
        sSide.min = 5; sSide.max = 80;
        sLength.min = 5; sLength.max = 80;
    } 
    else if (topic === 'line') {
        lblSide.innerText = "End A Above HP";
        lblLength.innerText = "True Length";
        lblHP.innerText = "HP Inclination (θ)";
        lblVP.innerText = "VP Inclination (φ)";
        
        sSide.min = 5; sSide.max = 50;
        sLength.min = 40; sLength.max = 120;
    }
    else if (topic === 'plane') {
        lblSide.innerText = "Side Length / Diam.";
        sLength.parentElement.style.display = 'none';
        lblHP.innerText = "Surface Inclination (θ)";
        lblVP.innerText = "Edge Inclination (φ)";
        
        sSide.min = 15; sSide.max = 60;
    }
    else if (topic === 'solid') {
        lblSide.innerText = "Base Side / Diameter";
        lblLength.innerText = "Axis Length";
        lblHP.innerText = "Axis Inclination (θ)";
        lblVP.innerText = "VP Inclination (φ)";
        sVP.parentElement.style.display = 'flex';
        
        sSide.min = 15; sSide.max = 50;
        sLength.min = 40; sLength.max = 100;
    }
    else if (topic === 'section' || topic === 'development') {
        lblSide.innerText = "Base Side / Diameter";
        lblLength.innerText = "Axis Length";
        lblHP.innerText = "Cutting Angle";
        sVP.parentElement.style.display = 'none';
        
        sSide.min = 20; sSide.max = 50;
        sLength.min = 40; sLength.max = 100;
    }
    else if (topic === 'isometric') {
        lblSide.innerText = "Base Side";
        lblLength.innerText = "Height";
        sHP.parentElement.style.display = 'none';
        sVP.parentElement.style.display = 'none';
        
        sSide.min = 20; sSide.max = 60;
        sLength.min = 30; sLength.max = 100;
    }
}

function updateSliders(reconstructText = true) {
    const side = document.getElementById('slider-side').value;
    const length = document.getElementById('slider-length').value;
    const hp = document.getElementById('slider-hp-angle').value;
    const vp = document.getElementById('slider-vp-angle').value;

    document.getElementById('val-side').innerText = side + "mm";
    document.getElementById('val-length').innerText = length + "mm";
    document.getElementById('val-hp-angle').innerText = hp + "°";
    document.getElementById('val-vp-angle').innerText = vp + "°";

    if (reconstructText) {
        // Build a dynamic text statement matching the selected slider parameters
        reconstructQuestionStatement(side, length, hp, vp);
    }
}

function reconstructQuestionStatement(side, length, hp, vp) {
    let text = "";
    if (currentTopic === 'point') {
        text = `Point A is ${side}mm above HP and ${length}mm in front of VP. Draw its projections.`;
    } 
    else if (currentTopic === 'line') {
        text = `A line AB ${length}mm long has its end A ${side}mm above HP and 20mm in front of VP. The line is inclined at ${hp} degrees to HP and ${vp} degrees to VP. Draw its projections.`;
    }
    else if (currentTopic === 'plane') {
        text = `A pentagonal lamina of ${side}mm side has one of its edges on HP. The surface is inclined at ${hp} degrees to HP and the resting edge is inclined at ${vp} degrees to VP.`;
    }
    else if (currentTopic === 'solid') {
        text = `A square prism of base side ${side}mm and axis length ${length}mm rests on HP with one of its base edges. Its axis is inclined at ${hp} degrees to HP and the resting edge is inclined at ${vp} degrees to VP.`;
    }
    else if (currentTopic === 'section') {
        text = `A square pyramid of base side ${side}mm and axis length ${length}mm rests on HP with its base. It is cut by a section plane perpendicular to VP and inclined at ${hp} degrees to HP, passing through a point on the axis 30mm from the base.`;
    }
    else if (currentTopic === 'development') {
        text = `A square prism of base side ${side}mm and axis length ${length}mm rests on HP with its base. It is cut by a section plane inclined at ${hp} degrees to HP. Draw the development of its lateral surface.`;
    }
    else if (currentTopic === 'isometric') {
        text = `Draw the isometric view of a square prism of base side ${side}mm and height ${length}mm resting vertically on its base.`;
    }
    document.getElementById('question-input').value = text;
}

async function submitQuestion() {
    const questionText = document.getElementById("question-input").value.trim();
    if (!questionText) {
        alert("Please enter a question statement first!");
        return;
    }

    // Stop autoplay
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        document.getElementById('play-btn').innerText = "▶";
    }

    const caseTitle = document.getElementById("case-title");
    const stepsList = document.getElementById("steps-list");
    const drawingArea = document.getElementById("drawing-area");
    const metaContainer = document.getElementById("meta-container");
    const givenBox = document.getElementById("given-data-box");
    const foundBox = document.getElementById("found-values-box");
    const animControls = document.getElementById("animation-controls");

    stepsList.innerHTML = "<li class='active'>Solving projection geometry algorithms...</li>";
    drawingArea.innerHTML = "<span style='color:#a1a1aa;'>Compiling vector node parameters...</span>";
    metaContainer.style.display = "none";
    animControls.style.display = "none";

    try {
        const response = await fetch(`${API_BASE_URL}/solve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: questionText })
        });

        const data = await response.json();
        const result = data.result;

        caseTitle.innerText = result.type;

        // Render steps
        stepsList.innerHTML = "";
        result.steps.forEach((step, index) => {
            const li = document.createElement("li");
            li.id = `text-step-${index + 1}`;
            li.innerText = step;
            stepsList.appendChild(li);
        });

        // Insert SVG drawing
        drawingArea.innerHTML = result.svg || "";

        // Fill metadata
        if (result.given_data && result.found_values) {
            givenBox.innerHTML = result.given_data;
            foundBox.innerHTML = result.found_values;
            metaContainer.style.display = "grid";
        }

        // Setup player step range
        setupInteractiveDrawing(result.steps.length);

    } catch (error) {
        console.error("Endpoint connect failure:", error);
        stepsList.innerHTML = `<span style='color:#ef4444;'>Connection error. Make sure your server at ${API_BASE_URL} is running!</span>`;
        drawingArea.innerHTML = "<span style='color:#ef4444;'>Draw server offline.</span>";
    }
}

function setupInteractiveDrawing(totalSteps) {
    currentStepIndex = 1; 
    totalStepsCount = totalSteps;
    
    document.getElementById("animation-controls").style.display = "flex";
    
    const svgEl = document.querySelector("#drawing-area svg");
    if (!svgEl) return;

    // Map children nodes that don't have explicit step assignments
    Array.from(svgEl.children).forEach(child => {
        if (child.hasAttribute("data-step")) return;
        
        // Simple fallback
        const tag = child.tagName;
        if (tag === "line") child.setAttribute("data-step", "1");
        else if (tag === "text") child.setAttribute("data-step", "1");
        else child.setAttribute("data-step", "2");
    });
}