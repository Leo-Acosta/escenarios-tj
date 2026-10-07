# Escenarios TJ · hoja de ruta actualizada

Estado al 7 de octubre de 2026. Arquitectura local: núcleo Python, SQLite e interfaz React/TypeScript. IA local opcional con revisión del analista. El sistema explora consecuencias de supuestos; aún no acredita capacidad de predicción empírica.

## Estado y orden de continuación

| Fase | Resultado esperado | Estado real |
|---|---|---|
| 1 · Base premium | API local y frontend React/TypeScript | Implementada |
| 2 · Experiencia integral | Expedientes, laboratorios, navegación y versiones | Funciones integradas; falta comprobar impresión HTML paginada |
| 3 · Variables y unidades | Diccionario de variables con unidad, tipo, fuente, incertidumbre y vínculo explícito con el modelo | Cerrada en alcance definido: API, editor React, historial, JSON, reproducción e informe ejecutivo |
| 4 · Gráficos avanzados | Árboles, redes, vectores y sensibilidad enlazados a versiones, con filtros y exportación | Árboles/redes existentes más vectores, sensibilidad Python, filtros, fuentes y exportaciones implementados; aceptación visual integral pendiente |
| 5 · Continuidad de datos | Autoguardado de borradores, respaldo, restauración y migraciones | Cerrada funcionalmente: borradores de expediente/laboratorios, variantes por pestaña, respaldo SQLite, restauración separada, esquema v1 y reproducción integral probados |
| 6 · Informe ejecutivo unificado | Un documento que reúna matriz y laboratorios desde referencias congeladas | Cerrada en alcance funcional: selección, historial, A4, PDF vectorial, JSON y reproducción; verificación visual de impresión HTML limitada |
| 7 · Agentes y comparación | Decisiones auditadas, políticas explícitas y mejora controlada | Implementación cerrada para juegos 2×2; baterías, registros versionados, asesor y calibración revisable integrados |
| 8 · Evaluación predictiva | Protocolo, particiones temporales y prueba independiente | Infraestructura y recorrido terminados; validación empírica abierta por falta de observaciones reales independientes |
| 9–10 · Distribución y calidad | Instalación Windows, funcionamiento offline, rendimiento y validación integral | Pendiente |

## Próximo bloque funcional

[Fase 3 · variables y unidades](FASE-3-VARIABLES.md) cerrada en su alcance definido. La fase 4 incorpora gráficos avanzados vinculados a variables y versiones; falta su aceptación visual integral, documentada en [Fase 4](FASE-4-GRAFICOS.md). Las fases 7–8 ya cuentan con infraestructura y no se repiten. La fase 6 permanece cerrada en su alcance funcional, conservando sus límites de verificación documentados.

El [cierre de implementación 7–8](CIERRE-FASES-7-8.md), la [guía de evaluación temporal](EVALUACION-TEMPORAL.md) y el [informe unificado de fase 6](FASE-6-INFORME-UNIFICADO.md) vinculan candidatos, métodos, decisiones y resultados observados. Lo siguiente para acreditar mejora es incorporar evidencia real bajo un protocolo independiente. Para EDESUR faltan facturas, consumo y respuestas documentadas; no se inventarán pagos ni probabilidades. Ampliación de gráficos de fase 4 y comprobaciones de plataforma/dispositivos de fases 9–10 siguen pendientes. Continuidad de fase 5 cerrada funcionalmente. No se necesitan mensajes de “continuá” por bloque para ejecutar una fase autorizada completa.

## Qué ya puede usarse

Crear y editar expedientes guiados, calcular y consultar matrices 2×2, comparar versiones, crear árboles secuenciales, explorar Monte Carlo, ejecutar agentes con memoria y repetir combinaciones de políticas, explorar incentivos, editar redes con evidencia y consultar propuestas locales de IA. Descargar PDF individuales de matrices, árboles, agentes, comparaciones e incentivos. Consultar sus PDF mediante el visor del navegador.

## Criterios que siguen abiertos

La impresión HTML necesita revisión visual paginada en un navegador que permita observar su salida. El visor PDF depende del navegador y mantiene descarga alternativa. Los escenarios complejos requieren ampliar las dimensiones actuales y las transformaciones de variables; el diccionario básico está implementado, y la IA no reemplaza la validación del modelo. Los editores de expediente ofrecen recuperación de copias locales al reabrir. Los formularios independientes de los laboratorios aún no tienen autoguardado. No hay fecha ni porcentaje de terminación global medidos.

## Interfaz experimental

Primera implementación blanca y oliva en React/TypeScript, con modo inmersivo y contexto trazable. Ver [alcance y verificación](INTERFAZ-EXPERIMENTAL.md). Este cambio visual no cierra la ampliación funcional de fase 4; revisión visual mediante captura pendiente por limitación del navegador.


## Continuidad de datos · fase 5

Ver [implementación, verificación y límites](FASE-5-CONTINUIDAD.md). Cerrada funcionalmente. Recuperación explícita de expediente y laboratorios, variantes por pestaña y restauración integral verificadas. La guía registra alcance manual/automatizado y límites de verificación móvil, impresión física y fallos de Windows para fases 9–10.
