# Comparación de versiones en React

Avance de fase 2 · 6 de octubre de 2026.

En **Editar expediente → Versiones → Comparación**, elegir una base y una versión de contraste y confirmar la comparabilidad de las escalas. Python calcula las diferencias; React muestra las utilidades antes/después, su diferencia y la descomposición entre cambios de pagos y de probabilidades. También muestra pagos modificados, p/q, equilibrios puros y los supuestos conservados de ambas versiones.

La descomposición cambia primero pagos con probabilidades iniciales, y después probabilidades con pagos nuevos. Su atribución depende de ese orden y no representa efectos causales ni predicciones calibradas. La comparación consulta versiones existentes; no guarda una nueva versión ni modifica los modelos.

Elegir una referencia distinta borra el resultado anterior y exige confirmar de nuevo las escalas. La misma versión en ambas referencias no se puede enviar. Actores o estrategias con nombres/posiciones distintos provocan un rechazo explicado por la API. Los estados de consulta y comparación se presentan por separado para evitar acumular paneles.

## Verificación

- Compilación React/TypeScript correcta y 10 pruebas TypeScript aprobadas, incluyendo conservación del resultado Python y rechazo de índices/dimensiones incompatibles.
- 3 pruebas del motor de comparación y 13 pruebas de API aprobadas. La API de comparación devuelve el mensaje concreto del error de validación.
- Navegador: versión 1 frente a 2; pagos sin cambios, q de 0,5 a 0, utilidades del Municipio de 1,5 a 0 y de 3 a 1. La diferencia se atribuye al cambio de probabilidades; los equilibrios puros permanecen iguales.
- Versiones 1 y 3 rechazadas por nombres diferentes de estrategias.
- No se migró el esquema ni se modificaron los datos principales.

## Estado

**Fase 2 en curso: experiencia visual y navegación de expedientes.** Consulta, edición, revisión, historial y comparación están en React. Faltan la integración de árboles, agentes, exploraciones e IA y las verificaciones completas de accesibilidad e impresión. Los gráficos avanzados y el informe ejecutivo unificado todavía no se consideran implementados en React.
