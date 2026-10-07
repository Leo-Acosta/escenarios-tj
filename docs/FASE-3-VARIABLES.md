# Fase 3 · variables y unidades

Inicio: 7 de octubre de 2026, después del cierre funcional de fase 6. Se retoma esta dependencia pendiente antes de ampliar escenarios y distribución. Las fases 7–8 mantienen su estado: infraestructura implementada y evidencia empírica real pendiente.

## Alcance y criterios de aceptación

Diccionarios versionados por expediente y matriz congelada. Cada variable debe identificar nombre, tipo, valor, unidad, fuente, incertidumbre, intervalo opcional, clasificación de evidencia y vínculo explícito. Tipos iniciales: número, categoría y booleano. Evidencia: sintética, supuesto, documentación declarada o pendiente. No se autentican documentos automáticamente.

Vínculos iniciales: contexto, p/q y celdas de pago a/b del modelo 2×2. Los vínculos numéricos deben coincidir con la matriz conservada; no se cambia una matriz existente al describir sus variables. Intervalos exploratorios no se presentan como distribuciones ni confianza estadística. No hay conversión automática de unidades ni agregación de escalas incompatibles.

Cierre requerido: API local, interfaz React española para crear/consultar diccionarios, referencias congeladas en el informe ejecutivo, exportación JSON, pruebas de integración y revisión visual. La incorporación futura de transformaciones exige fórmulas explícitas y revisión antes de generar una matriz nueva.

## Implementación y recorrido terminado

`escenarios.variables` valida y conserva diccionarios inmutables con SHA-256 y copia de la matriz. Rechaza nombres/vínculos repetidos, valores incompatibles, intervalos inválidos y registros sin revisión. La reproducción comprueba variables, vínculo de expediente/versión y todos los resultados de la matriz congelada. Las pruebas usan únicamente datos sintéticos y comprueban que la matriz no cambia.

En `/app/`, abrir **Variables y unidades**, elegir expediente y versión calculada. Completar nombre, vínculo, tipo, valor, unidad, evidencia, fuente e incertidumbre; indicar ambos extremos del intervalo o ninguno. Un vínculo numérico copia el valor de matriz y lo deja de solo lectura. p/q requieren unidad `proporción` o `1`; `%` se rechaza. Contexto permite números, categorías y booleanos, sin cambiar el modelo.

Revisar y pulsar **Conservar diccionario**. Cambios posteriores requieren conservar otro registro; el anterior permanece inmutable. El historial permite consultar registros de la versión seleccionada, exportar JSON completo y **Verificar variables** sin IA. Consultar un registro no reemplaza un borrador; cambiar versión/expediente o navegar con cambios requiere elegir si conservar la edición o descartarla. Un cierre inesperado no recupera el borrador: eso corresponde a fase 5.

En **Informe ejecutivo**, activar **Variables y unidades** y seleccionar un diccionario del mismo expediente y versión. Se conservan su copia completa y huella. HTML A4/PDF muestran tipo, valor/unidad, vínculo, intervalo, evidencia, fuente e incertidumbre. Los nombres de actores/estrategias describen vínculos de pagos; los códigos internos quedan en JSON para reproducción. El informe sigue reproduciéndose si se elimina el diccionario original.

## API y límites

- `POST /api/variables`: workflow_id, versión, lista de variables y reviewed=true.
- `GET /api/variables?id=…` y `GET /api/variables/export?id=…`: registro completo congelado.
- `GET /api/variables/history?workflow_id=…&version=…`: últimos 50 registros, filtrados antes del límite. Sin version, incluye todas las versiones del expediente.
- `GET /api/variables/replay?id=…`: verificación desde la copia, sin nueva inferencia.

Máximo 100 variables por diccionario y 1.200.000 bytes por solicitud HTTP. Fuente e incertidumbre: hasta 1.000 caracteres cada una. Se admiten unidades declaradas y tipos básicos; no se implementan conversiones dimensionales, fórmulas causales, fechas como tipo independiente ni juegos de mayor dimensión. Un intervalo exploratorio no implica distribución probabilística. Documentación declarada requiere comprobación externa; SHA-256 no es una firma.

## Verificación y cierre

Estado: **fase 3 cerrada en el alcance definido**, 7 de octubre de 2026.

- 165 pruebas Python y 59 frontend aprobadas; compilación TypeScript/Vite correcta. Incluye controles HTTP de origen, valores incompatibles, cien variables con textos Unicode extensos, versiones distintas, detección de cambios aun con huellas recalculadas y reproducción de informe sin fuente original.
- Recorrido React con dos variables sintéticas: proporción vinculada y booleano pendiente; protección de descarte, conservación, historial, reproducción, descarga JSON y selección en informe ejecutivo. Informe creado y reproducido desde React sin consultar Ollama.
- Revisión visual del editor en escritorio: campos, selección, tarjetas y jerarquía legibles. Una captura inicial falló y tardó varios minutos; posteriormente se obtuvo captura acotada. La emulación de 390 px reportó un ancho real de 749 px: no se declara comprobado el diseño móvil por debajo de 650 px.
- PDF sintético A4 de ocho páginas revisado página por página, sin recortes detectados. Prueba adicional de una fuente con 190 líneas verifica que las filas se dividan entre páginas sin perder texto. La salida del ejemplo conserva sus bytes después de ese ajuste.
- No se imprimió físicamente ni se validó la paginación HTML en todos los navegadores. No se modificó el caso EDESUR ni se incorporaron sus datos a Git.

La mejora predictiva empírica de fase 8 sigue abierta. Las ampliaciones de gráficos y la recuperación de borradores corresponden a fases 4 y 5; no son pendientes de este cierre.
