# Ollama · conexión verificada

Verificación del 7 de octubre de 2026 en el equipo del proyecto.

- Ollama instalado en C:/Users/LiberaTion/AppData/Local/Programs/Ollama/ollama.exe.
- Servicio local responde en http://127.0.0.1:11434/api/tags.
- Modelo compatible instalado: mistral:latest, digest 6577803aa9a036369e481d648a2baebb381ebc6e897f2bb9a766a2aa7bfbc1cf.
- Configuración de la base principal ya estaba habilitada; se conservó sin reinstalar ni descargar modelos.
- GET /api/ai/status confirmó enabled=true, connected=true y ready=true. La interfaz React mostró IA local lista y Motor conectado.
- Una solicitud REAL mediante local_ai.propose, sin mocks, devolvió propuesta válida con dos actores y dos alternativas por actor en 125,78 segundos. Se usó descripción hipotética en base aislada; no se aplicó a ningún expediente. Evidencia local: output/ollama-verificacion.json.
- Diez pruebas automatizadas de integración local correctas, incluidas indisponibilidad, contrato y revisión de modelo.

La integración existente sirve a las propuestas de expedientes y árboles. La IA no genera pagos ni probabilidades confirmadas, no sustituye el cálculo Python ni gobierna las políticas de agentes de las simulaciones. Cumplir el esquema no certifica la corrección estratégica de una propuesta.

Se incorpora scripts/check_ollama.py para repetir el diagnóstico y, con --generate, probar una propuesta real aislada. La ejecución sin --generate se verificó con código 0. La herramienta reutiliza el adaptador del proyecto y no descarga modelos ni modifica expedientes. El asistente mantiene habilitación/deshabilitación, consulta de procedencia y revisión antes de aplicar.
