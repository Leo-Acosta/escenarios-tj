# Escenarios TJ

Proyecto para construir un laboratorio de escenarios multiagente en Python, con interfaz y documentación en español y almacenamiento local.

Estado: primera entrega funcional del coordinador guiado. Incluye expedientes persistentes con conversación, fuentes, supuestos revisados, versiones de cálculo, gráficos propios e informe ejecutivo imprimible. Conserva matrices libres y el ejemplo institucional.

## Ejecutar

Python 3.11 o superior. La aplicación base usa la biblioteca estándar:

```powershell
python -m escenarios.server
```

Abrir http://127.0.0.1:8765. El servidor escucha sólo en el equipo local.

Para descargar PDF vectorial, instalar la dependencia opcional:

```powershell
python -m pip install "reportlab>=4.0,<5"
python -m escenarios.report
```

La impresión del navegador funciona sin ReportLab. Muestra incluida: `output/pdf/informe-ejecutivo-demo.pdf`.

Pruebas:

```powershell
python -m unittest discover -s tests -v
```

Los datos son ilustrativos. No es todavía un motor multiagente autónomo ni un sistema de predicción calibrado. La licencia de distribución del código propio queda pendiente de elección.

- [Auditoría del repositorio de referencia](docs/AUDITORIA_MIRO_FISH.md)
- [Diseño propuesto y etapas de implementación](docs/ARQUITECTURA.md)

La copia original se conserva en `reference/Miro-Fish`, excluida del control de versiones. No se ejecutó su código ni se instalaron sus dependencias. Se conserva intacta con su licencia y atribuciones. No se incorporaron sus implementaciones, prompts ni imágenes a la aplicación propia.

### Casos propios sin IA
La mesa permite definir un juego simultáneo 2×2 con nombres, estrategias, ocho pagos y probabilidades supuestas. Calcula utilidades esperadas, mejores respuestas de A, equilibrios puros y un equilibrio mixto interior aislado, si existe. Compara tres supuestos de conducta de B y guarda versiones en SQLite. No interpreta automáticamente el texto del chat ni calibra pronósticos. Los casos propios alimentan un árbol de consecuencias interactivo, vectores de utilidad y un informe ejecutivo imprimible. El informe propio se exporta con Imprimir → Guardar como PDF del navegador; la descarga directa de PDF sigue disponible para el ejemplo institucional.

El panel propio incluye sensibilidad de la utilidad de A al supuesto de B entre 0 % y 100 %, un umbral analítico de indiferencia y exportación de la curva SVG. La exploración es temporal hasta aplicar al análisis; puede guardarse como una nueva versión. El informe incluye la curva para el supuesto aplicado. Esto no estima la conducta de B con datos.

### Expedientes guiados

1. Crear un expediente con nombre y descripción.
2. Responder las cinco preguntas de preparación. Cada respuesta se guarda en SQLite.
3. Completar dos actores, sus estrategias y ocho pagos; registrar fundamentos, referencias y supuestos.
4. Guardar el borrador, o confirmar la revisión y calcular. Cada cálculo guarda una versión con el contexto completo.
5. Explorar gráficos e informe. Recuperar expedientes y consultar versiones en Análisis guardados.

El borrador matemático se guarda explícitamente; los campos no guardados no se recuperan al recargar. Los expedientes nuevos no traen pagos: los define el analista. El supuesto inicial 50 % / 50 % debe revisarse. Las fuentes registradas no se descargan ni se verifican automáticamente.

Esta entrega corresponde a A y B del prompt maestro. En esa entrega quedaban pendientes la IA local, el ejecutable y el PDF propio directo. Se aprobaron 23 pruebas automatizadas, incluyendo persistencia, revisión requerida, versiones históricas y conflictos de revisión.


### IA local revisable (primera integración de C)

Abrí **IA local y propuestas de modelado** en el coordinador. La aplicación comprueba Ollama en `http://127.0.0.1:11434`, permite activar o desactivar la asistencia y usa un modelo ya instalado. Esta entrega admite `mistral:latest` con el digest revisado en `local_ai.py`; no descarga modelos ni instala servicios.

**Proponer actores y variables** guarda antes el borrador del formulario y solicita una propuesta en segundo plano. Revisá el resumen, actores, estrategias, variables, preguntas, hipótesis y límites. Aplicar incorpora únicamente actores y estrategias al modelo y registra la propuesta. No completa pagos ni estima probabilidades. El cálculo sigue requiriendo preparación, datos completos y revisión del analista.

Cambiar el expediente o editar campos mientras se genera una propuesta impide aplicarla a un estado distinto; guardá y generá de nuevo. Los errores y propuestas se conservan en SQLite. Al reiniciar, las generaciones interrumpidas quedan marcadas como fallidas. Una generación a la vez, tiempo de respuesta limitado y contexto acotado; la interfaz informa si se usó un extracto.

Desactivar la asistencia evita nuevas solicitudes; una generación ya iniciada puede terminar. El modo guiado permanece disponible. Las propuestas no son evidencia ni predicciones validadas.

Verificado con una generación real de Mistral en 133 segundos y 33 pruebas aprobadas. El ejecutable, el PDF propio directo y los juegos secuenciales siguen pendientes.

### Árbol secuencial (primera entrega de D)

En la Mesa estratégica, el panel Árbol secuencial permite editar dos decisiones de A y dos respuestas de B por cada decisión observada. Cargá los ocho pagos, los supuestos y resolvé. El núcleo Python calcula todos los equilibrios puros perfectos en subjuegos mediante inducción hacia atrás, incluyendo empates. El gráfico permite ampliación y exploración de hojas. Confirmá la revisión para guardar una versión inmutable; el historial permite recuperarla. El botón de impresión prepara un informe específico del árbol.

Este módulo es independiente del expediente simultáneo y la IA aún no construye estos árboles. No incluye azar, información oculta, agentes ni Monte Carlo.

### Monte Carlo del árbol secuencial

Abrí **Incertidumbre y simulación Monte Carlo**, activá la simulación y elegí amplitud, 100–5000 repeticiones y semilla. Cada pago se muestrea uniformemente en base ± amplitud, de forma independiente. Los actores observan los pagos del escenario; el árbol se resuelve de nuevo en cada repetición. El gráfico muestra frecuencias de decisiones, escenarios con empates, rutas compatibles y percentiles de utilidad. Podés inspeccionar las primeras 20 repeticiones. Guardar el árbol conserva configuración y resultados; el informe de impresión incluye la simulación.

Esto explora sensibilidad de incentivos; todavía no modela agentes con memoria, conducta aprendida, pagos correlacionados ni incertidumbre oculta al decidir.

### PDF ejecutivo del árbol y Monte Carlo

Después de **Resolver y guardar versión** (o recuperar una versión del historial), aparece **Descargar PDF ejecutivo**. Exporta el modelo guardado, planes completos, árbol vectorial, pagos, supuestos y simulación si existe. El PDF identifica la versión y fecha del cálculo. Editar el formulario oculta la descarga hasta resolver y guardar de nuevo; no se exportan cambios sin guardar. Requiere ReportLab instalado en el Python que ejecuta el servidor. El informe del caso simultáneo propio sigue usando la impresión del navegador.
