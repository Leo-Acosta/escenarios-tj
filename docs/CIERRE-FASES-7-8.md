# Auditoría de cierre · fases 7–8

Estado al 7 de octubre de 2026: implementación funcional terminada para el alcance actual (juegos 2×2 y resultados binarios). La validación empírica de mejora predictiva continúa abierta.

Se auditó el motor de agentes, los trabajos locales, las versiones de expedientes y el evaluador prospectivo existente. Se reutilizaron cálculos, Brier y contratos; el registro nuevo enlaza esas funciones mediante protocolos temporales. La evaluación anterior queda aislada para impedir abrir una prueba reservada por otro endpoint.

| Requisito verificable | Resultado |
|---|---|
| Protocolo predefinido | Objetivo binario, horizonte, fuentes, independencia, referencia declarada o fija, ventanas y semilla conservados |
| Candidatos y procedencia | Versiones inmutables con matriz congelada, supuestos y comparación de agentes opcional; modelo/digest Ollama, configuración, decisiones y semillas conservados |
| Comparación múltiple | Plan de políticas, rivales, semillas y perturbaciones; victorias, empates, pérdidas y fallos retenidos, incluidos trabajos hijos |
| Temporalidad | Emisión prospectiva, corte de información, disponibilidad de fuentes, unidades separadas entre particiones y embargo de resultados finales |
| Ajuste y selección | Asesor consulta desarrollo; ajuste Python crea otra versión tras revisión; selección manual posterior a validación y anterior a pronósticos finales |
| Reproducción | Conjunto y referencias congelados; verificación de huellas, decisiones, calibración y cálculos sin inferencia |
| React en español | Consulta, gráficos explorables, evidencia, fallos, exportación JSON y resumen individual imprimible |
| Integración | Recorrido HTTP completo y recorrido real desde React con Ollama en base sintética aislada |
| Privacidad | Bases locales, informes privados y archivos de QA excluidos de la entrega Git |

## Comprobaciones

- 147 pruebas Python aprobadas: integración HTTP, persistencia, rechazo de acciones, aislamiento temporal, fallos de transporte, reproducción, referencia fija, selección y ausencia de promoción automática.
- 52 pruebas frontend aprobadas; TypeScript y compilación de producción correctos.
- Prueba real local con Mistral: cuatro condiciones simuladas, dos victorias y dos empates. Pérdidas y fallos ejercitados además en pruebas automatizadas. Utilidad simulada no equivale a precisión predictiva real.
- Recorrido React: cinco observaciones sintéticas de desarrollo, asesor local real, calibración revisada (prior 7), validación, selección, dos pronósticos finales, rechazo de observación prematura, evaluación, exportación, resumen y reproducción sin IA.
- Prueba final sintética: Brier candidato **0,325625** frente a referencia **0,25**; diferencia **+0,075625**, desfavorable. Se conserva la pérdida. Dos eventos no permiten conclusiones estadísticas ni prueban mejora real.

La captura de pantalla devolvió “Unable to capture screenshot”. Se verificaron estados DOM/accesibles y controles interactivos. La composición gráfica y la paginación impresa no quedaron verificadas visualmente; no se afirma aprobación visual premium completa. El aviso de empaquetado `use client` de React Flow no impidió compilar.

## Límites y cierre

El candidato original usa probabilidades aportadas por el analista con un método declarado. Las decisiones del juego no generan automáticamente probabilidades calibradas. Python aplica el ajuste de desarrollo, pero no certifica el método declarado ni la autenticidad de las fuentes. La IA puede justificar una acción válida con una interpretación incorrecta: en una ronda inicial aludió a rondas anteriores inexistentes. Sigue siendo necesaria la revisión semántica humana.

El reloj local debe ser correcto. SHA-256 identifica contenido y permite reproducción, pero no es firma ni defensa contra reescribir deliberadamente toda la base. El bootstrap presupone unidades independientes; treinta eventos es un mínimo operativo, no un cálculo de potencia. Resultados negativos, muestra e intervalo permanecen visibles.

**Fase 7: implementación cerrada para este alcance. Fase 8: infraestructura y recorrido terminados; validación empírica abierta.** Para cerrarla se requieren observaciones reales verificables, protocolo independiente, muestra justificada y evaluación fuera del desarrollo. No hay evidencia de mejora predictiva real ni datos para asignar probabilidades judiciales al caso EDESUR.

Informe unificado de fase 6, recuperación automática de borradores y distribución Windows permanecen fuera de este cierre. Ver [guía temporal](EVALUACION-TEMPORAL.md) y [hoja de ruta](HOJA-DE-RUTA.md).
