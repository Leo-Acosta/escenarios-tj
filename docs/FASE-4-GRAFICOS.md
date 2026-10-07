# Fase 4 · gráficos avanzados

Ampliación del 7 de octubre de 2026. Se reutilizan los laboratorios de árboles y redes existentes, sus versiones y controles. No se duplican simuladores ni se modifica el motor Python.

## Implementación

El Centro de análisis incorpora un observatorio de vectores y sensibilidad asociado al expediente y versión seleccionados. Los vectores parten del origen y representan los cuatro pares de pagos. Botones permiten inspeccionar cada resultado sin depender del ratón; filtros muestran todos, equilibrios puros o una estrategia de A. Los ejes se escalan separadamente: no debe inferirse comparabilidad interpersonal de utilidades ni probabilidades a partir de sus distancias.

El gráfico de sensibilidad utiliza las 101 muestras que ya calcula Python en la matriz conservada. Un deslizador selecciona q entre 0 y 100 %, con valores, mejores respuestas, empates y umbral de indiferencia recibidos del núcleo. Cambiar q es exploración temporal; no guarda ni modifica una versión. No ejecuta IA.

Puede seleccionarse un diccionario conservado de esa misma matriz para inspeccionar valores, unidades, vínculos, fuentes, evidencia e intervalos declarados. Se comprueban expediente, número de versión y matriz antes de asociar las fuentes. La interfaz muestra ausencia de diccionarios y errores sin inventar evidencia. Las variables de contexto y sus intervalos no se convierten automáticamente en distribuciones causales.

JSON exporta matriz, muestras Python, diccionario opcional y estado visual. SVG exporta ambos gráficos vectoriales con la vista seleccionada para documentos; el JSON contiene la trazabilidad detallada. Las reglas de impresión excluyen controles. Los informes ejecutivos y laboratorios existentes mantienen sus exportaciones previas.

## Verificación y límites

- TypeScript/Vite compila; 61 pruebas frontend pasan, incluidas muestras incompletas/desordenadas, valores no finitos y decisiones fuera del contrato.
- Navegador local: expediente sintético existente, carga de versión 3, selección R4, filtro de equilibrios, extremo q=100 %, ausencia de diccionarios y descarga JSON comprobados. El archivo descargado contiene 101 muestras y la configuración seleccionada. No es evidencia de predicción real.
- La exportación SVG compila, pero su descarga y representación visual aún no fueron verificadas en navegador.
- La captura del navegador volvió a fallar; composición visual, móvil y paginación física permanecen pendientes. Tampoco se verificó visualmente el recorrido con un diccionario no vacío en este bloque.

La fase 4 tiene esta ampliación funcional implementada, pero no se declara cerrada la aceptación visual integral. Quedan unificar las paletas de todos los laboratorios, comprobar exportación SVG y recorrido con variables documentadas y revisar escritorio/móvil e impresión. Luego corresponde fase 5: autoguardado, respaldo, restauración y migraciones. La validación empírica de fase 8 sigue independiente de estos gráficos.
