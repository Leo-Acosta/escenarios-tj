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
