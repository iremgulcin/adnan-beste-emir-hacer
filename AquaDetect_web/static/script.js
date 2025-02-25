document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('videoFile');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload video
        const uploadResponse = await fetch('http://0.0.0.0:8000/upload/', {
            method: 'POST',
            body: formData
        });
        const uploadData = await uploadResponse.json();

        // Show processing status
        document.getElementById('processingStatus').classList.remove('d-none');

        // Process video
        const processResponse = await fetch(`http://0.0.0.0:8000/process/${uploadData.video_id}`);
        const processData = await processResponse.json();

        // Fetch detections
        const detectionsResponse = await fetch(`http://0.0.0.0:8000/detections/${uploadData.video_id}`);
        const detectionsData = await detectionsResponse.json();

        // Process detections for display
        const detectionCounts = {};
        const detectionConfidences = {};

        detectionsData.detections.forEach(detection => {
            if (!detectionCounts[detection.animal_type]) {
                detectionCounts[detection.animal_type] = 0;
                detectionConfidences[detection.animal_type] = [];
            }
            detectionCounts[detection.animal_type]++;
            detectionConfidences[detection.animal_type].push(detection.confidence);
        });

        // Update the table
        const tbody = document.getElementById('detectionsBody');
        tbody.innerHTML = '';

        Object.keys(detectionCounts).forEach(animal => {
            const avgConfidence = (detectionConfidences[animal].reduce((a, b) => a + b, 0) /
                                 detectionConfidences[animal].length * 100).toFixed(1);

            const row = `
                <tr class="animal-row" data-species="${animal}">
                    <td>${animal}</td>
                    <td>${detectionCounts[animal]}</td>
                    <td>${avgConfidence}%</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });

        // Add click handlers for the animal rows
        document.querySelectorAll('.animal-row').forEach(row => {
            row.addEventListener('click', async () => {
                const species = row.dataset.species;
                try {
                    const response = await fetch(`http://0.0.0.0:8000/animal-info/${species}`);
                    const animalInfo = await response.json();

                    // Update the info panel
                    const infoPanel = document.getElementById('animalInfo');
                    infoPanel.querySelector('.animal-name').textContent = animalInfo.species_name;
                    infoPanel.querySelector('.common-name').textContent = animalInfo.common_name;
                    infoPanel.querySelector('.description').textContent = animalInfo.description;
                    infoPanel.querySelector('.threat-level').textContent = animalInfo.threat_level;
                    infoPanel.querySelector('.habitat').textContent = animalInfo.habitat;
                } catch (error) {
                    console.error('Error fetching animal info:', error);
                }
            });
        });

        // Hide processing status
        document.getElementById('processingStatus').classList.add('d-none');

        // Show video player and update video source
        const videoPlayer = document.getElementById('videoPlayer');
        videoPlayer.classList.remove('d-none');
        const video = videoPlayer.querySelector('video');
        video.src = processData.video_url;  // Use the video URL from the response
        video.load();
        video.play();

    } catch (error) {
        alert('An error occurred: ' + error.message);
        document.getElementById('processingStatus').classList.add('d-none');
    }
});