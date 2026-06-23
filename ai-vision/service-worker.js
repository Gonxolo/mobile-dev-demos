const CACHE_ESTATICA = 'ai-vision-assets-v1';
const CACHE_MODELO = 'ai-tensorflow-model-v2'; // Incrementamos la versión para limpiar basura previa

const ASSETS_TO_CACHE = [
  'index.html',
  'styles.css',
  'app.js',
  'manifest.json',
  'offline.html'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_ESTATICA).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

// Interceptación Avanzada con Limpieza de CORS para TensorFlow
self.addEventListener('fetch', (e) => {
  const url = e.request.url;

  // Detectar si la petición es para las librerías o los fragmentos binarios del modelo (.bin / .json)
  if (url.includes('cdn.jsdelivr.net') || url.includes('storage.googleapis.com')) {
    e.respondWith(
      caches.open(CACHE_MODELO).then((cache) => {
        return cache.match(e.request).then((cachedResponse) => {
          // 1. Si ya está guardado en el disco local, entregarlo de inmediato (0 milisegundos)
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // 2. Si no está, lo descargamos pero FORZAMOS el modo CORS 'cors' de manera limpia
          // Esto soluciona el problema de las peticiones opacas que TensorFlow hace por defecto
          const fetchRequest = new Request(e.request, { mode: 'cors', credentials: 'omit' });

          return fetch(fetchRequest).then((networkResponse) => {
            // Validar que la respuesta de la red sea exitosa (status 200) antes de guardarla
            if (networkResponse.status === 200) {
              cache.put(e.request, networkResponse.clone());
            }
            return networkResponse;
          }).catch((err) => {
            console.error("Error de red al intentar descargar fragmento del modelo:", err);
          });
        });
      })
    );
  } else {
    // Control normal de los archivos locales de la app
    e.respondWith(
      caches.match(e.request).then((cachedResponse) => {
        return cachedResponse || fetch(e.request).catch(() => caches.match('offline.html'));
      })
    );
  }
});