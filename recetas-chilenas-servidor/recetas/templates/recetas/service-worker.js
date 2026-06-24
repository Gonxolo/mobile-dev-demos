const CACHE_NAME = 'v1-recetas-chilenas';
const ASSETS = [
  '/',
  '/static/recetas/styles.css',
  '/static/recetas/recetas.js',
  '/offline/',
  '/manifest.json',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

// Páginas de recetas: red primero, caché de respaldo (para poder ver
// recetas ya visitadas sin conexión). Estáticos: caché primero.
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then((cached) => cached || fetch(e.request))
    );
    return;
  }

  e.respondWith(
    fetch(e.request)
      .then((response) => {
        const copia = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, copia));
        return response;
      })
      .catch(() =>
        caches.match(e.request).then((cached) => cached || caches.match('/offline/'))
      )
  );
});
