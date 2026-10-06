# Verificación de versión 0.1

Fecha: 5 de octubre de 2026.

- Núcleo: valores conocidos, transición de equilibrio, empate, extremos y entradas no finitas.
- SQLite: creación y lectura desde conexiones distintas. Detectó conexiones sin cerrar que bloqueaban el archivo en Windows; corregido con cierre explícito.
- JavaScript: comprobación de sintaxis con Node.
- API: parámetros no finitos rechazados, Host no permitido bloqueado, rutas fuera de la lista cerrada devuelven 404 y escrituras desde otros orígenes devuelven 403. El servidor recalcula antes de guardar; no acepta una recomendación inventada enviada por el cliente. Seis pruebas automáticas pasaron.
- PDF: dos páginas A4 renderizadas con Poppler e inspeccionadas visualmente; tablas, árbol, red y barras sin recortes.

- Navegador: pasar costo de 3 a 1 cambia la alternativa a competir y sus utilidades de 1 a 3; guardado de instantánea #1, recuperación del historial y apertura del informe con parámetros consistentes. Selección del actor B actualiza su descripción. No se observó desbordamiento de los paneles en la medición DOM de escritorio.
- La captura visual de la interfaz mediante la herramienta de navegador no estuvo disponible; la revisión de esa pantalla se limita al DOM, interacción y mediciones de composición. El PDF sí fue inspeccionado visualmente.

Ningún caso histórico ha sido utilizado: estas pruebas no demuestran precisión predictiva.

## Panel gráfico interactivo

Editor de red propia: ocho pruebas automáticas pasaron, con persistencia SQLite y rechazo de nombres/tipos/relaciones inválidos. En el navegador se crearon dos entidades y un vínculo, sin guardarlos como datos del usuario. Los nombres ingresados se escapan en el SVG y se insertan como texto en el inspector.

Verificado en navegador: selección directa de vector y nodo, selección por Enter, zoom 125 %, restablecimiento 100 %, plegado y expansión de rama (dos/cuatro hojas visibles). Selección sincronizada entre árbol, plano y lectura de pagos. Sin desbordamiento medido en los paneles de escritorio. Exportación SVG conserva el encuadre completo del árbol aunque se amplíe en pantalla. El plano usa igual escala por unidad en ambos ejes. Captura visual automatizada sigue sin estar disponible.

Avance de casos propios: 14 pruebas aprobadas (incluye dilema del prisionero, coordinación y juego sin equilibrio puro). Sintaxis de case.js validada con Node. Flujo de navegador comprobado: cálculo, guardado y recuperación de un caso 2×2; utilidades A de 1,8 y 3,4 bajo q=0,6. La revisión visual por captura no estuvo disponible.

Integración visual de casos propios: comprobados actores personalizados Municipio/Vecinos, selección sincronizada del resultado 4, informe con pagos propios y cambio de fuente a ejemplo institucional. Vectores SVG con escala común y flechas. Revisada captura de pantalla del informe; CSS de impresión agregado, sin verificación de paginación en un PDF impreso. Sintaxis de los tres JavaScript modificados validada.

Sensibilidad: 17 pruebas aprobadas, incluyendo cruce en 1/3, empate en todo el intervalo, dominancia y umbral en 0. En navegador: curva del caso propio, cambio de Cooperar a Competir al bajar q a 0, nueva versión guardada e informe con B 0 % y umbral 33,33 %. Sintaxis JavaScript validada.


## Coordinador guiado — primera entrega A y B

23 pruebas aprobadas. Cubren persistencia de conversación y pregunta pendiente, rechazo de cálculos sin preparación o revisión, rechazo de no finitos, fuentes incompletas, versiones con contexto inmutable, borrador incompleto sin resultados falsos, conflicto de revisión y API del expediente.

