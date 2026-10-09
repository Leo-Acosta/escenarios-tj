# Fase 11 Expediente documental y seguimiento real

Implementación del 9 de octubre de 2026. Núcleo Python y SQLite, interfaz React/TypeScript blanca y azul marino. Puede usarse con un expediente en preparación, sin matriz calculada. No incorpora automáticamente información del caso EDESUR ni envía reclamos a terceros.

## Recorrido y aceptación

1. Crear o seleccionar un expediente en React y abrir **Expediente documental**.
2. Incorporar PDF, PNG o JPEG local. Hasta 2 MiB por archivo y 8 MiB de originales por expediente. Se verifica extensión y cabecera de formato, no autenticidad ni ausencia de contenido malicioso. Nombre sin rutas; original y huella conservados en SQLite.
3. Consultar el original y el texto extraído. PDF de hasta 50 páginas con texto seleccionable puede extraerse mediante pypdf, si está disponible. Imágenes y escaneos requieren transcripción manual; no hay OCR. La extracción no se transforma automáticamente en hechos ni se usa para ejecutar instrucciones.
4. Registrar datos con fecha, valor, unidad, clasificación, original/página e incertidumbre. Confirmar revisión. Documentación declarada exige original. La revisión no acredita autenticidad. No se completan pagos o probabilidades.
5. Registrar acciones y respuestas con actor, fecha, estado, referencia y documento opcional. Corregir un dato o evento crea otro registro y conserva el anterior; rechaza una segunda corrección sobre la versión ya sustituida.
6. Comparar lecturas acumuladas revisadas en kWh: diferencia, días y promedio diario calculados con Decimal. Rechaza fechas iguales/invertidas, lecturas descendentes, valores no finitos, supuestos y registros corregidos. Confirmar mismo medidor permite conservar cálculo e inputs congelados. Los controles no verifican físicamente identidad del equipo, registro ni fechas; las horas exactas no intervienen.
7. Conservar un informe documental: fotografía de todos los registros y originales actuales, independientes de nuevas incorporaciones. Previsualizar HTML A4, imprimir/guardar PDF en el navegador, descargar JSON o ZIP con originales e informe. El historial completo, incluidas correcciones, permanece en JSON. No se hace inferencia nueva.
8. Los informes ejecutivos nuevos, desde matriz revisada, incorporan datos/eventos vigentes, cálculos y metadatos documentales congelados. El PDF/HTML ejecutivo no adjunta los binarios; el ZIP documental los conserva. Los informes anteriores no se reescriben.
9. Respaldo y recuperación SQLite incluyen originales y registros. La recuperación existente admite dossier_records. Sigue vigente el límite de 20 MiB por base para respaldos/recuperación: varias cuentas o muchos informes con copias de originales pueden alcanzarlo. No se promete almacenamiento documental ilimitado ni cifrado.

## API y reproducción

POST /api/dossier recibe document, fact, event, calculation o snapshot. Escrituras mantienen comprobación Host/Origin local. GET /api/dossier consulta por workflow_id; /record, /export, /file, /html y /zip por id. /consumption requiere workflow_id, first y last. Datos de otro expediente no se admiten como fuente. El archivo original se obtiene por id generado, nunca por ruta aportada. Huellas detectan cambios, no son firma ni autenticación.

La reproducción documental verifica originales y recalcula comparaciones conservadas desde sus inputs. Los informes congelados no dependen de una lectura del historial actual. El ZIP incluye JSON suficiente para auditar las copias; su importación como expediente nuevo no está implementada. Usar respaldo SQLite para recuperar el sistema.

## Verificación y límites

Cinco pruebas de integración nuevas cubren original, revisión, correcciones, consumo, cálculo alterado incluso con huella rehecha, congelación, ZIP, respaldo/recuperación, vinculación al informe ejecutivo, aislamiento entre expedientes y recorrido HTTP con rechazo de origen no autorizado. Suite general: 182 pruebas Python aprobadas; 80 contratos TypeScript existentes aprobados; compilación React aprobada. Pruebas con datos sintéticos, sin inferencia Ollama ni documentos personales.

La interfaz se revisa en el navegador integrado con una base sintética separada. La vista HTML A4 no certifica paginación nativa ni impresión física; esas verificaciones siguen perteneciendo al cierre integral de fase 10. No hay comprobación de OCR, firma digital, exportación Word nativa ni carga automática del caso real. Los borradores documentales avisan antes de navegar/recargar pero no tienen recuperación automática persistente.

## Incorporación del caso EDESUR

Conservar facturas y foto como originales privados; registrar cada lectura con su fecha y medidor, distinguiendo fecha confirmada de fecha de referencia. Registrar reclamo formal, constancia, respuesta y rectificaciones sin inventar observaciones. El cálculo de consumo no decide legalidad ni anticipa éxito judicial. Una respuesta observada debe incorporarse al protocolo predictivo existente mediante revisión explícita; no hay transferencia automática ni resultados binarios deducidos de texto libre.

Se completa el alcance funcional documental y de seguimiento descrito. Validación empírica de fase 8 abierta: este módulo conserva evidencia, no demuestra mejores predicciones. Ampliaciones posteriores: OCR local revisable, límites de volumen/paginación, vínculo explícito a variables/protocolos y exportación Word desde la aplicación.
