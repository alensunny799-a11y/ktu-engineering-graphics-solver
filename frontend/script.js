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