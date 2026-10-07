# Decisiones locales, comparación y mejora del proceso

El motor Python admite un proveedor de decisiones opcional. El proveedor recibe copias del modelo y de rondas terminadas: no puede modificar pagos ni memoria del motor, ni conocer la decisión simultánea actual del rival. Ollama devuelve únicamente índice 0 o 1 y justificación breve. Una respuesta incompleta o incompatible se rechaza sin ejecutar la acción. Cada intento se registra en SQLite antes de consultar al modelo y se conserva su respuesta o fallo.

La comparación enfrenta un actor con IA a una política existente, usando igual matriz, rival, número de rondas y semillas. El error de ejecución tiene un flujo aleatorio separado y común para candidato y referencia; elegir una política aleatoria no desplaza las perturbaciones. Las historias sí pueden divergir por las acciones elegidas, como corresponde a un juego repetido. Los pagos, frecuencias, totales y diferencias los calcula Python.

## Ejecutar y reproducir

Desde la raíz:

```powershell
python scripts/compare_local_agents.py --demo --out output/comparacion-agente-local.json
python scripts/compare_local_agents.py --replay ID_DEVUELTO
python scripts/compare_local_agents.py --optimize ID_DEVUELTO --out output/propuesta-optimizador-local.json
```

La demostración usa `data/local-agent-demo.sqlite3`, configura Mistral local y no modifica expedientes reales. No descarga modelos. La reproducción verifica huella, decisiones, contexto y cálculos; no vuelve a consultar Ollama. La generación puede tardar varios minutos. La reproducción no garantiza autenticidad ante una reescritura deliberada de toda la base de datos.

Para una configuración propia, usar `--config archivo.json --db ruta.sqlite3`. La base debe tener Ollama habilitado. El JSON requiere:

```json
{
  "model": {
    "title": "Caso hipotético",
    "actors": ["A", "B"],
    "strategies": [["Cooperar", "Competir"], ["Cooperar", "Competir"]],
    "a": [[3, 0], [5, 1]], "b": [[3, 5], [0, 1]], "p": 0.5, "q": 0.5
  },
  "options": {
    "actor": 0, "rounds": 2, "seeds": [42, 43],
    "baseline": "adaptive", "opponent": "mirror", "noise": 0.1
  },
  "assumptions": "Pagos hipotéticos revisados; sin calibración empírica.",
  "reviewed": true
}
```

Límites operativos: 1–20 rondas, 1–5 semillas distintas. La IA actúa para un actor; el rival sigue una política explícita. La memoria completa queda registrada; Ollama recibe las últimas diez rondas y los conteos acumulados. No se descuentan pagos futuros ni se acredita optimalidad.

## Agente de mejora del proceso

El optimizador primero comprueba que la comparación se reproduce. Luego propone recolectar observaciones, revisar el modelo, validar independientemente o realizar otro ensayo. No recibe datos observados en esta versión y no puede afirmar mejora predictiva. En un ensayo adicional, Python reserva semillas nuevas, acota rondas y propone perturbación mínima 0.1. El borrador devuelve `reviewed: false`: no se ejecuta ni promueve automáticamente.

El optimizador conserva recomendación, entrada, modelo, opciones, respuesta y comparación de origen. Es asesor de experimentación; aún no ajusta parámetros con entrenamiento/validación ni utiliza la evaluación prospectiva para promover candidatos.

## Evidencia obtenida

Prueba real de Ollama en un juego sintético de una ronda: candidato 5 puntos frente a referencia fija 3; diferencia de utilidad 2. La corrida se reprodujo sin inferencia nueva. Eso prueba ejecución y comparación, no mejora predictiva real ni beneficios en EDESUR. El optimizador real propuso un ensayo adicional; su propuesta quedó como borrador.

Nueve pruebas específicas comprueban rechazo de decisiones inválidas, auditoría de fallos e interrupciones, información previa, pagos protegidos, perturbaciones comunes, repetición sin red, detección de cambios y ausencia de promoción automática. La suite completa de 128 pruebas pasó con la implementación final.

## Panel React integrado

En `/app/`, abrir **Asistente de IA local** y seleccionar un expediente. El panel **Agente de decisión · IA frente a políticas** permite elegir una versión calculada, actor, referencia, rival, rondas, semillas y error de ejecución. Revisar la matriz y completar supuestos habilita el inicio. La API toma la matriz guardada de esa versión e ignora una matriz enviada por el navegador. Expedientes sin versiones calculadas no habilitan simulaciones.

El trabajo continúa en segundo plano. El historial conserva hasta veinte trabajos del expediente y muestra resultados, fallos y recomendaciones. El gráfico compara utilidad acumulada y el selector de ronda presenta acción pretendida, acción ejecutada, razón y pagos calculados por Python. Se puede verificar la reproducción y descargar el registro JSON con las respuestas originales. Los textos generados se conservan literalmente; el modelo puede devolver explicaciones en otro idioma.

El asesor se solicita sobre una comparación terminada. **Cargar propuesta para revisar** copia su configuración al formulario, con la revisión desmarcada; no inicia una simulación. La navegación protege un formulario modificado, aunque todavía no recupera borradores tras un cierre inesperado.

Verificación del bloque integrado: 133 pruebas Python y 47 de contratos de interfaz correctas, compilación de producción correcta. En una base de QA separada se ejecutó una comparación real desde React, se verificó su reproducción sin inferencia, se consultó una recomendación real y se cargó el borrador con dos rondas, semillas nuevas y ruido 0.1. La revisión quedó desmarcada y el inicio deshabilitado. Se comprobó el diálogo de descarte y la conservación del formulario al continuar editando. La captura de pantalla no estuvo disponible; se verificaron estados accesibles, no composición visual ni impresión paginada.

## Pendiente

El protocolo y la optimización con desarrollo/validación/prueba ya están implementados en **Evaluación y experimentos**. Ver [guía temporal](EVALUACION-TEMPORAL.md) y [auditoría final](CIERRE-FASES-7-8.md). La batería conserva comparaciones múltiples y fallos; el asesor de desarrollo propone calibración acotada con aceptación manual. Las funciones históricas descritas arriba permanecen disponibles. La utilidad simulada no se transforma en Brier ni en evidencia judicial. Pendientes: observaciones reales independientes, validación empírica e informe ejecutivo unificado.
