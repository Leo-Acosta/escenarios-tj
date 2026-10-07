# Fase 5 · continuidad y recuperación

Implementación del 7 de octubre de 2026. El núcleo de respaldo/restauración y la recuperación de borradores de expediente están operativos. La fase completa sigue abierta hasta ampliar la recuperación a los formularios independientes de todos los laboratorios.

## Qué protege

El editor React conserva una copia local de cada borrador de expediente, incluidos campos numéricos incompletos, fuentes parciales, supuestos, título/descripción de un expediente nuevo y respuesta guiada todavía no enviada. La Mesa estratégica original conserva modelo, fuentes, supuestos y campos pendientes de fuente/respuesta. Las copias se separan por expediente, interfaz y formato. Al reabrir se ofrecen, no se aplican automáticamente.

Recuperar vuelve a poner los datos en el formulario, elimina la confirmación de revisión y no modifica SQLite ni calcula. La interfaz advierte si la revisión del servidor cambió. Guardar sigue utilizando la revisión actual y los controles de conflicto existentes. Un cambio en otra pestaña ofrece la copia compartida antes de sobrescribirla; no se garantiza coordinación transaccional entre pestañas que escriban simultáneamente. Las copias del navegador no son versiones analíticas ni respaldo permanente: dependen del mismo origen/puerto, navegador y almacenamiento disponible. Se muestran errores de lectura, corrupción o cuota; no se afirma guardado cuando falla.

Las copias se limpian tras guardar correctamente en SQLite o mediante descarte explícito. Salir de un formulario descarta sus campos visibles, pero puede conservar su copia de recuperación. La revisión no se restaura como aceptada. Los formularios independientes de árboles, redes, variables, investigación, informe y parámetros de simulación mantienen su protección de descarte anterior; su autoguardado aún no está integrado.

## Respaldo y restauración

Abrir **Respaldo y recuperación** desde `/app/` o el acceso de la Mesa estratégica. **Descargar respaldo** produce una instantánea SQLite usando la API de respaldo, incluyendo cambios confirmados en WAL. Incluye tablas de expedientes, versiones, redes, agentes, investigación, IA local e informes que existan en la base. No incluye formularios pendientes del navegador ni los archivos externos citados como fuentes.

**Verificar y recuperar** acepta una copia de hasta 20 MiB y requiere revisión explícita. Comprueba integridad SQLite, versión de esquema, tablas/columnas permitidas, ausencia de objetos no admitidos y JSON de registros. Estas comprobaciones no validan veracidad de evidencias ni toda la coherencia semántica. Una copia compatible se recupera en `data/recovered/recuperada-UUID.sqlite3`, con SHA256 calculado. Nunca se sobrescribe ni se cambia la base activa desde la interfaz. Para usar la copia, detener el servidor y reiniciarlo con el comando que muestra la pantalla; conservar la base original permite volver a ella.

```powershell
python -m escenarios.server --port 8766 --database "data/recovered/recuperada-UUID.sqlite3"
```

La opción `--database` también permite una base nueva. No ejecutar simultáneamente varios servidores sobre la misma base para operaciones de recuperación. Los respaldos pueden contener datos privados y no se incorporan a Git.

## Esquema y herramientas

Se registra la versión 1 mediante `PRAGMA user_version`. La transición 0→1 valida las tablas existentes, crea primero una copia consistente y su manifiesto SHA256 en `data/migration-backups/`, y registra la versión sin reescribir los registros analíticos. Es idempotente. Versiones futuras o esquemas desconocidos se rechazan: no se intenta degradarlos. Los módulos siguen creando sus tablas opcionales cuando corresponde. Esta migración inicial no amplía la estructura de los modelos.

```powershell
python -m escenarios.continuity inspect --source "data/escenarios.sqlite3"
python -m escenarios.continuity backup --source "data/escenarios.sqlite3" --destination "mi-respaldo.sqlite3"
python -m escenarios.continuity recover --source "mi-respaldo.sqlite3" --destination "data/recovered"
```

La herramienta de respaldo exige un destino nuevo; recuperación genera otro nombre exclusivo. API: `GET /api/continuity/status`, `GET /api/continuity/backup`, `POST /api/continuity/recover`. La recuperación conserva los controles de Host y Origin locales y rechaza entradas sin confirmación, corruptas o demasiado grandes.

## Verificación

171 pruebas Python aprobadas. Las pruebas automatizadas cubren respaldo con WAL activo, migración idempotente con copia previa, rechazo de esquemas futuros/corrupción/objetos inesperados, recuperación sin alterar original, lectura idéntica de versiones congeladas y controles HTTP de origen y confirmación. Frontend: 64 pruebas, incluidos borradores incompletos, expedientes cruzados, formato futuro, corrupción y fallo de cuota.

En navegador se comprobó crear un borrador sintético React sin crear expediente, salir/reabrir/recuperar sus campos y descartar su copia. En la Mesa estratégica se modificó el título de un expediente sintético, se reabrió en otra pestaña y se recuperó sin guardar SQLite; la confirmación nativa de limpieza encontró una limitación del navegador y no se confirmó el descarte final de esa copia de prueba. La interfaz de recuperación aceptó una base sintética de 36 KiB y creó una base separada, mostrando identificador, SHA256 e instrucciones de activación. La base activa siguió disponible. No se utilizó el caso EDESUR como fixture.

La inspección visual mediante capturas sigue limitada por el navegador; no se acredita revisión móvil ni salida física de impresión. Tampoco se provocó un cierre abrupto del sistema operativo: se verificaron las rutas de almacenamiento y reapertura.

## Cierre pendiente

Extender copias de recuperación a los formularios independientes de los laboratorios, probar revisión concurrente entre pestañas y completar revisión visual. No se afirma cierre integral de fase 5 ni un porcentaje global. Después corresponde preparación de distribución y calidad Windows (9–10); fase 6 ya está implementada y no se repite. La validación empírica de fase 8 permanece pendiente de observaciones independientes.
