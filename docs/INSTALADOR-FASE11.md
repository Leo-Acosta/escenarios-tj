# Instalador actualizado · fase 11

Verificación del 14 de octubre de 2026 en Windows x64 local. Instalador 0.1.0 reconstruido desde el cierre documental 043c0f6; se conserva AppId y ruta por usuario para actualizar la instalación existente. El número de versión sigue siendo 0.1.0: identificar esta construcción mediante SHA-256, no solo por el nombre.

## Resultado

- Ejecutable y React actualizados, R y bibliotecas científicas CPU incluidos. Ollama y modelos LLM no incluidos.
- Instalador definitivo: release/EscenariosTJ-0.1.0-Setup.exe, 434085732 bytes. SHA-256: 696b5529e48aa811997e6ecac86ea2b24e5a510125e27d019d6f91ce61fc0483. Archivo .sha256 adjunto localmente.
- Manifiesto de 24845 archivos verificado en la instalación QA. Variante QA con AppId independiente; no sustituye una instalación del usuario.
- Dos arranques sin Python en PATH, rechazo de segunda instancia, original documental de más de 3 MiB idéntico, registro congelado y ZIP idénticos, PDF ejecutivo reproducible.
- R disponible desde el paquete instalado. Instalación, reinstalación y desinstalación aprobadas; datos sintéticos conservados. Se rechaza actualización con aplicación abierta y ruta demasiado larga antes de instalar.
- Copia SQLite privada del expediente real obtenida por backup transaccional: exportación del registro congelado idéntica al original, ZIP accesible, nuevo arranque después de reinstalar, datos conservados después de desinstalar. No se hizo inferencia ni se modificó la base de origen. Resultados privados y documentos excluidos de Git.

## Uso y conservación

Cerrar la aplicación antes de actualizar. Instalar en la ruta predeterminada del usuario; si se elige otra, actualizar cualquier acceso personalizado. La carpeta del programa está separada de los datos. La carpeta predeterminada de datos es %LOCALAPPDATA%/EscenariosTJ. Actualizar o desinstalar conserva esa carpeta; el instalador no incorpora expedientes personales.

Quien utilice datos en otra carpeta debe iniciar EscenariosTJ.exe con --data-dir seguido de la carpeta existente que contiene escenarios.sqlite3. Cerrar cualquier servidor o instancia que use esa misma base antes de abrirla. Se entregó un acceso privado para la carpeta del proyecto, sin incluirlo en el paquete. Conservar también un respaldo SQLite fuera de la carpeta del programa. No abrir las bases con dossier_blobs mediante instaladores anteriores.

## Límites y pendientes

Prueba automatizada en este Windows; no se repitió este nuevo paquete en un Windows limpio ni se hizo revisión visual completa del asistente nativo. Sin firma digital. Los artefactos binarios son locales, no se publicó una release GitHub. El formato de datos mantiene los límites documentados (5 MiB por archivo, 8 MiB por expediente, 20 MiB por respaldo).

El caso real sigue requiriendo actas, comprobantes e imputación de pagos, aclaración técnica, reclamo formal y respuesta escrita. El PDF original de cálculo doméstico no está accesible; las copias secundarias están identificadas. No se acredita mejora predictiva ni se concluye el conflicto jurídico por instalar el programa. P-EMP-01 permanece pendiente.
