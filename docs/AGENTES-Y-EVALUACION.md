# Agentes y evaluación prospectiva

El laboratorio IA local incorpora un analista y un crítico, ejecutados secuencialmente con Ollama. Dos roles del mismo modelo no son revisores independientes. Python calcula sobre la matriz conservada. Las revisiones registran entrada, modelo, opciones y revisión de origen; no aplican cambios automáticamente. Un contrato inválido falla; las contradicciones semánticas pueden pasar inadvertidas y requieren revisión humana.

El registro prospectivo conserva, antes del plazo del evento, probabilidades de candidato y política de referencia. No permite sobrescribir pronósticos ni observaciones. Las observaciones requieren procedencia y se registran después del plazo. La procedencia es declarada por el usuario, no autenticada por el sistema.

Python compara Brier binario mediante bootstrap pareado con semilla conservada. Cada evaluación guarda el conjunto exacto y SHA-256. `prediction_eval.replay(path, id)` verifica la huella y reproduce el resultado. La inferencia del LLM no se garantiza idéntica entre equipos.

Una diferencia favorable con intervalo negativo y al menos treinta eventos recibe la etiqueta **mejora provisional**. Ese mínimo operativo no sustituye un diseño estadístico, independencia de eventos, control de selección o validación externa. No se promueven políticas automáticamente. Las pruebas sintéticas demuestran funcionamiento, no mejora predictiva real.

## Caso inicial: decisiones frente a EDESUR

Objetivo declarado: solucionar deficiencias del suministro, atención y facturación y evaluar si iniciar una demanda. Las afirmaciones sobre abuso y parcialidad regulatoria se registrarán como relato del usuario hasta contar con documentos. No se asignan probabilidades de éxito sin base empírica.

Separar episodios de cortes, cargos cuestionados y daños. Registrar fechas, duración, facturas, importes, reclamos, respuestas y resoluciones; distinguir hechos documentados, alegaciones y supuestos. Evitar datos personales innecesarios. Determinar jurisdicción y someter viabilidad procesal, plazos y estrategia judicial a revisión profesional.

Alternativas a comparar: reclamo documentado ante la distribuidora; presentación o revisión ante el regulador según trámite aplicable; negociación o vía de consumo que corresponda; consulta profesional y eventual acción judicial. No reducir artificialmente todas estas vías a una matriz 2×2: el analista actual es una primera aproximación; el árbol decisorio deberá representar alternativas y secuencias completas.

Resultados observables posibles: respuesta dentro de un plazo previamente definido, restitución del suministro, corrección de un cargo o pago de un resarcimiento. Definir cada evento sin ambigüedad, antes de observarlo. Un caso individual no demuestra superioridad predictiva general.

Fuentes oficiales consultadas el 7 de octubre de 2026:

- https://www.argentina.gob.ar/enre (el portal se presenta como ENReGE, Electricidad, ex ENRE).
- https://www.argentina.gob.ar/enre/gestion-de-reclamos/formularios-online
- https://www.argentina.gob.ar/servicio/reclamar-por-falta-de-suministro-electrico
- https://www.argentina.gob.ar/enre/tramites-y-servicios

## Pendiente

Definición y evidencia completa del caso real, autenticación externa de documentos y validación empírica independiente. Decisiones IA, comparación, candidatos versionados, calibración revisable y particiones temporales ya están integrados en React/Python. El [protocolo temporal](EVALUACION-TEMPORAL.md) separa desarrollo, validación y prueba; no promueve candidatos. Sigue pendiente recuperar automáticamente borradores tras un cierre inesperado.

## Verificación de este bloque

Compilación React y 43 pruebas existentes de interfaz correctas. Suite Python de 118 pruebas correcta; posteriormente se agregó y verificó un noveno caso específico del nuevo módulo para atribución de acciones a actores. Prueba de interfaz aislada: registro prospectivo conservado y evaluación sin observaciones rechazada.

Prueba real con Mistral: la secuencia completa terminó en 142 segundos con semilla 42 y devolvió `requires_revision`. Antes hubo intentos incompatibles rechazados; no se garantiza disponibilidad ni validez de cada generación. El crítico pidió fechas y categoría tarifaria. El analista mezcló acciones de distintos actores y el crítico no lo detectó. Se incorporó un control Python para prefijos explícitos de actor y se conservó una validación posterior vinculada al registro original, sin afirmar que se repitió la inferencia. Ese control no detecta todas las incoherencias semánticas.

El expediente real y sus revisiones permanecen en SQLite local; los datos económicos aportados no se publican en el repositorio. Ninguna estrategia se aplicó y ninguna mejora predictiva real se demostró.

Las cifras anteriores corresponden a bloques históricos. La [auditoría final 7–8](CIERRE-FASES-7-8.md) registra 147 pruebas Python, 52 frontend y recorrido real sintético completo. Fase 7 implementada; infraestructura de fase 8 terminada, validación empírica abierta. El informe ejecutivo unificado de fase 6 no está cerrado.
