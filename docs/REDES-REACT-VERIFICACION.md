# Red de relaciones en React

Consulta del mapa global guardado en /api/graph. React Flow ofrece zoom, ajuste de vista y minimapa; búsqueda, filtros por entidad y relación, selección por nombre y detalle de conexiones. Los nombres y vínculos se leen de Python. No se generan datos de demostración cuando no existe una red guardada.

Esta integración es de consulta. El editor sigue en la mesa anterior. El registro global se reemplaza al guardar allí: no tiene versiones, asociación a expedientes ni evidencia documental. No se atribuye dirección causal a los vínculos. La asociación y conservación de versiones requieren un incremento posterior.

Validación: 25 pruebas de interfaz aprobadas, incluyendo referencias rotas y tipos inválidos en redes; compilación TypeScript/Vite aprobada. Navegador: estado vacío de la base principal y mapa aislado de tres entidades y dos relaciones en data/qa-network-react.sqlite3, puerto 8767. Selección de Vecinos muestra ambas relaciones; abrir Cooperación y buscar Acuerdo muestra una entidad, cero relaciones y aviso de relación oculta. No se escribió una red de prueba en la base principal.

Fase 2 en curso; base gráfica de fase 4. Informe ejecutivo unificado pendiente en fase 6.
