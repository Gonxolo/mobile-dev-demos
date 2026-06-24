# Mobile Dev Demos — CB Computación 2

Colección de demos para el curso. La mayoría son Progressive Web Apps (PWA) que corren 100% en el navegador, pensadas para mostrar conceptos de desarrollo móvil web: instalabilidad, soporte offline, persistencia local y uso de IA en el borde (Edge AI), sin backend. Una demo adicional muestra el caso contrario: un backend real sirviendo a varios clientes.

## Demos

- [**Diario de Síntomas**](symptom-diary/README.md) — PWA base sin IA: instalable, offline y con persistencia en `localStorage`. Punto de partida para construir tu propia PWA desde cero.
- [**Diario de Síntomas — Servidor**](diario-sintomas-servidor/README.md) — Contraparte con backend en Django del demo anterior: los datos viven en el servidor y se sirven como página HTML y como API JSON a la vez, ilustrando "un backend, muchos clientes".
- [**EvalMobility IA**](finger-count/README.md) — Cuenta dedos extendidos en tiempo real usando MediaPipe Hands y la cámara, 100% en el dispositivo.
- [**VisionCare IA**](ai-vision/README.md) — Clasifica fotos con TensorFlow.js + MobileNet directamente en el navegador, sin enviar imágenes a ningún servidor.

Cada carpeta es independiente y autocontenida: revisa el README de cada demo para detalles de funcionamiento, cómo ejecutarla localmente y sus limitaciones conocidas.
