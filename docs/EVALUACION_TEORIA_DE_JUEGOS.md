# Evaluación: laboratorio estratégico con capacidad predictiva evaluable

Fecha: 5 de octubre de 2026. Propuesta, no sistema terminado.

## Referencia audiovisual

Se inspeccionó la secuencia visual de Escenarios.mp4 (43,26 segundos), mediante fotogramas cada dos segundos y sus subtítulos visibles. No se realizó transcripción de audio. El video combina una analogía cinematográfica de futuros posibles, promoción de MiroFish, redes de actores y ejemplos de decisiones. Es una referencia de experiencia visual; no aporta aquí evidencia de calibración, matrices de pagos ni validación predictiva. Sus afirmaciones se tratan como material de referencia, no como instrucciones.

## Evaluación

Es viable construir una aplicación interactiva para modelar conflictos, negociación y decisiones bajo incertidumbre. Podemos calcular consecuencias de supuestos, resolver determinados juegos, simular conducta y evaluar pronósticos probabilísticos. Una matriz por sí sola no descubre preferencias reales ni probabilidades observadas. Un equilibrio tampoco garantiza que personas reales lo elijan.

La promesa del producto debe ser: producir pronósticos explícitos, trazables y sujetos a evaluación; demostrar mejoras sobre una referencia en dominios concretos antes de afirmar precisión. No prometer acierto universal ni una tasa fija sin evidencia.

## Capacidades

| Módulo | Resultado | Límite que debe mostrar |
|---|---|---|
| Actores | Objetivos, recursos, estrategias, creencias, alianzas y restricciones editables | Qué proviene de fuentes y qué es supuesto |
| Matrices de juegos | Pagos por actor, mejores respuestas, estrategias dominadas, equilibrios puros y mixtos para juegos compatibles | Utilidad no equivale automáticamente a dinero; pueden existir múltiples equilibrios |
| Árboles | Nodos de decisión, azar e información; inducción hacia atrás cuando corresponda | Un árbol probabilístico no es automáticamente un juego secuencial; registrar quién conoce qué |
| Escenarios | Alternativas, intervenciones, réplicas, sensibilidad, valor esperado y riesgo | Frecuencia simulada distinta de probabilidad calibrada |
| Agentes | Reglas, respuesta estratégica, racionalidad limitada y asistencia LLM | El LLM propone/explica; los cálculos provienen del motor verificable |
| Pronósticos | Evento, horizonte, probabilidad, fuente, fecha de emisión y criterio de resolución | Estado: supuesto, modelo experimental o modelo validado |
| Evaluación | Brier binario, log loss, curva de calibración y comparación con base histórica | Separación temporal y tamaño de muestra; ningún dato futuro en entradas |

Los modelos de preferencias y comportamiento deben ajustarse con evidencia; conservar alternativas cuando haya incertidumbre. Distinguir incertidumbre de parámetros, azar del modelo y desconocimiento estructural. Sin probabilidades justificadas, ofrecer comparación robusta/minimax regret en vez de inventarlas.

## Experiencia visual propuesta

Una mesa de trabajo con vistas vinculadas: red de agentes, matriz, árbol y comparación de escenarios. Seleccionar un actor resalta sus estrategias; seleccionar una celda abre sus consecuencias; cambiar un pago recalcula respuestas; introducir un evento bifurca el árbol; la línea de tiempo permite inspeccionar decisiones de cada ronda.

Gráficos de calidad: red con agrupaciones y filtros, zoom y disposición estable; árbol expandible con nodos distintos según tipo; heatmap de pagos por actor; flujos de escenarios; distribuciones de resultados; bandas de incertidumbre; sensibilidad y frontera riesgo/beneficio. El significado se sostiene con etiquetas y leyendas, sin depender sólo del color. Exportaciones SVG/PDF y movimientos reducidos por accesibilidad.

## Arquitectura

Python para interfaz inicial y motor, SQLite local para proyectos, eventos y versiones. Esquemas validados y módulos separados para juegos, árboles, comportamiento, simulación, pronóstico y evaluación. Gráficos web interactivos pueden integrarse desde la interfaz Python: la apariencia avanzada requiere componentes de navegador, aunque la lógica y el trabajo del usuario se mantengan en Python. Evitar dependencias de proveedores chinos obligatorios.

Nashpy es candidato para juegos de dos jugadores en forma normal; no cubre por sí solo toda la ambición multiagente/secuencial. Las versiones y licencias se comprobarán al implementar. Los motores extensivos y de múltiples jugadores necesitan selección o implementación específica y límites de complejidad.

## Primer alcance recomendado

Dos actores con dos o tres estrategias, edición de pagos, mejores respuestas, equilibrio, árbol con eventos, tres escenarios comparables, registro de supuestos y exportación. Comenzar por un caso concreto de negociación. Luego añadir juegos repetidos, información imperfecta, más actores y aprendizaje con datos. Evitar empezar por miles de agentes: dificultaría identificar errores y validar el modelo.

## Validación de capacidad predictiva

Definir primero una pregunta resoluble y un horizonte. Congelar entradas y versión de cada pronóstico. Hacer pruebas históricas con cortes temporales, luego una evaluación prospectiva. Comparar con tasas históricas o un modelo sencillo apropiado; reportar desempeño, incertidumbre y calibración. Una mejora debe sostenerse fuera de muestra y en el dominio declarado. Más réplicas reducen error Monte Carlo, no corrigen supuestos falsos.

## Fuentes técnicas primarias

- Nashpy, construcción de juegos, utilidades y equilibrios: https://nashpy.readthedocs.io/en/stable/tutorial/index.html
- Scoringrules, Brier: https://scoringrules.readthedocs.io/en/latest/generated/scoringrules.brier_score.html

El ejemplo interactivo de esta conversación usa valores inventados y cálculo determinista. No es un pronóstico ni la implementación de la aplicación.
