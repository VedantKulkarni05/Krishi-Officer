document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const modeBtns = document.querySelectorAll('.mode-btn');
    const imageSection = document.getElementById('imageSection');
    const textSection = document.getElementById('textSection');
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImageBtn = document.getElementById('removeImage');
    const textInput = document.getElementById('textInput');
    const diagnoseBtn = document.getElementById('diagnoseBtn');
    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    const resultsContent = document.getElementById('resultsContent');

    let currentMode = 'image';
    let selectedFile = null;

    // Mode Toggle
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            currentMode = mode;

            // Update button states
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Toggle sections
            if (mode === 'image') {
                imageSection.style.display = 'block';
                textSection.style.display = 'none';
            } else {
                imageSection.style.display = 'none';
                textSection.style.display = 'block';
            }
        });
    });

    // Upload Area Click
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    // File Input Change
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageUpload(file);
        }
    });

    // Drag and Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageUpload(file);
        }
    });

    // Handle Image Upload
    function handleImageUpload(file) {
        selectedFile = file;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadPlaceholder.style.display = 'none';
            imagePreview.style.display = 'block';
        };
        
        reader.readAsDataURL(file);
    }

    // Remove Image
    removeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        imageInput.value = '';
        uploadPlaceholder.style.display = 'flex';
        imagePreview.style.display = 'none';
        previewImg.src = '';
    });

    // Diagnose Button
    diagnoseBtn.addEventListener('click', () => {
        if (currentMode === 'image' && !selectedFile) {
            alert('Please upload an image first');
            return;
        }

        if (currentMode === 'text' && !textInput.value.trim()) {
            alert('Please describe the issue first');
            return;
        }

        // Show loading state
        diagnoseBtn.disabled = true;
        diagnoseBtn.innerHTML = '<span>⏳</span> Analyzing...';

        // Simulate API call (replace with actual API call)
        setTimeout(() => {
            showResults();
            diagnoseBtn.disabled = false;
            diagnoseBtn.innerHTML = '<span>🔍</span> Diagnose';
        }, 2000);
    });

    // Show Results
    function showResults() {
        resultsPlaceholder.style.display = 'none';
        resultsContent.style.display = 'block';

        // Demo results (replace with actual API response)
        resultsContent.innerHTML = `
            <div class="result-item">
                <h3 class="result-title">🪲 Detected Pest</h3>
                <p class="result-text">Based on the analysis, this appears to be <strong>Aphids</strong> affecting your crop.</p>
            </div>
            <div class="result-item">
                <h3 class="result-title">📋 Symptoms</h3>
                <p class="result-text">Yellowing leaves, sticky residue on leaves, curled or distorted leaves.</p>
            </div>
            <div class="result-item">
                <h3 class="result-title">💡 Recommended Treatment</h3>
                <p class="result-text">
                    1. Spray neem oil solution (2-3 tablespoons per liter of water)<br>
                    2. Introduce natural predators like ladybugs<br>
                    3. Remove heavily infested leaves<br>
                    4. Apply insecticidal soap if infestation is severe
                </p>
            </div>
            <div class="result-item">
                <h3 class="result-title">⚠️ Prevention Tips</h3>
                <p class="result-text">
                    • Regularly inspect plants for early signs<br>
                    • Maintain proper plant spacing for air circulation<br>
                    • Avoid over-fertilizing with nitrogen<br>
                    • Keep the garden clean and weed-free
                </p>
            </div>
        `;
    }
});
