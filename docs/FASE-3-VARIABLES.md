# Fase 3 · variables y unidades

Inicio: 7 de octubre de 2026, después del cierre funcional de fase 6. Se retoma esta dependencia pendiente antes de ampliar escenarios y distribución. Las fases 7–8 mantienen su estado: infraestructura implementada y evidencia empírica real pendiente.

## Alcance y criterios de aceptación

Diccionarios versionados por expediente y matriz congelada. Cada variable debe identificar nombre, tipo, valor, unidad, fuente, incertidumbre, intervalo opcional, clasificación de evidencia y vínculo explícito. Tipos iniciales: número, categoría y booleano. Evidencia: sintética, supuesto, documentación declarada o pendiente. No se autentican documentos automáticamente.

Vínculos iniciales: contexto, p/q y celdas de pago a/b del modelo 2×2. Los vínculos numéricos deben coincidir con la matriz conservada; no se cambia una matriz existente al describir sus variables. Intervalos exploratorios no se presentan como distribuciones ni confianza estadística. No hay conversión automática de unidades ni agregación de escalas incompatibles.

Cierre requerido: API local, interfaz React española para crear/consultar diccionarios, referencias congeladas en el informe ejecutivo, exportación JSON, pruebas de integración y revisión visual. La incorporación futura de transformaciones exige fórmulas explícitas y revisión antes de generar una matriz nueva.

## Inicio implementado

`escenarios.variables` valida y conserva diccionarios inmutables con SHA-256 y copia de la matriz. Rechaza nombres/vínculos repetidos, valores incompatibles, intervalos inválidos y registros sin revisión. Las pruebas usan únicamente datos sintéticos y comprueban que la matriz no cambia. Esta base aún no está expuesta en la aplicación: API, interfaz e incorporación al informe ejecutivo son los próximos trabajos. La fase 3 queda iniciada, no cerrada.
