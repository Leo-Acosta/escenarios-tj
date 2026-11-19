# Aceptación y distribución del estudio visual · 17/11/2026

Construcción de fase 12 sobre el cierre funcional `f1e2f06`. Este registro separa pruebas completadas y verificaciones pendientes. La demostración utiliza sólo datos sintéticos.

## Ejecutable portable

Reconstruido con PyInstaller, React compilado y entorno científico R/CRAN más Python/Keras/PyTorch CPU. Ollama y sus modelos siguen siendo opcionales y no se incluyen. La construcción y el manifiesto excluyen bases y documentos privados.

`packaging/smoke-windows.py` amplía el recorrido de distribución existente: crea una red visual con posiciones concretas, conserva un escenario, emite el informe, consulta las APIs instaladas y reproduce sin inferencia. Lo repite tras reiniciar, con PATH vacío. También verifica originales documentales de más de 3 MiB, ZIP documental, informe PDF idéntico y rechazo de una segunda instancia.

Resultado local portable: aprobado. Datos y registros de prueba en `tmp/fase12-portable-smoke`, excluidos de Git. No se usó EDESUR.

## Navegadores e impresión

La interfaz del navegador integrado se operó en la fase anterior. En esta aceptación la medición de ancho solicitada a 390 px devolvió 780 px efectivos, sin desbordamiento horizontal del documento. No se acredita móvil de 390 px.

El PDF vectorial de demostración fue revisado en A4 en la fase anterior. Esto no reemplaza la impresión HTML nativa.

Se solicitó una ventana separada de Edge o Brave. La revisión automática rechazó inspeccionar primero Brave con Zoom/SSO y luego Edge con otras tres páginas personales. No se inspeccionaron esas páginas ni se eludió el rechazo. La captura del navegador integrado no proporciona una vista fiable completa del lienzo. Después se pudo controlar una ventana separada autorizada de Edge. Se verificaron arrastre físico de Cooperativa vecinal, creación de conexión mediante puertos hacia Consejo de control, conversión a vínculo dirigido y guardado como nueva versión. Consulta independiente del registro confirmó 19 entidades, 28 vínculos, nueva posición y dirección. La base original no se modificó.

El arrastre de un solo movimiento necesitó umbral cero; además los cambios de cámara y posición usan actualizaciones sobre el estado más reciente para no pisarse. Los formularios siguen disponibles. Al navegar al informe HTML, Computer Use volvió a detener el control por no confirmar la URL. No se insistió ni se eludió esa restricción. Impresión HTML nativa y aceptación entre motores siguen pendientes. No se afirma certificación móvil, accesibilidad completa ni impresión física.

## Instalador

El script de compilación admite ahora un nombre de salida explícito para conservar artefactos previos; valida el nombre y produce su SHA-256 correspondiente. El paquete incluye la guía de estudio visual en construcciones nuevas. La prueba de instalación QA usa otro AppId y una carpeta sintética: nunca reemplaza automáticamente la instalación real.

Instalador final: **EscenariosTJ-0.1.0-Fase12-Setup.exe**, 434.348.987 bytes, disponible localmente en `release/`, excluido de Git. SHA-256 verificado:

`42f2c0e3048a240945ac0150087e672982ccc7d36851b64172968f15c904e328`

Variante QA con AppId separado: instalación, verificación de 24.867 archivos, ejecutable y R con PATH vacío y sin configuración externa de R/Python, rechazo de ruta demasiado larga, rechazo de actualización con aplicación abierta, reinstalación y desinstalación aprobados. La base sintética se conservó idéntica. R ejecutó el chequeo de disponibilidad y carga de los diez paquetes del laboratorio; no se repitió aquí el entrenamiento profundo científico de fases anteriores.

La variante QA y el paquete final tienen idénticos ejecutables, entorno científico e interfaz. La única diferencia de contenido es la guía de estudio visual actualizada. Los manifiestos se compararon antes de entregar el instalador. Una segunda ejecución del recorrido portable final también aprobó.

[Registro de aceptación](verification/visual-study-distribution-2026-11-17.json). Pruebas de interfaz: 85 contratos TypeScript aprobados y compilación tsc/Vite correcta. Cinco controles de lanzador aprobados en la aceptación previa inmediata; las 204 pruebas Python del cierre funcional permanecen registradas en la guía de fase 12. Los nuevos recorridos de distribución se ejecutaron sobre el paquete reconstruido.

La instalación real del usuario no se reemplazó. EDESUR quedó intacto: verificación SHA-256 de su base principal antes y después. El instalador contiene programa y entornos, sin facturas, fotos, bases, expedientes ni documentos privados del proyecto. Al actualizar, cerrar la aplicación y conservar un respaldo según la guía Windows; una instalación nueva usa su carpeta de datos local y no importa automáticamente expedientes del repositorio.

**Estado:** reconstrucción y aceptación local del instalador completas. Arrastre, conexión por puertos y persistencia aprobados en Edge; compatibilidad visual con otros motores y paginación HTML nativa pendientes por el bloqueo descrito. El PDF vectorial A4 mantiene la verificación previa independiente. Impresión física, firma de código y nuevos runners Windows limpios no se acreditan en este cierre. La validación predictiva real P-EMP-01 sigue abierta; estas pruebas no demuestran mejora de predicción.


## Pulido de interacción · 19/11/2026

