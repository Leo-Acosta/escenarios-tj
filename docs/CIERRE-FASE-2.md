# Estado de fase 2 · interfaz y navegación integral

Implementado: consulta/edición de expedientes, etapas e historial; comparación de versiones; árboles con creación, edición, asociación y Monte Carlo; laboratorios de agentes, comparación e incentivos vinculados a matrices conservadas; reproducción de agentes y repeticiones del comparador; redes con edición, versiones y evidencia; asistencia local de expediente y del editor de árboles.

## Un bloque pendiente para cerrar la fase

1. Revisión integral de los flujos React: cambios de expediente y versión, errores y conflictos, protección de borradores, teclado y tamaños de pantalla, impresión de vistas y consistencia de títulos/contexto. Resolver los defectos encontrados y documentar el cierre. Incluir la continuidad de trabajos secuenciales de IA y el acceso a su procedencia.

Es un bloque de trabajo pendiente, no un porcentaje medido ni una fecha comprometida. La revisión puede producir correcciones adicionales. La fase se cerrará solo con evidencia de la revisión integral completa.

Fuera del cierre de fase 2: formalización de variables y unidades (3), gráficos avanzados (4), autoguardado y recuperación (5), informe ejecutivo unificado congelado (6), evaluación empírica y distribución (fases posteriores). Estos objetivos no se consideran cumplidos por integrar la IA.

## Bloque terminado · reproducción del comparador

Selección de celda y repetición con semilla conservada, reconstrucción determinista en Python, gráfico de utilidad acumulada por actor, reproducción con velocidad y pausa, decisiones/pagos/motivos por ronda. La reconstrucción no guarda otra versión. Se validan referencia de origen, políticas, configuración, matriz y secuencia de rondas; los cambios cancelan consultas obsoletas. Históricos sin semillas muestran su limitación explícita.

Validación del 7 de octubre: 42 pruebas frontend, compilación de producción y 4 pruebas Python de comparación correctas. Navegador sobre base aislada: repetición 2/semilla 43, última ronda y cambio de celda con reinicio a ronda 1 comprobados. La revisión integral de impresión y accesibilidad queda en el bloque pendiente.

## Revisión integral · primer avance

Corregidos: desbordamiento de tablas mediante contenedores desplazables y columnas flexibles; navegación a la sección actual sin retirar la protección del borrador; apertura de expediente vinculado con confirmación antes de cambiar contexto; actualización que conserva la versión seleccionada si sigue disponible. Añadidos enlace para saltar al contenido, foco en el encabezado al cambiar sección y título del navegador según módulo. Las tablas de resultados son alcanzables con teclado.

Impresión: se conservan avisos de alcance, contexto y procedencia; se ocultan acciones y controles de reproducción; el comparador usa columnas compactas. Estas reglas requieren todavía verificación visual paginada antes del cierre.

Evidencia: 42 pruebas frontend y compilación correctas; consulta del comparador en navegador con tabla desplazable y encabezado contextual. La prueba automatizada del diálogo de descarte fue inconclusa (el navegador agotó el tiempo de la interacción); no se considera aprobada. La comprobación de ancho no confirmó que el cambio a 390 px estuviera aplicado, por lo que tampoco certifica ese tamaño.

Para terminar este bloque quedan: recorrido de conflictos y descarte/reanudación de formularios; comprobación efectiva de tamaños estrechos e impresión paginada; continuidad y procedencia de trabajos secuenciales de IA. La fase 2 permanece abierta.

## Continuidad de IA secuencial · recuperación y procedencia

El editor permite consultar y recuperar los últimos cinco trabajos secuenciales de la base local (no son exclusivos del árbol abierto). Recuperar vuelve a conectar el seguimiento de un trabajo en generación y muestra propuestas listas o errores conservados. No restaura automáticamente el borrador, su descripción ni sus pagos. Aplicar requiere revisión explícita y el modelo/descripción originales; Python mantiene la validación de huella de origen y rechaza cambios. La procedencia muestra trabajo, modelo, identificador, publicador y licencia cuando fueron registrados, sin inventar metadatos de históricos.

Verificación: 43 pruebas frontend, compilación correcta y 4 pruebas Python de IA secuencial. En navegador/base aislada se recuperó el trabajo QA 80471b0b-b89b-493c-968c-a8d9ce27aca2 desde otra sesión del editor y se consultó su procedencia. No se solicitó otra generación ni se modificaron pagos. El seguimiento de trabajos usa el mismo mecanismo de consulta existente; no se certifica una nueva generación real en este avance.

Para cerrar fase 2 aún deben completarse las pruebas de descarte y conflictos de formularios, pantalla estrecha e impresión paginada. La recuperación automática de borradores corresponde a fase 5.

## Descarte de borradores · diálogo integrado

La navegación principal y la apertura de expedientes vinculados usan un diálogo modal de la aplicación, con nombre/descripción accesibles y foco inicial en Seguir editando. Escape cancela la salida. Solo Descartar y continuar cambia la sección/contexto y retira la protección; pulsar la sección actual no descarta el borrador. Las versiones SQLite no se modifican.

Verificación en navegador/base aislada: título de un nuevo expediente introducido, clic en la sección actual, intento de navegar a laboratorios, diálogo visible con foco en Seguir editando, cancelación con título conservado y posterior descarte explícito con llegada a laboratorios. Esta evidencia reemplaza la prueba inconclusa del diálogo nativo de navegación principal. Los diálogos internos de árboles/redes/laboratorios y el manejo visual de conflicto siguen requiriendo recorrido específico.

El ajuste de viewport del navegador volvió a devolver un ancho efectivo de 749 px aunque se solicitó 390 px. No se certifica todavía el tamaño estrecho. Quedan pendientes pantalla estrecha e impresión paginada; fase 2 abierta.
