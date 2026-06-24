// Registro del service worker: en cualquier página de la app.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').catch((err) => {
      console.warn('No se pudo registrar el service worker:', err);
    });
  });
}

// Lo que sigue solo aplica a la página de detalle de una receta.
(function inicializarDetalleReceta() {
  const datosEl = document.getElementById('datos-receta');
  if (!datosEl) return;

  const datos = JSON.parse(datosEl.textContent);
  const { ingredientes, unidadesPorTipo, unidadesSimples, porcionesBase } = datos;

  const TIPOS = ['volumen', 'masa'];
  const seleccionUnidad = { volumen: '', masa: '' }; // '' = mantener unidad original de cada ingrediente
  let porcionesActuales = porcionesBase;

  // Construye los <select> de conversión solo para los tipos que de verdad
  // aparecen entre los ingredientes de esta receta (no tiene sentido
  // mostrar un selector de "masa" si la receta no usa gramos ni kilos).
  TIPOS.forEach((tipo) => {
    const usaEsteTipo = ingredientes.some((ing) => ing.tipo === tipo);
    const contenedor = document.querySelector(`[data-control-tipo="${tipo}"]`);
    const select = document.getElementById(`select-${tipo}`);
    if (!usaEsteTipo || !contenedor || !select || !unidadesPorTipo[tipo]) return;

    contenedor.hidden = false;

    const opcionOriginal = document.createElement('option');
    opcionOriginal.value = '';
    opcionOriginal.textContent = 'Original (mixto)';
    select.appendChild(opcionOriginal);

    unidadesPorTipo[tipo]
      .slice()
      .sort((a, b) => a.factor_base - b.factor_base)
      .forEach((unidad) => {
        const opcion = document.createElement('option');
        opcion.value = unidad.codigo;
        opcion.textContent = `${unidad.nombre} (${unidad.abreviatura})`;
        select.appendChild(opcion);
      });

    select.addEventListener('change', () => {
      seleccionUnidad[tipo] = select.value;
      render();
    });
  });

  document.getElementById('porciones-menos').addEventListener('click', () => {
    if (porcionesActuales > 1) {
      porcionesActuales -= 1;
      render();
    }
  });

  document.getElementById('porciones-mas').addEventListener('click', () => {
    porcionesActuales += 1;
    render();
  });

  function buscarUnidad(tipo, codigo) {
    return (unidadesPorTipo[tipo] || []).find((u) => u.codigo === codigo);
  }

  function formatearCantidad(valor) {
    const redondeado = Math.round(valor * 100) / 100;
    return redondeado % 1 === 0 ? redondeado.toFixed(0) : redondeado.toFixed(2).replace(/0$/, '');
  }

  function render() {
    document.getElementById('porciones-valor').textContent = porcionesActuales;
    const factorEscala = porcionesActuales / porcionesBase;
    const lista = document.getElementById('lista-ingredientes');
    lista.innerHTML = '';

    ingredientes.forEach((ing) => {
      const cantidadEscalada = ing.cantidad * factorEscala;
      let cantidadFinal = cantidadEscalada;
      let abreviatura;

      if (ing.tipo === 'unidad') {
        abreviatura = (unidadesSimples[ing.unidad_codigo] || {}).abreviatura || ing.unidad_codigo;
      } else {
        const origen = buscarUnidad(ing.tipo, ing.unidad_codigo);
        const destinoCodigo = seleccionUnidad[ing.tipo];
        const destino = destinoCodigo ? buscarUnidad(ing.tipo, destinoCodigo) : origen;

        if (origen && destino) {
          cantidadFinal = (cantidadEscalada * origen.factor_base) / destino.factor_base;
          abreviatura = destino.abreviatura;
        } else {
          abreviatura = ing.unidad_codigo;
        }
      }

      const li = document.createElement('li');

      const cantidadSpan = document.createElement('span');
      cantidadSpan.className = 'ingrediente__cantidad';
      cantidadSpan.textContent = `${formatearCantidad(cantidadFinal)} ${abreviatura}`;

      const nombreSpan = document.createElement('span');
      nombreSpan.className = 'ingrediente__nombre';
      nombreSpan.textContent = ing.nombre;
      if (ing.nota) {
        const nota = document.createElement('span');
        nota.className = 'ingrediente__nota';
        nota.textContent = ` (${ing.nota})`;
        nombreSpan.appendChild(nota);
      }

      li.appendChild(cantidadSpan);
      li.appendChild(nombreSpan);
      lista.appendChild(li);
    });
  }

  render();
})();