Se unificó la persistencia de desplazamientos mediante eventos de posición final de React Flow. Incluye flechas del teclado y fin de arrastre, excluye clics/selección, posiciones sin cambio y cuadros intermedios de arrastre. Se validan posiciones finitas y límites de coordenadas; no se crean pasos de historial por seleccionar una entidad. Las indicaciones accesibles de movimiento están en español. El formulario de guardado utiliza campos de ancho completo, grilla adaptable y acciones separadas.

87 pruebas TypeScript aprobadas (dos nuevas regresiones de eventos de movimiento), compilación tsc/Vite correcta. En navegador integrado con datos sintéticos: selección sin cambio pendiente; flecha derecha X=120 a X=125; Deshacer a 120, Rehacer a 125; revisión, guardado y reapertura con X=125 conservado. Columnas del formulario medidas desde DOM con anchos coincidentes. La captura de pantalla falló, por lo que no se declara una revisión visual completa nueva.

El arrastre físico y los puertos tienen la aceptación de Edge del 17/11; no se repitió esa interacción física tras este ajuste del manejador. Los eventos de final de arrastre están incluidos en las pruebas de contrato. La impresión HTML nativa y otros motores continúan pendientes. La base real no se usó para las pruebas.

Este ajuste está en el código y la interfaz compilada local. El instalador del 17/11 se conserva con su huella y aceptación originales; no se presenta como si ya incluyera este pulido. Antes de publicar otro instalador corresponde repetir el arrastre físico y luego empaquetar el nuevo frontend con su registro de aceptación.


## Cierre de distribución r2 · 19/11/2026

**Implementación y distribución de fase 12 cerradas en el alcance documentado; aceptación visual total aún limitada.** El instalador r2 incorpora el pulido de teclado, el manejador unificado de posiciones y el formulario adaptable del commit `6eb40b5`, manteniendo el entorno científico local R/CRAN y Python/Keras/PyTorch CPU. El instalador anterior queda conservado.

Artefacto local: `release/EscenariosTJ-0.1.0-Fase12-r2-Setup.exe`, 434.533.099 bytes, con archivo `.sha256`. Huella verificada: `5e16322caee7cb44bf6081bf0a77b7679a1d3c05fa204104a241023c8ca308be`. Los manifiestos completos del paquete QA y del final coinciden: 24.885 archivos, incluida la interfaz actual. Código, pruebas y documentación se publican; ejecutables, bases y expedientes privados no se suben a Git.

### Aceptación realizada

- Arrastre físico repetido en Edge sobre el nuevo manejador: Hospital Central cambió de posición, se guardó una nueva red y una lectura independiente confirmó las coordenadas nuevas. Los 19 nodos y 28 vínculos se conservaron. Se observó también el formulario con campos de ancho completo. No se alteraron escenarios congelados por editar la red.
- El informe se emitió desde la interfaz y se abrió mediante su enlace de previsualización, sin introducir una URL en la barra de direcciones. Su contenido procede de las fuentes congeladas del escenario seleccionado, no se actualiza automáticamente al editar otra versión de red.
- PDF vectorial de ese informe: 14 páginas A4, reproducción sin inferencia nueva, todas las páginas renderizadas y revisadas en planchas; red y árbol inspeccionados ampliados. Copia sintética imprimible local en `output/pdf/Verificacion-estudio-visual-A4-r2.pdf`, excluida de Git.
- 87 pruebas TypeScript y compilación tsc/Vite aprobadas. El recorrido del ejecutable final con PATH vacío pasó dos ciclos y comprobó documentación, SVG, posiciones, escenarios y PDF congelado idéntico. Además creó una red, un escenario y un informe por la API del ejecutable instalado y reprodujo ese informe.
- Instalación QA con AppId separado: 24.885 archivos verificados, ejecutable y carga de paquetes R aprobados con PATH vacío; ruta demasiado larga y actualización con aplicación abierta rechazadas. Reinstalación y desinstalación conservaron la base sintética idéntica. No se sustituyó la instalación real del usuario. La base original mantuvo su SHA-256 del inicio de este recorrido.

### Límites que permanecen abiertos

Al invocar Ctrl+P en el informe, Computer Use detuvo el control por no confirmar la URL de la vista de impresión. Se dejó de operar el navegador y se completaron las otras verificaciones. **No se declara aprobada la paginación HTML nativa ni la impresión física.** El PDF A4 sí tiene verificación independiente.

No se probó la versión actual en otros motores o navegadores: no se presenta el recorrido de Edge como certificación de Firefox, WebKit o Brave. La conexión por puertos conserva su aceptación anterior; el arrastre actual y el teclado sí cuentan con las verificaciones nuevas descritas. No se acredita firma de código, un nuevo runner Windows limpio ni mejora predictiva real; P-EMP-01 permanece separado.

[Registro de aceptación r2](verification/visual-study-r2-2026-11-19.json). Los registros anteriores siguen disponibles y no se reescriben como si hubieran probado esta revisión.

### Repetir la construcción

El paquete científico existente requiere el Python 3.12 preparado para sus bibliotecas CPU. Compilar `frontend` primero; luego puede ejecutarse `packaging/build-windows.ps1 -Python <python-del-entorno> -IncludeScientific -SkipArchive` y `packaging/build-installer.ps1 -Python <python-del-entorno> -OutputName EscenariosTJ-0.1.0-Fase12-r2-Setup`. `-SkipArchive` conserva el manifiesto y su validación, evitando generar además un ZIP cuando sólo se necesita el instalador. El comportamiento predeterminado que genera ZIP se conserva. Se comprobó la sintaxis PowerShell del script; el instalador r2 se ensambló desde el paquete científico ya validado, actualizando sus recursos React y verificando de nuevo el manifiesto.
