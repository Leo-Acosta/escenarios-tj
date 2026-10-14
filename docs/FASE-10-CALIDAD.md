# Fase 10 · aceptación de plataforma

## Actualización del 13 de octubre de 2026

Se amplió la aceptación con Chromium y Firefox: giro WebGL 3D real, reproducción,
vista de 390 px sin desbordamiento y estilos de impresión aprobados. Chromium
generó cinco páginas científicas y ocho ejecutivas A4, revisadas visualmente.
Ver [evidencia y distribución científica](CIERRE-CIENTIFICO-WINDOWS.md).
La aceptación entre esos motores y el PDF de impresión queda verificada;
vista previa nativa Edge/Safari/Firefox, impresora física y dispositivos reales
siguen fuera del alcance probado. Los resultados históricos siguientes no se
presentan como una prueba nueva del instalador científico en runners limpios.

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

## Resultados del 9 de octubre de 2026

La [evidencia conservada](verification/platform-2026-10-09.json) contiene todas las duraciones, entornos, resultados y referencias. El commit probado es `535b6e25e9d754f0917c117d4c998c48b28f0206`. [CI de compatibilidad](https://github.com/Leo-Acosta/escenarios-tj/actions/runs/37974763576): los cuatro trabajos aprobaron 176 pruebas Python y los presupuestos de calidad. Localmente pasaron además 80 contratos TypeScript, compilación y seis pruebas del informe después de modificar los estilos.

La [reconstrucción y aceptación Windows](https://github.com/Leo-Acosta/escenarios-tj/actions/runs/37974763585) aprobó ambos runners en ese mismo commit: compilación, portable, instalador, rechazo de actualización con la aplicación abierta, reinstalación y desinstalación sin eliminar la base. El segundo runner instaló el artefacto descargado sin preparar Python ni Node. Los binarios de este commit se encuentran en los artefactos de esa ejecución; la carpeta `release/` local conserva la construcción anterior de fase 9 y no se presenta como una reconstrucción local nueva.

| Operación local, diez muestras | P95 |
|---|---:|
| Monte Carlo, 5.000 iteraciones | 124,64 ms |
| Reproducción HTTP del informe | 201,14 ms |
| HTML A4 | 27,34 ms |
| PDF completo | 204,42 ms |

Los valores de la tabla se redondean hacia arriba. Doce solicitudes de PDF con cuatro lectores devolvieron bytes idénticos. El PDF completo tiene 19 páginas A4; se inspeccionaron visualmente las páginas 4, 6, 13 y 19: matriz, agentes, evaluación y trazabilidad legibles. La fase 6 conserva su revisión previa página por página; esta comprobación nueva no la reemplaza ni afirma haber inspeccionado otra vez todas las páginas.

Interfaz React inspeccionada en anchos realmente observados de 780 y 480 px. En 480 px no hubo desbordamiento horizontal y se pudo navegar al compositor y seleccionar un informe congelado. La herramienta duplicaba el tamaño solicitado y aplicaba un mínimo de 480 px: no se acredita una prueba de 390 px. La corrección de estilos añade foco visible, reducción de movimiento, ocultación obligatoria de paneles inactivos al imprimir y tablas de ancho fijo. Las reglas del informe para pantallas pequeñas quedan restringidas a `screen`, para evitar interferir con A4.

La impresión HTML nativa **no quedó verificada**. La revisión automática rechazó inicialmente inspeccionar la ventana personal de Edge. Después de que el usuario abrió el informe sintético en Brave, Computer Use detuvo la sesión por no poder confirmar su URL con suficiente confianza. No se eludió esa restricción. No se realizaron más acciones de interfaz; las pruebas restantes fueron de código y CI.

**Estado: implementación y aceptación automatizada terminadas; cierre integral de fase 10 abierto por aceptación visual nativa pendiente.** Para cerrar sin reservas: verificar el informe en vista previa A4 de un navegador controlable, guardar su PDF, inspeccionar paginación y contrastar capítulos; completar recorridos en otros motores de navegador. Impresora física y móviles reales requieren disponibilidad de esos dispositivos y permanecen fuera de la evidencia actual. No hay acreditación WCAG, firma Authenticode del producto ni una prueba de carga de Ollama. La identidad binaria PDF se compara dentro de cada entorno, no entre fuentes Windows y Linux.
