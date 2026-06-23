const CACHE_NAME = 'v1-taller-salud';
const ASSETS = [
  'index.html',
  'styles.css',
  'app.js',
  'offline.html',
  'manifest.json'
];

// Instalar el Service Worker y almacenar archivos críticos en caché
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Interceptación de peticiones: Priorizar Red, respaldar con Caché
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => {
      return caches.match(e.request).then((response) => {
        // Si el archivo solicitado está en caché, lo devuelve. Si no, va a la pantalla offline
        return response || caches.match('offline.html');
      });
    })
  );
});