# Diario de Síntomas — Taller de PWA

PWA de demostración, sin IA, enfocada en los tres pilares básicos de una Progressive Web App: **instalable**, **funciona offline**, y **persiste datos localmente** (sin backend). Sirve como base/referencia para que el público construya su propia PWA desde cero.

## Idea principal

Un diario simple donde el usuario registra síntomas con fecha/hora. Cada registro se guarda en `localStorage` del navegador, por lo que los datos sobreviven a recargar la página o cerrar la app, y nunca salen del dispositivo.

## Cómo funciona

1. `app.js` registra el `service-worker.js` al cargar la página.
2. Al enviar el formulario, el síntoma se guarda como objeto `{ texto, fecha }` en un arreglo en `localStorage` (clave `historialSintomas`) y se antepone a la lista en pantalla.
3. Al recargar la app, `cargarSintomas()` lee `localStorage` y reconstruye la lista.
4. `service-worker.js` usa una estrategia **network-first con respaldo en caché**: intenta ir a la red primero y, si falla (sin conexión), responde con el archivo cacheado correspondiente o, si no existe, con `offline.html`.
5. El banner de instalación (`beforeinstallprompt`) permite instalar la app a la pantalla de inicio.

## Cómo ejecutarlo localmente

El Service Worker requiere un **contexto seguro** (HTTPS o `localhost`); no funciona abriendo `index.html` con doble clic (`file://`).

```bash
# Desde esta carpeta, con Python instalado:
python3 -m http.server 8080
# o con Node.js:
npx serve .
```

Luego abre `http://localhost:8080`. Para probar el modo offline: carga la app una vez con conexión, después desactiva la red (o usa la pestaña "Network → Offline" de las DevTools) y recarga.

## Estructura de archivos

```txt
pwa-taller-salud/
├── index.html           # Interfaz del Diario de Síntomas (Responsiva)
├── styles.css           # Estilos mobile-first base
├── app.js               # Lógica del cliente y registro del Service Worker
├── manifest.json        # Configuración de instalación PWA
├── service-worker.js    # Estrategia Offline (network-first con respaldo en caché)
└── offline.html         # Pantalla de respaldo sin conexión
```

## Limitaciones conocidas (para discutir en clase)

- `localStorage` es por navegador y por origen: los datos no se sincronizan entre dispositivos ni se respaldan en la nube; borrar datos del navegador los elimina permanentemente.
- No hay validación ni límite de tamaño para el texto del síntoma — es intencional, para mantener el ejemplo simple.
- El ícono del manifest se carga desde un CDN externo (Flaticon): si el dispositivo está completamente offline antes de la primera carga, el ícono de instalación puede no mostrarse.

## Referencias para profundizar

- [web.dev: ¿Qué es una PWA?](https://web.dev/explore/progressive-web-apps)
- [MDN: Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [web.dev: Offline cookbook (estrategias de caché)](https://web.dev/articles/offline-cookbook)
- [MDN: Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [web.dev: beforeinstallprompt y banner de instalación](https://web.dev/patterns/web-apps-install-promotion/)
