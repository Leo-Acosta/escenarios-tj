# Fase 6: informe ejecutivo unificado

## Auditoría y criterios de cierre

Los exportadores existentes de matriz, árbol/Monte Carlo, agentes, comparaciones e incentivos generan documentos individuales. El módulo research genera HTML de evaluación binaria. No existe un manifiesto que congele la selección entre módulos ni una vista unificada. Se reutilizarán sus motores y registros; no se concatenarán PDF ni se volverá a inferir con Ollama.

Requisitos verificables: selección explícita de fuentes del mismo expediente; matriz versionada como base; árbol identificado como modelo independiente; selección de secciones; resumen con evidencia y pendientes; fuentes y límites obligatorios; registro inmutable con copias y huellas; reproducción desde esas copias aunque cambie el expediente; HTML A4 y PDF vectorial con igual contenido; interfaz española con historial, previsualización y exportación; controles de integración, privacidad y revisión visual de páginas renderizadas.

Las fuentes documentales son aportadas por el analista, no autenticadas automáticamente. Los hechos declarados no se transforman en hechos verificados. Los resultados sintéticos nunca acreditan mejora real. No se inventan valores para completar módulos faltantes. Los informes y bases privados quedan fuera de Git.

## Resultado y uso

Implementación terminada el 7 de octubre de 2026. En `/app/`, abrir **Informe ejecutivo**, seleccionar expediente y versión calculada, clasificar la evidencia y elegir secciones y fuentes. Revisar la composición y pulsar **Conservar y previsualizar informe**. El historial permite abrir documentos conservados, verificar su reproducción y descargar PDF o JSON. **Abrir A4 e imprimir** abre la versión HTML con impresión del documento, sin los controles del compositor. Los exportadores individuales permanecen disponibles; no se duplicaron sus motores.

El documento incluye portada, índice, resumen ejecutivo, matriz, árboles, Monte Carlo, agentes con memoria, comparación de políticas, sensibilidad, decisiones de IA local, baterías y evaluación predictiva. Las secciones de análisis son opcionales; resumen, fuentes, pendientes y límites siempre se incluyen. Si falta una fuente, se indica como pendiente. Los árboles son modelos secuenciales independientes del mismo expediente: no se afirma que hereden la matriz simultánea. Las fuentes restantes deben corresponder a la misma versión de matriz.

Los gráficos PDF son vectoriales y comparten coordenadas y contenido con los SVG de la vista A4. Las escalas de cada actor se mantienen separadas. El informe muestra Brier y referencia explícita cuando existe evaluación; conserva victorias, empates, pérdidas y fallos de la batería. Las líneas se muestrean hasta 80 puntos y las tablas largas muestran muestras identificadas; el JSON conserva todas las trazas y observaciones. Las fuentes aportadas se identifican como documentación declarada, sin autenticación automática.

## Conservación y reproducción

`executive_reports` almacena manifiestos nuevos, sin edición posterior por la API. Cada uno conserva selección, versión de matriz, copias completas de fuentes, UUID, fecha y SHA-256. Cambiar el expediente o eliminar un registro original no cambia su copia dentro del informe. La reproducción recalcula con los motores Python existentes y utiliza las decisiones IA conservadas; no solicita una nueva inferencia ni cambia pagos, evidencias o políticas.

Rutas: `GET /api/executive/catalog?workflow_id=…&version=…`, `POST /api/executive`, y consultas `history`, `replay`, `export`, `html` y `pdf`. Las últimas cuatro usan `id` del informe; history usa workflow_id. PDF requiere ReportLab. Sin esa dependencia, la API devuelve un error visible y la vista HTML A4 continúa disponible.

SHA-256 permite detectar cambios de contenido; no es una firma ni protege frente a quien reescribe toda la base y sus huellas. Los controles de reproducción no garantizan coherencia semántica completa. Los exportadores muestran resultados conservados, no consultan datos nuevos ni reclasifican una evaluación provisional como demostración definitiva.

## Verificación del cierre

- 154 pruebas Python aprobadas: incluye recorrido HTTP completo, rechazo de fuentes ajenas/duplicadas/no revisadas, modificación de cálculos aun con huellas recalculadas, reproducción sin fuentes originales, escape de HTML, A4 y PDF determinista.
- 56 pruebas frontend aprobadas y compilación TypeScript/Vite correcta. Persiste una advertencia del empaquetador sobre `use client` de React Flow; no impide compilar.
- Recorrido React con expediente sintético: composición, conservación, historial, vista A4, reproducción y descarga PDF. Protección de descarte conserva el borrador cuando se elige seguir editando. Desactivar árbol desactiva Monte Carlo y retira sus referencias; restablecer composición requiere confirmar descarte.
- PDF sintético de 19 páginas renderizado con Poppler: todas las páginas revisadas visualmente después de las correcciones de tablas, títulos y etiquetas. Portada, textos, gráficos y trazabilidad legibles, sin recortes detectados. Se probaron además textos extensos y pagos negativos.
- Compositor revisado visualmente en escritorio con captura acotada: se corrigieron campos inicialmente sin estilo; se comprobaron campos amplios, tarjetas de selección, contraste y jerarquía. La captura general inicial fue incompleta; una nueva pestaña y captura acotada permitieron completar esta revisión. No se afirma una verificación del diálogo/paginación de impresión HTML ni de todos los tamaños móviles. La salida PDF A4 sí fue revisada página por página; no se realizó impresión física.

## Límites operativos y pendientes externos

La fase 3 agrega **Variables y unidades** como fuente opcional del mismo expediente y versión. Los informes existentes mantienen sus referencias originales; no se incorpora un diccionario automáticamente. Ver [guía de fase 3](FASE-3-VARIABLES.md).

Hasta 16 fuentes complementarias por informe; catálogo de hasta 200 fuentes e historial de 50 informes por expediente. Ampliar paginación para volúmenes mayores. Modelos con las dimensiones que soportan los laboratorios existentes; no se amplían por generar el documento. La reproducibilidad del PDF se verifica en el mismo entorno de fuentes y dependencias, no se promete identidad binaria entre sistemas operativos diferentes.

Se cierra la **implementación funcional de fase 6** para el alcance indicado. La revisión visual de impresión HTML queda como limitación de verificación, no como prueba superada. La validación empírica de fase 8 continúa abierta: faltan observaciones reales independientes; el ejemplo sintético no acredita mejora predictiva ni éxito judicial. No se creó información nueva del caso EDESUR. Recuperación de borradores, variables y distribución Windows corresponden a otras fases.