Flujo en navegador: creación de un expediente de obra pública con datos hipotéticos; recuperación tras recargar en la segunda pregunta; cinco respuestas; modelo manual; guardado del borrador; rechazo de cálculo sin revisión; referencia de prueba; cálculo de versión 1; gráficos e informe con objetivo, datos pendientes, fuentes y supuestos. Aplicar sensibilidad a q=0 produjo versión 2 del mismo expediente. El informe histórico de versión 1 conservó B=50 %. Captura de la vista ejecutiva revisada; paginación de impresión pendiente.

Los JavaScript modificados pasaron la validación de sintaxis con Node. No se configuró IA ni se descargaron modelos. No se generó un ejecutable ni un PDF propio directo en esta entrega.


## Primera integración C — IA local

33 pruebas aprobadas. Nuevas verificaciones: configuración limitada a un modelo revisado, rechazo de digest modificado, desconexión con modo guiado disponible, esquema sin campos de pagos/probabilidades/código, aplicación de nombres sin cambiar números, rechazo de propuestas desactualizadas, registro de fallos y recuperación de trabajos interrumpidos. Pruebas del contrato /api/chat con esquema y rechazo de JSON inválido o generación incompleta.

Equipo inspeccionado: 22,8 GiB RAM, AMD Radeon integrada, Ollama 0.35.1 y Mistral 7B Q4_K_M instalados. Procedencia contrastada con la ficha oficial del publicador; licencia Apache en el modelo instalado. No se instalaron servicios ni se descargaron modelos. La primera prueba real alcanzó el timeout de 180 segundos y conservó el expediente. Se redujeron contexto/salida a 4096/600 tokens y se ajustó el timeout a 240 segundos para esta CPU.

La segunda generación real finalizó correctamente en 132,51 segundos (421 tokens). En navegador se aplicó al expediente de prueba, se conservaron A/B y p=0,5/q=0, se confirmó la revisión y se guardó versión 3. El informe propio mostró modelo, digest, licencia y variables propuestas, separados de las fuentes. La IA retomó el 50 % de una respuesta anterior: se agregó el borrador numérico actual al contexto y una instrucción para señalar contradicciones. Esta corrección de contexto está cubierta por prueba de contrato; su efecto semántico requiere nuevas evaluaciones reales. El contexto enviado y las opciones se conservan en nuevas propuestas.

## Primera entrega D: árboles secuenciales

39 pruebas aprobadas: inducción hacia atrás, respuestas fuera de la ruta, ocho planes en empate total, pagos inválidos, versiones inmutables y API con revisión obligatoria para guardar. En navegador: solución Entrar → Acomodar (2,1), exploración Entrar → Competir con aviso de respuesta no óptima, guardado, recuperación tras recargar y ampliación a 140 %. Informe específico preparado para impresión; paginación física/PDF pendiente de revisión. Monte Carlo, agentes y conexión del árbol al coordinador siguen pendientes.

## Simulación de incertidumbre en árboles

43 pruebas aprobadas. Nuevos casos: amplitud cero coincide con solución base; semilla idéntica reproduce resultados y muestras; otra semilla cambia las muestras; pagos respetan los intervalos; empate total conserva ambigüedad y rutas; se rechazan configuraciones inválidas. La API guarda y recupera estadísticas. En navegador: 1000 repeticiones, semilla 42, amplitud ±2: Entrar 79,7 %, No entrar 20,3 %. Inspección de repetición 2, guardado y recuperación tras recargar verificados. El informe incorpora estadísticas y supuestos; la paginación de impresión sigue sin verificación.

## Exportación directa de PDF secuencial

46 pruebas aprobadas: modelo e identificador guardados en PDF, simulación con semilla y conteos, literalidad de marcado del usuario y paginación de supuestos largos. API: MIME application/pdf, cabecera PDF y 404 para versión inexistente. Descarga real desde navegador: informe-arbol-escenarios-tj.pdf, tres páginas, UUID de la versión y semilla 42 verificados. El ejemplo output/pdf/informe-arbol-monte-carlo.pdf fue renderizado con Poppler; las tres páginas finales se inspeccionaron visualmente sin superposiciones ni recortes. Corregidos una página casi vacía y artefacto de barra a 0 %. El PDF propio simultáneo, conexión de IA al árbol, agentes y ejecutable siguen pendientes.

