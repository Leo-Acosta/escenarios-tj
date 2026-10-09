# Fase 9 · distribución Windows

Avance verificado el 9 de octubre de 2026: distribución portable Windows x64 construida y probada. No se declara cerrada la instalación asistida ni la fase 10 de calidad.

## Uso

Descomprimir **toda** la carpeta EscenariosTJ del ZIP. Ejecutar EscenariosTJ.exe: abre la interfaz local en http://127.0.0.1:8766/app/. Mantener abierta su consola; Ctrl+C detiene el servidor. No requiere Python ni Node instalados. El núcleo, React compilado, ReportLab y fuentes están incluidos. Los cálculos y PDF funcionan localmente; Ollama es opcional y sus modelos no están incluidos.

El arranque crea una base nueva en **%LOCALAPPDATA%\EscenariosTJ\escenarios.sqlite3**. No importa automáticamente bases del repositorio. Esto evita distribuir o trasladar datos privados sin una decisión del usuario. La carpeta del programa puede reemplazarse sin reemplazar la carpeta de datos.

Argumentos disponibles:

```powershell
.\EscenariosTJ.exe --version
.\EscenariosTJ.exe --no-browser
.\EscenariosTJ.exe --data-dir "C:\Mi carpeta de datos" --port 8767
```

La carpeta de datos debe ser escribible. Una segunda instancia sobre la misma carpeta se rechaza. Un puerto ocupado se rechaza antes de migrar la base; no se cambia automáticamente de puerto, porque los borradores del navegador dependen del origen. El servicio escucha únicamente en 127.0.0.1 y conserva los controles de Host/Origin.

## Actualización, recuperación y vuelta a una versión anterior

1. Descargar un respaldo desde la aplicación y conservar la carpeta del programa anterior.
2. Detener el servidor con Ctrl+C. Extraer la nueva versión en otra carpeta; no extraer sobre una aplicación en ejecución.
3. Ejecutar la nueva versión usando la misma carpeta de datos. La migración existente crea una copia previa para la transición admitida y rechaza esquemas desconocidos.
4. Si es necesario volver, detener el servidor y ejecutar el programa anterior. Si el esquema cambió, recuperar el respaldo en una carpeta de datos nueva y usar --data-dir; nunca degradar ni sobrescribir la base activa.

Para usar una base verificada y recuperada desde la interfaz, conservar el original, copiar la base recuperada a una carpeta nueva con el nombre escenarios.sqlite3 y arrancar con --data-dir apuntando a esa carpeta. Los documentos externos referenciados deben conservarse por separado. Los borradores locales no viajan dentro de SQLite.

Estas operaciones son manuales y revisables: este avance no introduce un actualizador automático ni promete compatibilidad con esquemas futuros. El ejecutable no tiene firma de código ni instalador asistido.

## Compilación y trazabilidad

Compilar primero frontend con npm run build. En un entorno de desarrollo con Python, PyInstaller y ReportLab instalados:

```powershell
powershell -NoProfile -File packaging/build-windows.ps1
```

Sólo se empaquetan módulos importados y los directorios web y frontend/dist. No se recopilan data, output, reference ni archivos de entorno del repositorio. Un control final rechaza bases SQLite y carpetas de datos privadas. El manifiesto registra SHA-256 de cada archivo; el ZIP recibe su propio archivo SHA-256. Estas huellas detectan diferencias de contenido, no acreditan autenticidad ni equivalen a firma. La construcción se puede repetir, pero no se promete identidad binaria byte a byte entre compilaciones.

Entorno de esta construcción: Windows 11 x64, Python 3.13.14, PyInstaller 6.20.0, ReportLab 4.2.5. El artefacto y dependencias binarias permanecen locales en release/, excluido de Git; código, pruebas y guía se guardan en el repositorio.

## Verificación

176 pruebas Python aprobadas, incluidas cuatro nuevas: ubicación de datos, bloqueo y liberación de instancia, puerto ocupado sin migración y manifiesto que rechaza bases privadas. Se conserva la compilación React aprobada y sus 80 pruebas de fase 5; no se modificó el frontend en este avance.

packaging/smoke-windows.py ejecutó el binario desde una carpeta sintética con PATH vacío: arranque, respuestas de /app/ y Mesa, APIs de expedientes, reproducción e informe PDF. Rechazó otra instancia, detuvo el proceso, volvió a iniciarlo y obtuvo un PDF de 82.314 bytes idéntico. Los datos son sintéticos. La parada de la prueba termina el proceso, por lo que también comprueba lectura de registros confirmados después de una terminación; no demuestra conservación de una inferencia interrumpida ni de campos no persistidos.

No se verificó todavía en una máquina limpia diferente, ni mediante instalación asistida, firma de código, impresión física o dispositivos móviles. La prueba de recursos HTTP no sustituye revisión visual de la interfaz. PyInstaller emitió avisos de importaciones opcionales; la prueba del ejecutable confirmó las rutas utilizadas, sin acreditar todas las funcionalidades opcionales.

## Estado siguiente

Fase 9: portable funcional terminada; instalación asistida y validación en Windows limpio pendientes. Fase 10: pruebas integrales de plataforma, rendimiento y experiencia de actualización pendientes. La fase 8 permanece abierta en validación empírica: no hay nueva evidencia de mejora predictiva real.
