# Mejoras científicas en R

Estas dos etapas complementan la hoja de ruta existente; no reinician su numeración.

## Etapa 1: gráficos científicos

El observatorio React ofrece **Descargar laboratorio R**. La API GET
`/api/scientific/bundle?workflow_id=...&version=1` entrega un ZIP reproducible:
matriz congelada, pagos CSV, sensibilidad Python, corridas guardadas de esa versión,
scripts y manifiesto SHA-256. No incluye documentos privados del expediente.
El contenido de la matriz puede contener nombres introducidos por el usuario:
revisar antes de compartir el ZIP. No se envía automáticamente a GitHub.

`graficos.R` genera puntos, líneas, barras de valores y boxplots por actor cuando
existen corridas. Colores azul marino y ocre, leyendas en español, facetas y ejes
independientes para actores con unidades diferentes. Salida PDF vectorial y PNG
300 dpi. La interfaz interactiva existente continúa usando React/TypeScript.

RStudio es un IDE; Tableau y Power BI son aplicaciones que pueden importar los
CSV. No se agregaron paquetes ficticios con esos nombres. Plotly/htmlwidgets
generan una vista 3D opcional de q y las dos utilidades de A, sin inventar variables.

## Etapa 2: analítica avanzada

`aprendizaje.R` recibe datos externos revisados y cortes temporales. Compara una
referencia de prevalencia del desarrollo, regresión logística y, si están
instalados caret/nnet, una red pequeña. Selección por Brier de validación;
keras3 ofrece una red profunda opcional activada con `ESCENARIOS_KERAS=1`, con
normalización de desarrollo, semilla y modelo guardados. Requiere backend
configurado y no garantiza determinismo entre dispositivos.
normalización aprendida solo en desarrollo. Se excluyen unidades que cruzan
cortes. La carpeta final conserva modelos RDS, pronósticos, puntajes y entorno.
No permite sobrescribir una evaluación final existente. No autentica fechas ni
impide al operador repetir el análisis en otra carpeta: el protocolo Python
existente sigue siendo el registro de referencia para una evaluación prospectiva.
Los resultados externos no se importan ni promocionan automáticamente.

`exploracion.R` compara búsqueda exhaustiva discreta y recocido SANN sobre la
utilidad de A. No suma pagos de actores ni modifica la matriz. igraph representa
relaciones entre estrategias; simmer ejecuta un ejemplo sintético de cola de
atención; arules procesa transacciones binarias externas, si existen.
Las asociaciones no representan causalidad. La cola no modela el caso EDESUR.
No se encontró respaldo oficial de un paquete llamado SBO++; se utiliza optim.

## Verificación y pendientes

Pruebas Python verifican integridad, exportación determinista, correspondencia de
matriz/corridas y rechazo de versiones inválidas. Compilación TypeScript valida
la integración. **Rscript no está disponible en el entorno de desarrollo**:
los scripts no se han ejecutado ni sus gráficos se han inspeccionado visualmente.
No declarar cerradas ambas etapas hasta ejecutar R, revisar resultados y verificar
dependencias/versiones. La ejecución es externa y explícita; el servidor no admite
código R arbitrario ni instala paquetes.

Pendientes: gráficos R/3D ejecutados y revisados;
keras3 con entorno y datos suficientes; integración revisada de resultados R en
protocolos prospectivos Python; evaluación empírica independiente. No existe
evidencia nueva de mejora predictiva real.

Fuentes: [ggplot2](https://ggplot2.tidyverse.org/reference/),
[optim](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/optim.html),
[simmer](https://r-simmer.org/), [keras3](https://keras3.posit.co/).
