# Fase 5 · continuidad y recuperación

Cierre funcional: 7 de octubre de 2026. Implementación, pruebas de integración y recorrido de recuperación terminados. La validación empírica de fase 8 permanece abierta; este cierre no acredita mejores predicciones.

## Borradores y concurrencia

El editor React conserva campos incompletos, pagos, fuentes parciales, título, descripción, supuestos y respuestas sin enviar. Los laboratorios conservan parámetros de agentes/comparación/barridos, variables, composición ejecutiva, árboles, redes, protocolos/candidatos, baterías, decisiones IA y pronósticos/observaciones. La Mesa estratégica protege el expediente y los cuatro formularios analíticos originales. La entrada auxiliar de nodos de su red ilustrativa no constituye un editor versionado: para redes propias se usa React.

Cada documento/pestaña escribe una variante separada. Las copias se identifican por interfaz, expediente y versión/fuente/protocolo según el módulo. El registro predictivo histórico es global y se identifica así. Dos pestañas pueden conservar sus últimas variantes sin sobrescribirse: el panel permite elegir la copia. Las claves antiguas siguen siendo compatibles. Guardar o eliminar una copia no elimina las variantes de otras pestañas; si el contenido seleccionado cambió, se rechaza su eliminación o recuperación. No se promete una transacción distribuida ni una fusión automática entre pestañas. Las copias incompatibles se conservan y las válidas del editor siguen disponibles.

Recuperar requiere una acción explícita, devuelve los campos al formulario y desmarca la revisión. No modifica SQLite, calcula ni inicia inferencias. Cambiar de expediente o versión exige el control de descarte existente. El editor advierte si cambió la revisión del servidor; guardar continúa usando control de conflictos. Los contratos de recuperación tienen estructura estable y excluyen revisiones y autorizaciones de inferencia. Al crear un protocolo/candidato, los campos pendientes del contexto anterior no se aplican silenciosamente al nuevo.

Las copias dependen del navegador, origen/puerto y almacenamiento disponible. No son versiones analíticas ni respaldo permanente. Se muestran errores de cuota y lectura. Las variantes abandonadas se retiran explícitamente: no hay caducidad que elimine trabajo sin consentimiento. Guardar en SQLite limpia la copia propia/consumida de React; los parámetros de la Mesa se limpian manualmente. Descartar campos visibles puede conservar su copia recuperable.

Si un módulo no puede cargarse tras actualizar la interfaz, un aviso visible permite reabrir la aplicación y recuperar sus copias. No se afirma que una copia exista si su almacenamiento falló.

## Respaldo, restauración y esquema

En **Respaldo y recuperación**, descargar una instantánea SQLite consistente incluye cambios confirmados en WAL y todas las tablas existentes de expedientes, versiones, redes, agentes, investigación, IA e informes. No incluye archivos externos citados ni formularios del navegador.

**Verificar y recuperar** requiere revisión y admite hasta 20 MiB. Verifica integridad SQLite, esquema, tablas/columnas, objetos permitidos y JSON, rechazando NaN/Infinity. Estos controles no verifican autenticidad documental ni toda la coherencia semántica. Recupera una base nueva en data/recovered/recuperada-UUID.sqlite3 con SHA-256; nunca sobrescribe ni activa automáticamente la base original. La pantalla entrega el comando para activarla después de detener el servidor:

~~~powershell
python -m escenarios.server --port 8766 --database "data/recovered/recuperada-UUID.sqlite3"
~~~

Esquema v1 mediante PRAGMA user_version. La transición 0→1 valida tablas, crea una copia consistente y manifiesto en data/migration-backups/ y registra la versión sin reescribir resultados. Es idempotente. Versiones futuras y esquemas desconocidos se rechazan. Las tablas opcionales siguen creándose cuando corresponde.

~~~powershell
python -m escenarios.continuity inspect --source "data/escenarios.sqlite3"
python -m escenarios.continuity backup --source "data/escenarios.sqlite3" --destination "mi-respaldo.sqlite3"
python -m escenarios.continuity recover --source "mi-respaldo.sqlite3" --destination "data/recovered"
~~~

El destino de respaldo debe ser nuevo. API: GET /api/continuity/status, GET /api/continuity/backup, POST /api/continuity/recover, con controles de Host/Origin y confirmación. Conservar la base original permite volver a ella. Respaldos y datos privados se excluyen de Git.

## Evidencia de aceptación

| Requisito | Evidencia |
| --- | --- |
| Copia consistente y recuperación separada | Pruebas WAL, original intacto, esquema futuro/corrupción rechazados y HTTP con origen/revisión |
| Registros congelados completos | Prueba integrada con matriz, árboles, agentes, comparación, barrido, decisiones, batería, investigación, variables, red e informe: tablas idénticas tras restaurar |
| Reproducción sin inferencia | Inferencia sustituida por una función que falla si se llama; reproducción e informe/PDF idénticos tras restaurar |
| Formularios incompletos y versiones aisladas | Contratos de los ocho grupos de laboratorios, editor y variantes; formatos inválidos, revisiones anidadas y cuota rechazados |
| Variantes concurrentes | Escrituras intercaladas y eliminación conservadora automatizadas; navegador: variantes de 7 y 9 rondas recuperables, guardar 9 conserva la de 7 |
| Recuperación explícita y guardado revisado | Navegador aislado: agentes, variables, árbol, red e informe recuperados y guardados; revisión inicialmente desmarcada |
| Planes sin ejecución automática | Navegador: protocolo y batería parciales, decisión IA y pronóstico recuperados; botones de IA permanecen deshabilitados |
| Informe trazable después de recuperar | Recorrido navegador: emisión sintética, vista A4 y reproducción confirmada desde copias congeladas |
| Fallo de carga visible | Actualización de assets con pestaña abierta: aviso de continuidad, reapertura y acceso a registros |

Resultado: **172/172 pruebas Python y 80/80 pruebas frontend aprobadas**. TypeScript y build Vite aprobados. Vite conserva un aviso no bloqueante de la dependencia React Flow sobre su directiva use client. La prueba completa de restauración utiliza datos sintéticos; no se utilizó EDESUR ni información privada como fixture.

No todos los formularios se recorrieron manualmente: su cobertura completa de estructura/contexto es automatizada; los guardados del núcleo están cubiertos por integración. Se inspeccionó visualmente la interfaz blanco/azul marino y los controles de recuperación. El proveedor del navegador devolvió un viewport distinto al solicitado en el ensayo móvil y capturas con área vacía: no se acredita revisión visual en un dispositivo móvil real. CSS oculta paneles de recuperación al imprimir y las pruebas verifican PDF A4; no se realizó impresión física. Tampoco se provocó un cierre abrupto de Windows ni se acreditó reanudación de inferencias reales en curso. Estas comprobaciones de plataforma corresponden al empaquetado/calidad de fases 9–10, no alteran la restauración de registros ya confirmados.

## Lo siguiente

Fase 5 cerrada funcionalmente. Fase 6 no se repite. Continúan distribución Windows y calidad de fases 9–10: instalable, arranque/parada, actualización con rollback, pruebas de dispositivos/impresión y fallos de proceso. Fase 8 necesita observaciones reales independientes para acreditar mejora predictiva; permanece abierta en su validación empírica.
