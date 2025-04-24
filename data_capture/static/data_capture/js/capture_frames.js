const startButton = document.getElementById('start-button');
const stopButton = document.getElementById('stop-button');
const modal = document.getElementById('modal');
const videoStream = document.getElementById('video-stream');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
let stream;
let frameInterval;
let detectionStatusDiv = document.getElementById('detection-status');

let selectedCameraUrl = null;

const cameraSelectInputs = document.querySelectorAll('.camera-select');
cameraSelectInputs.forEach(input => {
  input.addEventListener('change', (event) => {
    selectedCameraUrl = event.target.getAttribute('data-url');
    console.log("Cámara seleccionada: " + selectedCameraUrl);
  });
});

startButton.addEventListener('click', async function() {
  try {
    if (selectedCameraUrl === "default") {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      videoStream.srcObject = stream;
      videoStream.play();
      modal.style.display = "block";

      frameInterval = setInterval(captureFrame, 400);
    } else if (selectedCameraUrl) {
      videoStream.src = selectedCameraUrl;
      videoStream.load();

      videoStream.onloadeddata = function() {
        modal.style.display = "block";

        frameInterval = setInterval(captureFrame, 400);
      };

      videoStream.onerror = function() {
        alert("La cámara seleccionada no está conectada o no responde.");
        stopStreaming();
      };

    } else {
      alert("Por favor, selecciona una cámara primero.");
    }
  } catch (error) {
    console.error("Error al acceder a la cámara: ", error);
    alert("Error al acceder a la cámara.");
  }
});

stopButton.addEventListener('click', function() {
  stopStreaming();
});

function captureFrame() {
  context.drawImage(videoStream, 0, 0, canvas.width, canvas.height);
  const frameData = canvas.toDataURL('image/jpeg');

  fetch(detectFightUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}'
    },
    body: JSON.stringify({ image: frameData })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Frame enviado exitosamente:', data);
    if (data.status) {
      if(data.detection_message == "Sin anomalías."){
        detectionStatusDiv.textContent = data.detection_message;  
        detectionStatusDiv.style.color = "green"
      }else{
        detectionStatusDiv.textContent = data.detection_message; 
        detectionStatusDiv.style.color = "red"
      }
    } else if (data.error) {
      detectionStatusDiv.textContent = `Error: ${data.error}`; 
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function stopStreaming() {
  clearInterval(frameInterval);
  modal.style.display = "none";
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
}



const openModalButton = document.getElementById('open-modal');
const anomalyModal = document.getElementById('anomaly-modal');
const confirmSelectionButton = document.getElementById('confirm-selection');
const closeModalButton = document.getElementById('close-modal');

function loadSelectedAnomalies() {
  const savedAnomalies = JSON.parse(localStorage.getItem('selectedAnomalies')) || ["agglomeration", "fight_detected", "fire_detected"];
  document.querySelectorAll('.anomaly-checkbox').forEach(checkbox => {
    checkbox.checked = savedAnomalies.includes(checkbox.value);
  });
}

openModalButton.addEventListener('click', () => {
  loadSelectedAnomalies();
  anomalyModal.classList.remove('hidden');
});

closeModalButton.addEventListener('click', () => {
  anomalyModal.classList.add('hidden');
});

confirmSelectionButton.addEventListener('click', () => {
  const selectedAnomalies = [];
  document.querySelectorAll('.anomaly-checkbox:checked').forEach(checkbox => {
    selectedAnomalies.push(checkbox.value);
  });

  if (selectedAnomalies.length > 0) {
    localStorage.setItem('selectedAnomalies', JSON.stringify(selectedAnomalies));

    fetch(setAnomaliesUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token }}'
      },
      body: JSON.stringify({ selectedAnomalies })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Anomalías actualizadas:', data);
      anomalyModal.classList.add('hidden');
    })
    .catch(error => {
      console.error('Error al enviar anomalías:', error);
    });
  } else {
    alert("Seleccione al menos una anomalía.");
  }
});
