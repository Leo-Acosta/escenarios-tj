# Escenarios TJ · hoja de ruta actualizada

Estado al 13 de octubre de 2026. Arquitectura local: núcleo Python, SQLite e interfaz React/TypeScript. IA local opcional con revisión del analista. El sistema explora consecuencias de supuestos; aún no acredita capacidad de predicción empírica.

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
| 8 · Evaluación predictiva | Protocolo, particiones temporales y prueba independiente | Cerrada funcionalmente por solicitud del usuario; validación empírica conservada como pendiente transversal P-EMP-01, sin mejora real acreditada |
| 9 · Distribución Windows | Ejecutable portable e instalación | Cerrada funcionalmente: portable e instalador por usuario; instalación, reinstalación, desinstalación y datos conservados aprobados localmente y en dos runners Windows nuevos |
| 10 · Calidad de plataforma | Rendimiento, dispositivos, impresión y actualización | Implementación y aceptación automatizada terminadas: presupuestos, concurrencia, A4 y matriz Windows/Linux × Python 3.11/3.13 aprobados; cierre integral abierto por impresión HTML nativa y aceptación entre navegadores pendientes |
| 11 · Expediente documental y seguimiento real | Originales locales, datos revisados, acciones/respuestas e informes congelados | Implementada en alcance acotado: PDF/PNG/JPEG, extracción de texto no OCR, correcciones, comparación de lecturas, exportación y recuperación. Ver FASE-11-EXPEDIENTE-DOCUMENTAL.md |

## Próximo bloque funcional

[Fase 3 · variables y unidades](FASE-3-VARIABLES.md) cerrada en su alcance definido. La fase 4 incorpora gráficos avanzados vinculados a variables y versiones; falta su aceptación visual integral, documentada en [Fase 4](FASE-4-GRAFICOS.md). Las fases 7–8 ya cuentan con infraestructura y no se repiten. La fase 6 permanece cerrada en su alcance funcional, conservando sus límites de verificación documentados.

El [cierre de implementación 7–8](CIERRE-FASES-7-8.md), la [guía de evaluación temporal](EVALUACION-TEMPORAL.md) y el [informe unificado de fase 6](FASE-6-INFORME-UNIFICADO.md) vinculan candidatos, métodos, decisiones y resultados observados. Lo siguiente para acreditar mejora es incorporar evidencia real bajo un protocolo independiente. Para EDESUR ya se aportaron facturas, estimación de equipos y foto del medidor en el trabajo local; falta revisar su incorporación al expediente y registrar reclamos/respuestas verificables. La [fase 11](FASE-11-EXPEDIENTE-DOCUMENTAL.md) permite hacerlo sin inventar pagos ni probabilidades. Comprobaciones de plataforma y aceptación visual siguen abiertas; continuidad de fase 5 cerrada funcionalmente.

## Qué ya puede usarse

Crear y editar expedientes guiados, calcular y consultar matrices 2×2, comparar versiones, crear árboles secuenciales, explorar Monte Carlo, ejecutar agentes con memoria y repetir combinaciones de políticas, explorar incentivos, editar redes con evidencia y consultar propuestas locales de IA. Descargar PDF individuales de matrices, árboles, agentes, comparaciones e incentivos. Consultar sus PDF mediante el visor del navegador.

## Criterios que siguen abiertos

**P-EMP-01 · validación empírica:** pendiente independiente del cierre funcional de
fase 8. Exige observaciones reales verificables, muestra justificada, referencia
congelada y prueba temporal independiente. No se oculta ni se cuenta como cumplido.
El siguiente trabajo concreto es revisar el expediente EDESUR en fase 11.

La impresión HTML necesita revisión visual paginada en un navegador que permita observar su salida. El visor PDF depende del navegador y mantiene descarga alternativa. Los escenarios complejos requieren ampliar las dimensiones actuales y las transformaciones de variables; el diccionario básico está implementado, y la IA no reemplaza la validación del modelo. Los editores de expediente ofrecen recuperación de copias locales al reabrir. Los formularios de laboratorios ofrecen recuperación explícita de borradores, documentada en fase 5. No hay fecha ni porcentaje de terminación global medidos.

## Interfaz experimental

Interfaz blanca y azul marino en React/TypeScript, con modo inmersivo y contexto trazable. Ver [alcance y verificación](INTERFAZ-EXPERIMENTAL.md). Este cambio visual no cierra la ampliación funcional de fase 4; revisión visual mediante captura pendiente por limitación del navegador.


## Continuidad de datos · fase 5

Ver [implementación, verificación y límites](FASE-5-CONTINUIDAD.md). Cerrada funcionalmente. Recuperación explícita de expediente y laboratorios, variantes por pestaña y restauración integral verificadas. La guía registra alcance manual/automatizado y límites de verificación móvil, impresión física y fallos de Windows para fases 9–10.

## Distribución Windows · fase 9

Ver [paquete portable, uso, actualización y verificación](FASE-9-WINDOWS.md). Ejecutable x64 y ZIP locales con recursos incluidos, datos separados y bloqueo de segunda instancia. Se probó sin Python en PATH, con PDF idéntico después de reiniciar. Instalador asistido y recorrido independiente en dos runners Windows aprobados. Fase 9 cerrada funcionalmente; calidad de dispositivos y plataformas de escritorio continúa en fase 10.

## Calidad de plataforma · fase 10

Ver [resultados, protocolo y límites](FASE-10-CALIDAD.md). 176 pruebas Python, 80 contratos TypeScript y compilación aprobados. Mediciones sintéticas repetidas en cuatro combinaciones de sistema/Python; PDF concurrente idéntico, reproducción sin inferencia y A4 comprobados. Vista reducida de 480 px sin desbordamiento observada. La impresión nativa quedó bloqueada por la verificación de URL de Computer Use, incluso después de abrir el usuario una ventana autorizada. No se declara cerrada la aceptación integral ni se exige repetir los bloques implementados: resta verificación visual nativa y entre navegadores. La fase 8 está cerrada funcionalmente; P-EMP-01 sigue pendiente por falta de observaciones independientes.

## Ampliación científica R · etapas 1–2 solicitadas

Etapas 1–2 cerradas funcionalmente el 10 de octubre de 2026 en Windows: R instalado, gráficos y cuatro modelos ejecutados, red profunda y modelos guardados reproducidos, resultados integrados en React e informes congelados. El 13 de octubre se verificaron giro 3D en Chromium/Firefox, vista móvil y PDF A4, y se construyó un instalador científico con R y Keras CPU. Ver [aceptación y límites](CIERRE-CIENTIFICO-WINDOWS.md). La fase 8 está cerrada funcionalmente; P-EMP-01 permanece pendiente por falta de evaluación empírica independiente; otros navegadores nativos, dispositivos, impresión física y un Windows limpio para el nuevo paquete mantienen límites de plataforma.
