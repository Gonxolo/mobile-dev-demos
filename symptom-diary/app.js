// 1. Registrar el Service Worker si el navegador lo soporta
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js')
      .then((reg) => console.log('Servicio médico activo en segundo plano.', reg))
      .catch((err) => console.error('Error al activar el servicio.', err));
  });
}

// 2. FUNCIÓN CLAVE: Cargar síntomas desde LocalStorage al iniciar la app
function cargarSintomas() {
  const lista = document.getElementById('sintomas-lista');
  if (!lista) return;

  // Recuperar los datos guardados (o un arreglo vacío si no hay nada)
  const sintomasGuardados = JSON.parse(localStorage.getItem('historialSintomas')) || [];

  if (sintomasGuardados.length > 0) {
    lista.innerHTML = ''; // Limpiar el mensaje de "No hay síntomas"
    
    // Renderizar cada síntoma guardado
    sintomasGuardados.forEach(sintoma => {
      const nuevoElemento = document.createElement('li');
      nuevoElemento.textContent = `${sintoma.fecha}: ${sintoma.texto}`;
      lista.appendChild(nuevoElemento); // Mantiene el orden cronológico guardado
    });
  }
}

// 3. Capturar el envío del formulario y PERSISTIR el dato
document.getElementById('sintoma-form')?.addEventListener('submit', (e) => {
  e.preventDefault();
  const input = document.getElementById('sintoma-input');
  const lista = document.getElementById('sintomas-lista');
  
  if (input.value.trim() !== "") {
    const textoSintoma = input.value;
    const horaActual = new Date().toLocaleTimeString();

    // --- NUEVA LÓGICA DE PERSISTENCIA ---
    // Obtener lo que ya existía en la base de datos local
    const sintomasExistentes = JSON.parse(localStorage.getItem('historialSintomas')) || [];
    
    // Crear el nuevo objeto de registro clínico
    const nuevoRegistro = {
      texto: textoSintoma,
      fecha: horaActual
    };

    // Agregar al inicio del arreglo para que lo nuevo aparezca arriba
    sintomasExistentes.unshift(nuevoRegistro);

    // Guardar el arreglo actualizado de vuelta en la memoria del teléfono
    localStorage.setItem('historialSintomas', JSON.stringify(sintomasExistentes));
    // ------------------------------------

    // Remover el estado vacío si es el primer elemento
    const emptyState = lista.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    // Actualizar la interfaz visual inmediatamente
    const nuevoElemento = document.createElement('li');
    nuevoElemento.textContent = `${nuevoRegistro.fecha}: ${nuevoRegistro.texto}`;
    lista.prepend(nuevoElemento);

    input.value = ""; // Limpiar el formulario
  }
});

// 4. Ejecutar la carga inicial apenas se abra la aplicación
document.addEventListener('DOMContentLoaded', cargarSintomas);

/// Install banner
let deferredPrompt;
const installBanner = document.getElementById('install-banner');
const btnInstallNow = document.getElementById('btn-install-now');
const btnCancelInstall = document.getElementById('btn-cancel-install');

// Capturar el evento nativo del navegador
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Mostrar el banner elegantemente cambiando el display
  if (installBanner) installBanner.style.display = 'block';
});

// Acción de Instalar
btnInstallNow?.addEventListener('click', async () => {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`Resultado de instalación: ${outcome}`);
    deferredPrompt = null;
    if (installBanner) installBanner.style.display = 'none';
  }
});

// Acción de Cancelar/Cerrar
btnCancelInstall?.addEventListener('click', () => {
  if (installBanner) installBanner.style.display = 'none';
});

// Ocultar si ya se instaló por otra vía
window.addEventListener('appinstalled', () => {
  if (installBanner) installBanner.style.display = 'none';
});