## IA local para árboles secuenciales

52 pruebas aprobadas. Nuevas verificaciones: tres nodos obligatorios, rechazo de campos de pagos y alternativas duplicadas, conservación de pagos/supuestos, conflicto por descripción o simulación modificadas, generador específico, registro de esquema/contexto, API de aplicación y procedencia en PDF. Prueba real de Mistral: 143,61 segundos, 442 tokens; seis decisiones válidas y variables/preguntas. En navegador se modificó el título y se verificó aplicación deshabilitada; se restauró, aplicó y guardó una versión con Monte Carlo. PDF output/pdf/informe-arbol-ia-local.pdf: cuatro páginas renderizadas e inspeccionadas visualmente, con propuesta separada de modelo final y metadatos.

La prueba real es un caso ilustrativo; no demuestra precisión general ni validación predictiva. Todavía faltan agentes con memoria, ejecutable y unificación del expediente simultáneo y secuencial.

## Agentes con memoria

60 pruebas aprobadas. Nuevos casos: memoria sin observar la ronda actual, cambio persistente, orientación de la mejor respuesta de B, ruido observado en la siguiente ronda, reproducibilidad sin mutar entradas, configuración inválida, versiones inmutables y revisión requerida por API. Navegador: Municipio copia la segunda alternativa de Vecinos recién en ronda 2; en ronda 25 se verificaron 24 observaciones previas y acumulados A=24/B=29. Guardado y recuperación tras recargar comprobados. JavaScript validado con Node. El PDF de agentes y la calibración con datos siguen pendientes.

## Informes de agentes y traza CSV

65 pruebas aprobadas. Nuevas verificaciones: PDF con UUID, políticas, totales y semilla; gráfico con pagos acumulados nulos; marcado de usuario literal; supuestos largos paginados; dos filas por ronda en CSV y memoria previa; texto de fórmula neutralizado sin alterar pagos negativos. API: formatos, firmas y 404 para corrida inexistente. Descargas reales desde navegador verificadas: tres páginas y 100 filas para 50 rondas; UUID conservado y acumulado final de B=54. PDF output/pdf/informe-agentes-memoria.pdf renderizado con Poppler e inspeccionado en sus tres páginas finales; corregida una página casi vacía. CSV de ejemplo output/rondas-agentes.csv. El empaquetado Windows, PDF propio simultáneo y calibración predictiva siguen pendientes.

## Comparador de políticas

69 pruebas aprobadas. Nuevos casos: 36 pares contrastados con ejecuciones individuales, orientación de pagos, dispersión con una repetición, límites y tipos inválidos, matriz inmutable, reproducción de semilla e índices inválidos. Interfaz: comparación revisada guardada, selector A/B, combinación Azar/Frecuencia y semilla 44 reproducida con medias A=0,66/B=2,86; recuperación tras recarga comprobada. Las pruebas SQLite necesitaron ejecución fuera del sandbox por restricciones de directorios temporales. Exportación propia del comparador y validación predictiva quedan pendientes.

## PDF del comparador

74 pruebas aprobadas. Verificado: cuatro páginas, UUID y semillas conservados, resumen de B por columnas, pagos negativos y escala uniforme, título con marcado literal y supuestos largos paginados. API verifica firma PDF, tipo MIME y 404. En navegador se recuperó la comparación guardada y se comprobó el enlace de descarga con su UUID. Ejemplo output/pdf/informe-comparador.pdf renderizado con Poppler: cuatro páginas inspeccionadas sin recortes ni solapamientos. Pendientes: calibración predictiva y empaquetado Windows.
