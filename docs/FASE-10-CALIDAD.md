# Fase 10 · aceptación de plataforma

## Alcance verificable

La aceptación usa expedientes sintéticos en una base separada. No modifica datos personales ni ejecuta Ollama. Se comprueban cálculo reproducible, exportación congelada, cuatro lectores simultáneos, presupuesto de respuesta, asignaciones Python, formato A4 y compatibilidad del núcleo Python 3.11/3.13 en Windows/Linux. La interfaz distribuida sigue orientada a Windows x64; comprobar el núcleo en Linux no equivale a distribuir un instalador Linux.

La prueba repetible es `python packaging/quality-platform.py --output "tmp/calidad con espacios" --samples 10`. La carpeta debe ser nueva. Conserva base de prueba, informe HTML/PDF, registro del servidor y `acceptance.json`; ningún dato de esta carpeta debe añadirse a Git. Una muestra de calentamiento queda fuera del cálculo. Se publican diez duraciones por operación, mediana y percentil 95 por rango más cercano; con diez muestras el P95 es el máximo. El presupuesto previo es 3 segundos para las operaciones medidas y 32 MiB de asignaciones Python para la simulación máxima admitida de 5.000 iteraciones. No son un SLA de hardware ni una medición de toda la memoria del proceso.

GitHub Actions repite la prueba y toda la suite Python en cuatro combinaciones Windows/Linux y Python 3.11/3.13. La distribución Windows conserva su recorrido de instalación, actualización bloqueada con la aplicación abierta, reinstalación y desinstalación en dos runners independientes, con datos preservados. No hay descarga ni promoción automática de actualizaciones.

## Impresión y compatibilidad visual

Los informes ejecutivos utilizan versiones congeladas, SVG y PDF vectorial. Las pruebas verifican tamaño A4, presencia de capítulos, identidad de exportaciones concurrentes y reproducción sin una nueva inferencia. La inspección visual y las limitaciones concretas de navegador se documentarán en la evidencia de cierre. No se certifica una impresora física, un dispositivo móvil real ni todos los navegadores por comprobar un tamaño de ventana.

## Criterios de cierre

- Suite Python, contratos TypeScript y compilación aprobados.
- Mediciones reproducibles bajo los presupuestos y sin perder trazabilidad.
- PDF A4 con capítulos legibles y contenido conservado.
- Interfaz revisada en tamaños de escritorio y tamaños reducidos realmente observados.
- Matriz de compatibilidad ejecutada; fallos corregidos y evidencia conservada.
- Actualización y continuidad cubiertas por el recorrido de distribución existente.
- Límites externos visibles: impresión física, dispositivos reales, firma del ejecutable y validación predictiva empírica.

La fase 8 permanece abierta hasta incorporar observaciones independientes. Una prueba sintética aprobada no demuestra mejores predicciones.
