# VisionCare IA — Clasificador de Imágenes en el Borde

PWA de demostración que usa **TensorFlow.js + MobileNet** para clasificar una fotografía (tomada o subida desde el celular) directamente en el navegador, sin enviar la imagen a ningún servidor.

## Idea principal

Mostrar inferencia de IA "en el borde" (Edge AI): un modelo de redes neuronales convolucionales (MobileNet, entrenado sobre ImageNet) se descarga una vez y luego clasifica imágenes localmente, preservando la privacidad del paciente/usuario.

## Cómo funciona

1. `app.js` registra el `service-worker.js` y carga el modelo MobileNet (`mobilenet.load()`) al iniciar la página.
2. Al seleccionar/capturar una foto, `FileReader` la convierte a una URL `data:` en memoria (nunca sale del dispositivo).
3. Cuando la imagen termina de renderizarse en el DOM, se ejecuta `modeloAI.classify(imgElement)`.
4. Los resultados (clase + probabilidad) se listan en `#prediction-result`.
5. El `service-worker.js` usa una estrategia especial para los binarios del modelo (`.bin`/`.json` desde `jsdelivr`/`storage.googleapis.com`): los cachea aparte en `CACHE_MODELO` para que, tras la primera carga, el modelo funcione sin conexión.

## Cómo ejecutarlo localmente

El Service Worker y la captura de cámara (`capture="camera"`) requieren un **contexto seguro** (HTTPS o `localhost`); no funciona abriendo `index.html` con doble clic (`file://`).

```bash
# Desde esta carpeta, con Python instalado:
python3 -m http.server 8080
# o con Node.js:
npx serve .
```

Luego abre `http://localhost:8080`. La primera carga necesita internet para descargar TensorFlow.js, MobileNet y sus pesos; después quedan cacheados para uso offline.

## Estructura de archivos

```txt
pwa-ai-vision/
├── index.html           # Interfaz para captura de imágenes e IA
├── styles.css           # Diseño clínico mobile-first para previsualización de fotos
├── app.js               # Registro PWA + Lógica de TensorFlow.js / MobileNet
├── manifest.json        # Configuración de instalación PWA
├── service-worker.js    # Trabajador en segundo plano para soporte Offline
└── offline.html         # Pantalla de respaldo sin conexión
```

## Limitaciones conocidas (para discutir en clase)

- MobileNet está entrenado sobre ImageNet (1000 categorías genéricas de objetos/animales), **no** sobre imágenes médicas — las predicciones para fotos clínicas reales no son fiables y son solo ilustrativas.
- La primera carga del modelo (~16 MB) requiere conexión; el modo offline solo funciona después de esa primera descarga exitosa.
- El ícono del manifest se carga desde un CDN externo (Flaticon): si el dispositivo está completamente offline antes de la primera carga, el ícono de instalación puede no mostrarse.
- Es una demo educativa, no una herramienta de diagnóstico.

## Referencias para profundizar

- [TensorFlow.js — documentación oficial](https://www.tensorflow.org/js)
- [TensorFlow.js Models: MobileNet](https://github.com/tensorflow/tfjs-models/tree/master/mobilenet)
- [MDN: FileReader API](https://developer.mozilla.org/en-US/docs/Web/API/FileReader)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [web.dev: Offline cookbook (estrategias de caché)](https://web.dev/articles/offline-cookbook)
