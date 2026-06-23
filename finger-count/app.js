// ==========================================
// 1. REGISTRO DE SERVICE WORKER Y PWA
// ==========================================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js')
      .then((reg) => console.log('Service Worker de IA Activo.', reg))
      .catch((err) => console.error('Error al registrar Service Worker.', err));
  });
}

// Control de Banner de Instalación
let deferredPrompt;
const installBanner = document.getElementById('install-banner');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (installBanner) installBanner.style.display = 'block';
});

document.getElementById('btn-install-now')?.addEventListener('click', async () => {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    if (installBanner) installBanner.style.display = 'none';
  }
});

document.getElementById('btn-cancel-install')?.addEventListener('click', () => {
  if (installBanner) installBanner.style.display = 'none';
});

// ==========================================
// 2. MOTOR DE IA: VISIÓN COMPUTACIONAL LOCAL
// ==========================================
const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');
const statusElement = document.getElementById('ai-status');

// Elementos de métricas clínicas
const metricHand = document.getElementById('metric-hand-present');
const metricFingers = document.getElementById('metric-fingers-count');

// Función matemática simple para calcular si un dedo está estirado (falange superior vs falange inferior)
function contarDedosExtendidos(landmarks) {
  // Los índices de MediaPipe representan las puntas de los dedos y sus articulaciones inferiores
  const tipIds = [8, 12, 16, 20]; 
  let dedosArriba = 0;

  // Evaluar 4 dedos largos (Índice, Medio, Anular, Meñique)
  for (let tipId of tipIds) {
    if (landmarks[tipId].y < landmarks[tipId - 2].y) {
      dedosArriba++;
    }
  }

  // Evaluar Pulgar (Usa la coordenada X en lugar de Y por la anatomía de abducción)
  if (landmarks[4].x < landmarks[3].x) {
    dedosArriba++;
  }

  return dedosArriba;
}

function procesarResultados(results) {
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    statusElement.textContent = "Analizando anatomía de la mano...";
    statusElement.style.color = "#00aa6c";
    metricHand.textContent = "Detectada";
    metricHand.style.color = "#00aa6c";

    const landmarks = results.multiHandLandmarks[0];
    
    // Contar dedos activos
    const conteo = contarDedosExtendidos(landmarks);
    metricFingers.textContent = conteo;

    // Dibujar los esqueletos en el Canvas de forma nativa y ultra ligera
    for (const point of landmarks) {
      const x = point.x * canvasElement.width;
      const y = point.y * canvasElement.height;
      canvasCtx.beginPath();
      canvasCtx.arc(x, y, 4, 0, 2 * Math.PI);
      canvasCtx.fillStyle = '#00aa6c';
      canvasCtx.fill();
    }
  } else {
    statusElement.textContent = "Apunta la cámara hacia tu mano abierta";
    statusElement.style.color = "#888";
    metricHand.textContent = "No Detectada";
    metricHand.style.color = "#7f8c8d";
    metricFingers.textContent = "-";
  }
}

// Configurar el modelo MediaPipe Hands
const hands = new Hands({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});

hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.6,
  minTrackingConfidence: 0.6
});

hands.onResults(procesarResultados);

// Inicialización asíncrona de cámara de hardware
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
    .then((stream) => {
      videoElement.srcObject = stream;
      statusElement.textContent = "Descargando modelo neuronal local...";
      
      // Enlazar los ciclos del procesador
      videoElement.addEventListener('loadedmetadata', () => {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        
        async function bucleIA() {
          if (!videoElement.paused && !videoElement.ended) {
            await hands.send({ image: videoElement });
          }
          requestAnimationFrame(bucleIA); // Ejecución continua de baja latencia
        }
        bucleIA();
      });
    })
    .catch((err) => {
      console.error("Acceso denegado a la cámara:", err);
      statusElement.textContent = "Error: Requiere permisos de cámara.";
    });
}