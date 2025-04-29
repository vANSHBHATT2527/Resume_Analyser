document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    const resultsSection = document.getElementById('resultsSection');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Configure marked options
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });

    // Drag and drop functionality
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#2980b9';
        uploadBox.style.backgroundColor = '#f8f9fa';
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#3498db';
        uploadBox.style.backgroundColor = 'white';
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#3498db';
        uploadBox.style.backgroundColor = 'white';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // File input change handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file');
            return;
        }

        const formData = new FormData();
        formData.append('resume', file);

        // Show loading overlay
        loadingOverlay.style.display = 'flex';
        resultsSection.style.display = 'none';

        // Send file to backend
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI with results
            document.getElementById('resumeScore').textContent = data.score || 'N/A';
            document.getElementById('extractedName').textContent = data.name || 'Not found';
            document.getElementById('extractedEmail').textContent = data.email || 'Not found';
            document.getElementById('extractedPhone').textContent = data.phone || 'Not found';
            
            // Update analysis with markdown support
            const analysisContent = document.getElementById('resumeAnalysis');
            if (data.analysis) {
                analysisContent.innerHTML = marked.parse(data.analysis);
                // Apply syntax highlighting to any code blocks
                analysisContent.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            } else {
                analysisContent.innerHTML = '<p>No analysis available</p>';
            }
            
            // Update course recommendations
            const recommendationsContent = document.getElementById('courseRecommendations');
            if (data.recommendations) {
                recommendationsContent.innerHTML = data.recommendations.map(course => 
                    `<div class="course-item">
                        <h4>${course.title || 'Untitled Course'}</h4>
                        <p>${course.description || 'No description available'}</p>
                        <a href="${course.link || '#'}" target="_blank" class="course-link">Learn More</a>
                    </div>`
                ).join('');
            } else {
                recommendationsContent.innerHTML = '<p>No course recommendations available.</p>';
            }

            // Show results section
            resultsSection.style.display = 'grid';
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || 'An error occurred while analyzing your resume. Please try again.');
        })
        .finally(() => {
            // Hide loading overlay
            loadingOverlay.style.display = 'none';
        });
    }
}); 