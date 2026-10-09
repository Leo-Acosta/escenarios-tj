# Fase 9 · distribución Windows

Cierre funcional del 9 de octubre de 2026: distribución portable e instalador Windows x64 construidos y probados localmente y en dos runners Windows independientes. Fase 9 cerrada en este alcance; fase 10 permanece separada.

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

Estas operaciones son manuales y revisables: no hay actualizador automático ni promesa de compatibilidad con esquemas futuros. El instalador asistido instala por usuario, no cierra procesos ni borra la carpeta de datos. El ejecutable y el instalador del producto no tienen firma de código.

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

La instalación asistida se verificó localmente. No se acredita firma de código, impresión física ni comprobación en dispositivos móviles. La prueba de recursos HTTP no sustituye revisión visual de la interfaz. PyInstaller emitió avisos de importaciones opcionales; la prueba del ejecutable confirmó las rutas utilizadas, sin acreditar todas las funcionalidades opcionales.

## Estado siguiente

Fase 9 cerrada funcionalmente: portable, instalación asistida, reinstalación, desinstalación con datos conservados y recorrido en dos runners Windows nuevos aprobados. Fase 10: pruebas integrales de plataforma, rendimiento y experiencia de actualización pendientes. La fase 8 permanece abierta en validación empírica: no hay nueva evidencia de mejora predictiva real.

## Instalador asistido

Archivo: EscenariosTJ-0.1.0-Setup.exe. Asistente en español, instalación por usuario sin solicitar administración, carpeta predeterminada %LOCALAPPDATA%\Programs\EscenariosTJ, acceso en el menú Inicio y acceso opcional al escritorio. Abrir la aplicación al terminar es opcional. Desinstalar desde Windows elimina los archivos instalados y accesos; conserva %LOCALAPPDATA%\EscenariosTJ y los datos personalizados fuera del programa. Se rechaza elegir la carpeta de datos predeterminada como destino de instalación.

Cerrar la aplicación antes de reinstalar o actualizar. La comprobación de archivo en uso rechaza la operación sin terminar procesos. Descargar antes un respaldo; el instalador no migra bases ni prepara una restauración automática. Reinstalar la misma versión se probó como operación idempotente sobre los archivos del programa. No se acredita un cambio entre versiones de esquema futuro.

Construcción con Inno Setup 6.7.3 del proveedor oficial. La firma del compilador descargado se comprobó como válida, publicada por Pyrsys B.V.; esto no firma el producto construido. [Descarga oficial](https://jrsoftware.org/isdl.php), [instalación sin administración](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm).

~~~powershell
powershell -NoProfile -File packaging/build-installer.ps1 -Compiler "ruta\ISCC.exe"
~~~

El script verifica el paquete portable, compila el instalador y genera SHA-256. packaging/windows-installer.iss define la instalación. La variante QA usa otro AppId para no sustituir una instalación real. packaging/smoke-installer.py prueba archivos, ejecutable sin Python en PATH, PDFs congelados, bloqueo al actualizar abierto, reinstalación y desinstalación, comparando la base sintética. packaging/smoke-clean-windows.ps1 hace otra prueba desde PowerShell, sin Python ni Node en PATH. Los dos recorridos locales aprobaron.

## Aceptación independiente

La automatización .github/workflows/windows-distribution.yml construye desde Git en un runner Windows nuevo, ejecuta pruebas, compila portable e instalador y prueba la instalación QA. Un segundo runner descarga el artefacto, sin pasos de preparación de Python/Node ni compilación, e instala, calcula un ejemplo sintético, exporta PDF, reinstala y desinstala con PATH vacío, conservando la base. Los runners tienen herramientas preinstaladas del proveedor: el PATH vacío comprueba independencia de esos ejecutables; no equivale a certificar toda configuración posible de Windows de escritorio.

El primer intento detectó pypdf ausente de las dependencias declaradas de pruebas. Se corrigió; se conservan sus registros. Dos ejecuciones intermedias se cancelaron al quedar reemplazadas por la final. Se corrigió también el uso de Invoke-WebRequest en Windows PowerShell 5.1, verificado localmente. La firma comercial del producto y la matriz de dispositivos/Windows de escritorio corresponden a decisiones de distribución y calidad posteriores.

### Resultado final independiente

[GitHub Actions · ejecución 37972765418](https://github.com/Leo-Acosta/escenarios-tj/actions/runs/37972765418) terminó con **success** sobre el commit 7f41cd4. Primer job: frontend, integración Python, portable, compilador firmado, instalador QA y recorrido completo aprobados. Segundo job: instalación en otro runner, sin preparar Python/Node, cálculo sintético, PDF, reinstalación y desinstalación aprobados. Se descargó y verificó el registro del segundo job: installerVerified, runtimePathEmpty, pdfExported y dataPreserved verdaderos; synthetic verdadero. Artefacto de aceptación 11637951398.

Las ejecuciones descartadas permanecen consultables en Actions. Los artefactos de construcción tienen retención de 14 días; el registro de aceptación y el enlace de ejecución se conservan en Git. Los ejecutables locales quedan en release/. GitHub no incluye datos reales. No se acredita mejora predictiva por estos ensayos.
