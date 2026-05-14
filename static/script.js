/** 
 * Antigravity Calligraphy Studio
 * Logic for API interaction and UI reactivity
 */

const API_BASE = ""; // Relative to the host

// DOM Elements
const translitInput = document.getElementById('translit-input');
const generateBtn = document.getElementById('generate-btn');
const monogramImg = document.getElementById('monogram-img');
const imageFrame = document.getElementById('image-frame');
const previewPlaceholder = document.getElementById('preview-placeholder');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const predClass = document.getElementById('pred-class');
const confLevel = document.getElementById('conf-level');
const confText = document.getElementById('conf-text');
const predictionResults = document.getElementById('prediction-results');

// Status Elements
const modelDot = document.getElementById('model-dot');
const modelStatus = document.getElementById('model-status');
const datasetSizeEl = document.getElementById('dataset-size');
const classesCountEl = document.getElementById('classes-count');

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    updateSystemStatus();
    setInterval(updateSystemStatus, 5000); // Check status every 5 seconds
});

// --- API Calls ---

async function updateSystemStatus() {
    try {
        const resp = await fetch(`${API_BASE}/status`);
        const data = await resp.json();

        // Update UI
        if (data.model_exists) {
            modelDot.classList.add('online');
            modelStatus.textContent = "Loaded & Ready";
        } else {
            modelDot.classList.remove('online');
            modelStatus.textContent = "Not Trained";
        }

        datasetSizeEl.textContent = `${data.dataset_size.toLocaleString()} images`;
        classesCountEl.textContent = data.classes_count;

    } catch (err) {
        console.error("Failed to fetch status:", err);
    }
}

async function generateCalligraphy() {
    const text = translitInput.value.trim();
    if (!text) return;

    generateBtn.textContent = "Crafting...";
    generateBtn.disabled = true;

    const payload = {
        text: text,
        font_size: parseInt(document.getElementById('font-size').value),
        fg_color: document.getElementById('fg-color').value,
        bg_color: document.getElementById('bg-color').value,
        vertical: document.getElementById('vertical-toggle').checked
    };

    try {
        const resp = await fetch(`${API_BASE}/monogram`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error("Generation failed");

        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        
        monogramImg.src = url;
        imageFrame.classList.remove('hidden');
        previewPlaceholder.classList.add('hidden');

    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        generateBtn.textContent = "Generate Masterpiece";
        generateBtn.disabled = false;
    }
}

async function predictImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const resp = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            body: formData
        });

        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        // Update UI
        predClass.textContent = data.devanagari || data.predicted_class;
        const confPerc = (data.confidence * 100).toFixed(1);
        confLevel.style.width = `${confPerc}%`;
        confText.textContent = `${confPerc}% Confident`;
        
        predictionResults.classList.remove('hidden');

    } catch (err) {
        alert("Prediction Error: " + err.message);
    }
}

// --- Event Listeners ---

generateBtn.addEventListener('click', generateCalligraphy);

// Drag and Drop Logic
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('active');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('active'));

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    if (e.dataTransfer.files.length) {
        predictImage(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        predictImage(e.target.files[0]);
    }
});

// Admin Button Logic
document.getElementById('gen-data-btn').addEventListener('click', async () => {
    if (confirm("Regenerate dataset? This will take a few minutes.")) {
        await fetch(`${API_BASE}/generate`, { method: 'POST' });
        showJobStatus("Generating Data...");
    }
});

document.getElementById('train-model-btn').addEventListener('click', async () => {
    if (confirm("Start training the model?")) {
        await fetch(`${API_BASE}/train`, { method: 'POST' });
        showJobStatus("Training Model...");
    }
});

function showJobStatus(msg) {
    const el = document.getElementById('job-status');
    el.textContent = msg;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 5000);
}
