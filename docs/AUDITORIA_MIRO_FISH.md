# Auditoría estática de Miro-Fish

Fecha: 5 de octubre de 2026.
Repositorio: https://github.com/parety/Miro-Fish
Rama descargada: main. Commit: `985f89f49acbb44ee14d9d680682c741a44eeebe`.

## Alcance y conclusión

Revisión inicial de arquitectura, configuración, rutas API, persistencia, servicios de simulación, dependencias declaradas y workflow de construcción. No incluye ejecución, explotación, análisis completo de dependencias transitivas, pentest ni validación científica. Los riesgos señalados son hallazgos estáticos; no se afirma que se hayan explotado.

El proyecto sirve como referencia funcional para un laboratorio de escenarios. No conviene trasladarlo directamente a producción ni presentar sus simulaciones como pronósticos validados. La propuesta es una implementación propia en Python, con español como idioma y proveedores configurables.

## Arquitectura observada

El backend ya es Python: Flask, cliente compatible con OpenAI, Zep Cloud y OASIS/CAMEL. La interfaz es Vue 3, Vite, Axios y D3; no es Python.

Flujo: documentos PDF/texto → extracción y ontología generada por LLM → grafo Zep → perfiles de agentes → simulación de plataformas tipo Twitter/Reddit → informe e interacción con agentes. Las simulaciones se lanzan mediante procesos Python; los proyectos y estados se guardan en archivos JSON.

Evidencia: `backend/pyproject.toml`, `frontend/package.json`, `backend/app/services/graph_builder.py`, `simulation_manager.py`, `simulation_runner.py`, `report_agent.py` y `backend/scripts/`.

## Hallazgos priorizados

| Prioridad | Hallazgo y evidencia | Impacto y corrección propuesta |
|---|---|---|
| Alta | `backend/app/config.py` activa DEBUG por defecto; `backend/run.py:40-45` escucha en 0.0.0.0 y usa el servidor de desarrollo. | Riesgo al exponer el servicio y su depurador. Iniciar en loopback, debug desactivado y servidor adecuado al despliegue. |
| Alta | No se observó autenticación ni control de propietario en las rutas revisadas. `backend/app/api/graph.py:36-90` permite consultar/listar/borrar proyectos. | Un cliente con acceso a la API puede operar sobre datos ajenos. Añadir autorización por proyecto antes de uso compartido. |
| Alta | `backend/app/models/project.py:113-115` une el identificador con el directorio sin validarlo; `:222-236` utiliza ese resultado en rmtree. Otros servicios también construyen rutas con identificadores. | Riesgo de escape de directorio, especialmente con separadores de Windows. Validar UUID y comprobar confinamiento de ruta. La explotabilidad por HTTP requiere comprobación específica de router/proxy. |
| Media | CORS permite cualquier origen en `backend/app/__init__.py:43`. | Amplía el acceso desde navegadores; no reemplaza autenticación. Restringir orígenes o usar mismo origen. |
| Media | El middleware registra cuerpos JSON (`backend/app/__init__.py:52-58`) y numerosas respuestas incluyen traceback (`backend/app/api/simulation.py`). | Posible exposición de documentos, conversaciones y detalles internos. Redactar logs y devolver errores públicos con identificador. |
| Media | Zep es obligatorio en `Config.validate`; el grafo y su memoria usan el cliente remoto de Zep. | Documentos y memorias salen del equipo. Sustituir por persistencia local y hacer explícito cualquier envío a proveedores LLM. Zep no se clasifica aquí como servicio chino. |
| Media | Archivos JSON y estado de tareas/procesos en memoria; no se observó un sistema durable de trabajos en los módulos revisados. | Recuperación y concurrencia limitadas. Usar SQLite transaccional, estados persistentes y cancelación/recuperación de trabajos. |
| Media | `.env.example` recomienda DashScope/Qwen; `docker-compose.yml` incluye un mirror chino comentado y una imagen externa con etiqueta latest. | Configuración y suministro poco controlados para nuestra versión. Eliminar presets/mirrors y construir artefactos propios con versiones verificadas. El mirror comentado no está activo. |
| Media | No se encontró CI de pruebas; el workflow revisado construye/publica Docker. Hay scripts de prueba, por lo que no corresponde afirmar que no existen pruebas. | Añadir comprobaciones del motor, aislamiento, cancelación, presupuestos y recuperación antes de publicar. |

No se identificó evidencia de malware en esta revisión limitada. El idioma u origen de un proyecto no constituye por sí mismo evidencia de riesgo.

## Calidad de las simulaciones

No se encontró en los archivos revisados una evaluación contra resultados reales, calibración de probabilidades o protocolo de backtesting. Los perfiles y narrativas generados por LLM no equivalen a una población representativa. Repetir relatos plausibles tampoco demuestra precisión.

Nuestra versión deberá distinguir fuentes, supuestos, eventos simulados e interpretaciones; guardar configuración, versiones, semillas cuando apliquen y métricas de costo; comparar múltiples ejecuciones y escenarios. No prometer reproducibilidad exacta de proveedores LLM remotos.

## Qué significa eliminar los componentes chinos

Para este proyecto se interpreta como: traducir interfaz, prompts, mensajes y documentación al español; sustituir ejemplos culturales por casos pertinentes; quitar DashScope/Qwen y mirrors chinos de la configuración; evitar servicios chinos obligatorios y revisar dependencias por función, licencia y conexiones externas.

OASIS/CAMEL son bibliotecas Python: quitarlas exige reemplazar el motor, no solamente traducirlo. Se propone un motor propio para reducir acoplamiento. Los avisos de autoría y licencia del material reutilizado deben conservarse.

## Licencia

El repositorio contiene GNU AGPL v3 (`LICENSE`); el backend declara AGPL-3.0. Modificarlo no elimina sus obligaciones: la sección 13 trata la oferta de código correspondiente a usuarios que interactúan remotamente con una versión modificada. Traducir o portar código no lo vuelve automáticamente independiente.

Fuente primaria: https://github.com/parety/Miro-Fish/blob/985f89f49acbb44ee14d9d680682c741a44eeebe/LICENSE

Antes de distribuir, definir si se hará una derivación AGPL o una implementación independiente sin copiar código, prompts ni recursos. Este informe es una observación técnica de la licencia, no un dictamen jurídico. Por ahora no se ha incorporado código original a la aplicación propia.
