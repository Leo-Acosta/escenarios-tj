# Escenarios TJ

Proyecto para construir un laboratorio de escenarios multiagente en Python, con interfaz y documentación en español y almacenamiento local.

Estado: laboratorio funcional en Python y primera fase de migración a React + TypeScript. Incluye expedientes persistentes, versiones, matrices, árboles secuenciales, simulaciones y documentos. La nueva interfaz de consulta está en `/app/`; la mesa estratégica existente permanece en `/`. No es todavía una entrega premium completa.

Para construir la nueva interfaz: ejecutar `npm ci`, `npm test` y `npm run build` dentro de `frontend`, y luego iniciar el servidor Python. Ver [arquitectura y fases](docs/ARQUITECTURA-PREMIUM.md).

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

### IA local para decisiones secuenciales

El panel **Asistente local para el árbol** recibe una descripción del caso y el borrador completo. Activá Mistral en el coordinador y usá **Proponer decisiones por etapa**. La generación conserva una propuesta separada con actores, tres pares de decisiones, variables, preguntas, hipótesis y límites. Aplicar cambia solamente nombres y decisiones del borrador; revisá nuevamente la correspondencia de los pagos, resolvé y guardá. Si cambian descripción, modelo u opciones de simulación antes de aplicar, se exige una propuesta nueva. Las versiones guardadas y PDF conservan la procedencia de la IA. La propuesta no acredita evidencia ni genera pagos automáticamente.

### Agentes con memoria: juegos repetidos

En la Mesa estratégica, **Agentes con memoria** toma la matriz del formulario del caso simultáneo. Elegí una política para cada actor, 1–500 rondas, semilla y error de ejecución. Las seis políticas usan alternativas por índice: fija 1, fija 2, copiar la última alternativa rival, cambiar permanentemente tras observar la alternativa 2, mejor respuesta a frecuencias observadas y aleatorio 50/50. Las políticas de memoria comienzan con alternativa 1.

El gráfico muestra pagos acumulados. El control de ronda revela intención, acción ejecutada, pago y memoria previa de ambos agentes. Guardar exige revisión y conserva la matriz, opciones y todas las rondas; el historial recupera cada corrida sin cambiar el formulario principal. p/q del modelo base no se usan. El error invierte cada decisión con la frecuencia configurada y el rival observa la acción ejecutada. Estas conductas son supuestos, no predicciones aprendidas ni decisiones de un LLM. La exportación PDF de agentes sigue pendiente.

### Exportar corridas de agentes

En una corrida guardada o recuperada aparecen **Descargar PDF ejecutivo** y **Exportar todas las rondas (CSV)**. El PDF incluye resumen, matriz, evolución vectorial, supuestos y una muestra de las primeras/últimas diez rondas sin duplicados. El CSV (UTF-8 con BOM y separador punto y coma) incluye todas las rondas, dos filas por ronda: actor, política, intención, acción ejecutada, pago, acumulado, motivo y memoria previa. Los índices 1/2 corresponden a las alternativas del actor. Las exportaciones usan la corrida inmutable, sin volver a simular. El PDF requiere ReportLab; CSV no requiere dependencias externas.

## Comparador de políticas

La mesa estratégica incluye una matriz interactiva de 36 combinaciones. Permite 1–100 rondas, 1–10 semillas consecutivas y error de ejecución. Muestra utilidad por actor, media y desviación poblacional entre semillas. Las comparaciones revisadas se guardan en SQLite con la matriz original; cada repetición puede reproducirse en el explorador de agentes. Las simulaciones dependen de los supuestos y no están calibradas como predicciones reales.

## Informe ejecutivo de comparaciones

Cada comparación guardada ofrece Descargar informe ejecutivo PDF. El documento vectorial conserva UUID, matriz, semillas, medias y dispersión por actor, rango frente a seis rivales y supuestos. No presupone probabilidades de las políticas rivales. Requiere ReportLab, igual que los demás informes.

## Explorador de pagos y equilibrios

En la mesa estratégica, elegí uno de los ocho pagos y un rango para explorar 101 valores. El gráfico muestra utilidades esperadas por estrategia de A o B; el deslizador y los botones de cambio permiten inspeccionar equilibrios, empates y mejores respuestas. El caso original y p/q permanecen constantes. Los intervalos entre muestras no son umbrales exactos. La exploración es temporal, sin persistencia ni PDF propio.

## Versiones del explorador de incentivos

Los barridos revisados ahora se guardan en SQLite mediante Explorar y guardar versión, con UUID, fecha, motor, matriz original, rango y supuestos. El historial permite recuperar los 101 escenarios sin modificar el caso principal. Cada versión ofrece CSV con utilidades, mejores respuestas, equilibrios y probabilidades del mixto interior. La exportación PDF propia del barrido sigue pendiente.

## PDF ejecutivo de incentivos

Cada barrido guardado ofrece Descargar informe ejecutivo PDF junto al CSV. El informe vectorial conserva UUID, configuración, matriz, gráficos de utilidades separados por actor, extremos del rango, intervalos de cambio y supuestos. Requiere ReportLab. La extensión crece si los supuestos o etiquetas requieren más páginas.

## Centro de análisis guardados

La vista Análisis guardados reúne seis tipos: matrices libres, versiones de expediente, árboles, agentes, comparaciones e incentivos. Busca por título, actor o identificador, filtra por tipo y pagina de a 30 versiones sobre todo el historial disponible. Consultar versión muestra el modelo y resumen sin modificar formularios. Ofrece PDF y CSV para los módulos que ya tienen exportación. Los accesos anteriores y expedientes en preparación permanecen en un desplegable.

## Comparación entre versiones

En el Centro de análisis, las tarjetas de matrices libres y versiones de expediente ofrecen Usar como base y Usar para comparar. Se requiere coincidencia de nombres y posiciones de actores/estrategias y confirmación de escalas equivalentes. El contraste muestra pagos y p/q modificados, utilidades antes/después, descomposición aritmética por pagos y probabilidades, equilibrios que aparecen/desaparecen y supuestos. La atribución cambia primero pagos y después probabilidades; no identifica efectos causales. La comparación es temporal, sin PDF ni persistencia propios.
