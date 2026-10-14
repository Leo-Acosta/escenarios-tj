# Verificación 3D, impresión y distribución científica

Actualización: 13 de octubre de 2026. Pruebas realizadas exclusivamente con datos sintéticos.

## Navegadores y presentación

Prueba reproducible: `packaging/verify-browsers.py` con Playwright 1.63.0,
Chromium 153.0.8010.12 y Firefox 155.0 en Windows.

- El iframe aislado cargó el canvas WebGL y el gráfico Plotly.
- El arrastre cambió la cámara: se verificó una interacción real, no solo la existencia del canvas.
- Reproducción desde la interfaz aprobada, sin inferencia nueva.
- Vista de 390 × 844 px sin desbordamiento horizontal en ambos motores.
- Botones de impresión ocultos en el medio de impresión de ambos motores.
- Chromium generó cinco páginas científicas y ocho ejecutivas A4; todas midieron aproximadamente 595 × 842 puntos. Se renderizaron y revisaron las trece páginas: texto y gráficos íntegros.
- Capturas de pantalla y registros conservados localmente en `tmp/browser-acceptance-final`; intentos anteriores también conservados.

Alcance: navegadores de prueba aislados, sin perfiles personales. Firefox usa el
motor distribuido para pruebas por Playwright. No se acredita la vista previa
nativa de Firefox, Edge o Safari, ni una impresora física. La verificación de
impresión PDF de Chromium y estilos Firefox no equivale a esas comprobaciones.
No se acredita compatibilidad con todos los GPU ni dispositivos móviles reales.
Se mantienen gráficos 2D como alternativa.

## Distribución científica Windows x64

El paquete incluye R 4.6.1, los paquetes CRAN usados y Python 3.12 independiente
con Keras 3.12.0/PyTorch 2.14.1 CPU. La aplicación busca el entorno junto al
ejecutable instalado, conserva licencias y metadatos y no requiere R/Python en PATH.
Ollama y sus modelos LLM siguen siendo opcionales y no están incluidos.

El paquete CPU excluye las cabeceras C++ de desarrollo de PyTorch; no permite
compilar extensiones C++ personalizadas. Se recargó la red profunda guardada y
se obtuvo una salida finita después de esa exclusión. Se conservan las licencias.
El instalador rechaza destinos de más de 80 caracteres antes de extraer archivos,
para evitar el límite de rutas de Windows. El destino predeterminado es válido.
El primer intento QA en una ruta larga falló y revirtió su instalación; ese
intento se conserva en los registros y no se cuenta como aceptación aprobada.

La aceptación final del instalador QA aprobó: 27.515 archivos contrastados con el
manifiesto, R detectado desde la aplicación instalada, dos arranques sin Python
en PATH con PDF congelado idéntico, rechazo de actualizar una aplicación abierta,
reinstalación y desinstalación conservando la base sintética. Se comprobó el rechazo
preventivo de rutas largas. Pasaron 191 pruebas Python y los controles de
distribución se repitieron después del ajuste final.
La [evidencia sintética](verification/scientific-platform-2026-10-13.json) conserva
versiones, resultados, pruebas de navegadores y huella del instalador. Binario
local: `release/EscenariosTJ-0.1.0-Setup.exe`, aproximadamente 434 MiB; no contiene
datos EDESUR y no se sube automáticamente al repositorio.

Se ejecutó el paquete autónomo en una carpeta sintética: cuatro métodos,
53 archivos de resultados, evaluación y reproducción aprobadas. Coincidieron los
resultados con la aceptación original. Este resultado no demuestra mejora real.

```powershell
& packaging/build-windows.ps1 -Python ruta\python.exe -IncludeScientific
& packaging/build-installer.ps1 -Python ruta\python.exe
```

La construcción científica actual requiere Python 3.12 y las dependencias de
`packaging/requirements-build.txt`. R y el entorno Keras deben estar instalados
previamente mediante `scripts/install-scientific.ps1`.

`packaging/bundle-scientific.py` copia únicamente bibliotecas instaladas y crea
un intérprete independiente: no traslada un venv con referencias al equipo original.
`release_manifest.py` conserva huellas de todos los archivos y rechaza bases
SQLite y carpetas privadas; admite los datos públicos incluidos en los paquetes.
El manifiesto usa lectura incremental para las bibliotecas grandes.

El instalador no tiene firma digital. La verificación local no sustituye una
prueba del paquete científico en un segundo Windows limpio ni una revisión de
licencias antes de distribuir binarios públicamente. Las licencias originales
permanecen incluidas; fuentes oficiales: [R](https://www.r-project.org/Licenses/),
[CRAN](https://cran.r-project.org/), [Keras](https://github.com/keras-team/keras),
[PyTorch](https://github.com/pytorch/pytorch).

## Incorporación de EDESUR: trabajo pendiente

No se importó evidencia personal en las pruebas ni se incluyó en el instalador o GitHub.
El caso puede analizarse documentalmente sin esperar a entrenar un predictor.

1. Incorporar las facturas originales y el cálculo de aparatos en un expediente privado. Revisar extracción contra cada página: período, días, kWh, lecturas, lectura real/estimada, categoría, tarifas, subsidios, cargos, impuestos y saldos anteriores.
2. Vincular fotos del mismo medidor con número de serie, fecha/hora de captura y lectura legible. Verificar las fechas y la diferencia de once días; recalcular kWh/día y comparar períodos equivalentes. Una lectura reciente no reconstruye por sí sola consumos anteriores.
3. Conservar reclamos escritos, constancias, respuestas, fechas, pagos y ajustes; registrar resultados posteriores sin reemplazar la evidencia inicial.
4. Definir el resultado objetivo: discrepancia de consumo/cargo, corrección de factura, devolución y tiempo de respuesta son objetivos distintos. No asignar probabilidades de éxito judicial sin evidencia apropiada.
5. Construir escenarios y restricciones con supuestos revisados; separar hechos documentados, declaraciones y pendientes. Las rutas administrativas/judiciales requieren fuentes vigentes y revisión jurídica específica.
6. Para medir mejora predictiva, reunir observaciones suficientes e independientes, reservar una prueba temporal y comparar contra una referencia congelada. Un expediente individual y un consumo diario estimado no bastan para entrenar o validar generalización.

La fase 8 permanece abierta en validación empírica. No se concluye sobrefacturación,
fraude, responsabilidad o éxito de una demanda a partir del ejemplo sintético.

El comparador científico actual evalúa resultados binarios (0/1), por ejemplo
corrección de una factura dentro de un horizonte definido. Predecir kWh o importes
continuos requiere ampliar modelos y métricas a regresión/series temporales;
no se presenta el clasificador existente como un predictor de consumo doméstico.
La conciliación documental y aritmética de este expediente puede realizarse ahora,
sin convertirla en una demostración de precisión estadística.
