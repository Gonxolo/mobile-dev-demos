// ==========================================
// 1. REGISTRO DE SERVICE WORKER Y PWA
// ==========================================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js')
      .then((reg) => console.log('Service Worker de Visión Activo.', reg))
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
// 2. MOTOR DE IA: CLASIFICACIÓN DE IMÁGENES
// ==========================================
let modeloAI;
const imgSelector = document.getElementById('image-selector');
const imgElement = document.getElementById('selected-image');
const statusElement = document.getElementById('ai-status');
const resultElement = document.getElementById('prediction-result');

// Cargar el modelo MobileNet al inicializar la app
async function inicializarModelo() {
  try {
    statusElement.textContent = "Cargando cerebro de IA (MobileNet)...";
    statusElement.style.color = "#f39c12";
    
    // Configuración para permitir que el Service Worker guarde los archivos del modelo en caché de forma segura
    const configModelo = {
      version: 1,
      alpha: 1.0
    };

    // Cargar el modelo con la configuración
    modeloAI = await mobilenet.load(configModelo);
    
    statusElement.textContent = "IA Lista. Captura una foto para analizar.";
    statusElement.style.color = "#0a7cff";
  } catch (error) {
    console.error("Error cargando el modelo de IA:", error);
    statusElement.textContent = "Error al inicializar la IA local.";
    statusElement.style.color = "#cc0000";
  }
}

// Escuchar cuando el usuario tome o seleccione una foto
imgSelector?.addEventListener('change', async (event) => {
  const archivo = event.target.files[0];
  if (!archivo) return;

  const lector = new FileReader();
  
  // Procesar archivo de manera local en memoria base64
  lector.onload = async (e) => {
    imgElement.src = e.target.result;
    imgElement.style.display = 'block';
    
    statusElement.textContent = 'Procesando tensores de imagen...';
    statusElement.style.color = '#f39c12';
    resultElement.innerHTML = ''; // Limpiar predicciones anteriores

    // Esperar a que los pixeles estén completamente renderizados en el DOM
    imgElement.onload = async () => {
      if (!modeloAI) {
        statusElement.textContent = "El modelo aún no está listo.";
        return;
      }

      // 🧠 EJECUCIÓN DE LA INFERENCIA LOCAL
      const predicciones = await modeloAI.classify(imgElement);
      
      statusElement.textContent = "Análisis completo.";
      statusElement.style.color = "#27ae60";

      // Renderizar los resultados con sus porcentajes estructurados
      resultElement.innerHTML = predicciones.map(p => `
        <div class="prediction-item">
          <span>🔍 ${p.className.split(',')[0]}</span>
          <span class="prediction-percentage">${(p.probability * 100).toFixed(1)}%</span>
        </div>
      `).join('');
    };
  };
  
  lector.readAsDataURL(archivo);
});

// Lanzar inicialización al cargar el DOM
document.addEventListener('DOMContentLoaded', inicializarModelo);