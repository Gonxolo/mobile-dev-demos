# EvalMobility IA — Visión Computacional para Kinesiología

PWA de demostración que usa **MediaPipe Hands** para detectar la mano del usuario a través de la cámara y contar cuántos dedos están extendidos, en tiempo real y 100% en el dispositivo (sin enviar video a ningún servidor).

## Idea principal

Simula una herramienta de apoyo para evaluación de movilidad: el modelo de IA corre localmente en el navegador (Edge AI), detecta los 21 puntos de referencia ("landmarks") de la mano, y una función simple (`contarDedosExtendidos` en [app.js](app.js)) decide si cada dedo está estirado comparando la posición Y de la punta contra la articulación inferior (X para el pulgar).

## Cómo funciona

1. `app.js` registra el `service-worker.js` para soporte offline y pide acceso a la cámara con `getUserMedia`.
2. Cada frame de video se envía al modelo `Hands` de MediaPipe (cargado desde CDN).
3. El resultado (`onResults`) dibuja los landmarks sobre un `<canvas>` superpuesto al video y actualiza las métricas en pantalla.
4. Un bucle con `requestAnimationFrame` mantiene el análisis corriendo mientras el video esté activo.

## Cómo ejecutarlo localmente

La cámara (`getUserMedia`) y el Service Worker requieren un **contexto seguro** (HTTPS o `localhost`); no funciona abriendo `index.html` directamente con doble clic (`file://`).

```bash
# Desde esta carpeta, con Python instalado:
python3 -m http.server 8080
# o con Node.js:
npx serve .
```

Luego abre `http://localhost:8080` en el navegador y acepta el permiso de cámara.

## Estructura de archivos

```txt
pwa-ai-kine/
├── index.html           # Interfaz médica con contenedor de cámara
├── styles.css           # Diseño clínico adaptado a video y pantallas táctiles
├── app.js               # Registro PWA + Lógica de MediaPipe Hands
├── manifest.json        # Configuración de instalación PWA
├── service-worker.js    # Trabajador en segundo plano para soporte Offline
└── offline.html         # Pantalla de respaldo sin conexión
```

## Limitaciones conocidas (para discutir en clase)

- El conteo de dedos es una heurística simple basada en coordenadas, no una clasificación de gestos: puede fallar con la mano rotada, parcialmente oculta, o en ángulos extremos.
- Como la cámara usa `facingMode: "user"` (frontal), la imagen aparece espejada; la comparación del pulgar en X asume esa orientación.
- El ícono del manifest se carga desde un CDN externo (Flaticon): si el dispositivo está completamente offline antes de la primera carga, el ícono de instalación puede no mostrarse.
- Es una demo educativa, no un dispositivo médico — no está validada clínicamente.

## Referencias para profundizar

- [MediaPipe Hands — documentación oficial](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [MDN: MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [web.dev: Web App Manifest](https://web.dev/articles/add-manifest)
- [web.dev: Offline cookbook (estrategias de caché)](https://web.dev/articles/offline-cookbook)
