# Laboratorios del expediente en React

## Uso y alcance

Desde Centro de análisis → Agentes, políticas e incentivos o la barra lateral → Laboratorios del expediente. Tres vistas: agentes con memoria, comparación de políticas y exploración de incentivos. El selector de expediente filtra versiones guardadas; sin expediente se consultan también registros históricos independientes. Cada selección devuelve sus últimos 20 análisis, después de filtrar.

Para ejecutar: seleccionar una matriz calculada del expediente, configurar el laboratorio, fundamentar las hipótesis, revisar y guardar. Python recupera la matriz congelada; no acepta una matriz enviada por el cliente como sustituto. El registro conserva workflow.id, workflow.title y workflow.version junto con el modelo y resultados. No hay migración ni modificación de registros previos.

Agentes: políticas de A/B, rondas 1–500, semilla y error de ejecución. Gráfico de utilidad acumulada por actor, selección de ronda con teclado/deslizador y detalle de decisiones, pagos, acumulados y motivos.

Comparación: 1–100 rondas, 1–10 repeticiones por combinación, semilla común y error de ejecución. Mapa de calor de 36 combinaciones, selección de actor y celda, media, dispersión y extremos calculados por Python. El color se normaliza para el actor seleccionado; no compara escalas de A y B. La dispersión no es un intervalo de confianza.

Incentivos: selección de un pago de A/B, fila y columna y rango creciente. 101 muestras resueltas en Python, gráfico de utilidades esperadas por estrategia del actor seleccionado y detalle de pagos/equilibrios puros por muestra. No estima umbrales exactos ni conducta observada.

Se muestran la matriz de origen, configuración, fundamento y límites. Cada resultado abre el expediente actual y sus PDF individuales existentes; agentes e incentivos ofrecen CSV. No se ha generado el informe ejecutivo unificado de fase 6 ni se ha incorporado el vínculo al expediente dentro de esos PDF.

## Verificación

Compilación TypeScript/Vite aprobada; módulo separado, cargado al abrir laboratorios, sin nuevas dependencias. 20 pruebas frontend y 103 Python aprobadas. La prueba HTTP de los nuevos endpoints se repitió tras ampliar el límite de cuerpo para fundamentos extensos: 15 API aprobadas.

Cobertura: origen congelado, rechazo de revisión faltante, versión inexistente, configuración inválida, históricos independientes, filtro anterior al límite y rechazo de contratos no finitos/incompatibles. Se comprueba que una matriz alterada en el cliente no reemplaza la fuente.

En navegador, base aislada data/qa-laboratorios-react.sqlite3 en puerto 8767: guardado de agentes (12 rondas), comparación (12 rondas y dos repeticiones) e incentivos (0–10); selección de última ronda, actor, última muestra y celda; regreso al expediente; consulta tras recarga. Se comprobó que cada registro conserva la versión 1. La base principal no recibió escrituras de prueba. Capturas en output/screenshots/laboratorio-*-integrado.png.

## Pendientes y fase

Fase 2 en curso, con los laboratorios de árboles, agentes, comparación e incentivos integrados. Los borradores de configuración se conservan en memoria durante la vista, con aviso al salir; todavía no hay autoguardado. Cambiar laboratorio o expediente restablece la configuración tras confirmar si había cambios. La repetición detallada de comparaciones, controles avanzados Monte Carlo, IA local y redes mantienen sus interfaces anteriores. Las redes y gráficos enlazados avanzados corresponden a fase 4; respaldo/autoguardado a fase 5 y el informe ejecutivo unificado a fase 6. La integración no demuestra capacidad predictiva empírica.
