# Sensibilidad Monte Carlo en React

## Uso

Laboratorio de árboles → Crear árbol o Editar como nueva versión → Explorar incertidumbre en los pagos. Configurar 100–5000 repeticiones, semilla entera 0–4294967295 y amplitud no negativa. Los intervalos de los ocho pagos deben permanecer dentro de ±1000000. Registrar supuestos, revisar y guardar. Cualquier cambio invalida la revisión anterior.

Al editar, Monte Carlo comienza desactivado. Si se activa sobre una versión simulada se recupera su configuración, pero se ejecuta una nueva simulación: no se reutilizan resultados ni se altera el original. Desactivado guarda únicamente el modelo base. No se modificó el motor Python ni se añadieron dependencias.

## Resultados conservados

Tres categorías excluyentes: únicamente primera decisión, únicamente segunda decisión, ambas compatibles. Los conteos por ruta pueden superponerse y no deben sumarse. Se muestran P5 del mínimo y P95 del máximo de utilidad de A entre los equilibrios simulados; no son intervalos de confianza ni utilidades de una política fija.

El selector Escenario del gráfico permite consultar el modelo base y hasta 20 muestras guardadas. El diagrama utiliza sus pagos y rutas devueltas por Python; JavaScript no resuelve los juegos. La consulta de un nodo muestra pagos de esa muestra. Los planes completos y la tabla terminal se identifican explícitamente como modelo base. Seleccionar un plan del modelo base devuelve el gráfico al modelo base.

El panel conserva las opciones y supuestos de uniformidad, independencia e información perfecta. Las frecuencias no representan probabilidades empíricas de conducta. El PDF individual existente incorpora el resumen de simulación de la versión guardada. El informe ejecutivo unificado permanece pendiente en fase 6.

## Verificación

Compilación TypeScript/Vite aprobada. 23 pruebas frontend y 19 Python/API (4 de simulación, 15 HTTP) aprobadas. Nuevas pruebas cubren: amplitud cero frente a campo vacío, límites, semilla, frecuencias coherentes con conteos, versión del motor admitida, rutas superpuestas y actualización del gráfico sin modificar el modelo base.

En navegador sobre base aislada data/qa-react-tree-editor.sqlite3, puerto 8767: activar Monte Carlo, guardar 100 repeticiones con semilla 9 y amplitud 3, invalidar revisión al cambiar amplitud, seleccionar muestras 1 y 20, consultar nodo y regresar al modelo base. Resultado conservado: 82 repeticiones solo Entrar, 18 solo Esperar. Otra nueva versión con amplitud cero conservó Entrar 100/100 y utilidad 4. La versión con amplitud 3 permaneció intacta.

Caso de empate total preparado en la base aislada: ambas decisiones compatibles 100/100, cuatro rutas 100/100 y ocho planes completos. La consulta tras recarga conservó resultados y configuración. La base principal no recibió escrituras de prueba. La herramienta de captura no pudo producir una imagen de esta sesión; se verificaron el estado accesible y los controles en navegador, sin captura visual exportable.

## Fase y límites pendientes

Fase 2 continúa: el control avanzado de sensibilidad de árboles ya está integrado a React y usa los gráficos de la base de fase 4. Pendientes IA local, redes y reproducción detallada de políticas en React. No incorpora distribuciones correlacionadas, calibración con datos ni árboles de tamaño general. No hay autoguardado de borradores (fase 5) ni informe ejecutivo unificado (fase 6).
