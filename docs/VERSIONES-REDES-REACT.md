# Versiones y asociación de redes

React permite conservar la red global cargada como una nueva versión, con título, fundamento, revisión explícita y expediente opcional. Las versiones se consultan por expediente o globalmente. El mapa guardado incluye todos los nodos y relaciones, sin aplicar filtros visuales. Cambiar título o fundamento invalida la revisión. Hay protección de borradores al navegar y al cerrar; todavía no se autoguardan.

GET /api/graph/versions filtra por workflow_id antes del límite de 30. POST agrega un UUID y fecha UTC en graph_versions con INSERT; guarda la revisión, título e ID históricos del expediente, validado por Python. No modifica la tabla graph existente ni registros previos. No existe migración automática de la red global: conservarla es una acción explícita. La asociación no deriva vínculos desde una matriz ni aporta evidencia causal. El editor de entidades sigue en la mesa anterior; la red global y las copias conservadas se distinguen en pantalla.

Validación: 26 pruebas frontend; 106 pruebas Python; compilación TypeScript/Vite aprobada. Bases temporales verifican versiones independientes, contexto congelado, supuestos, revisión y referencia inexistente (404). Navegador en puerto 8768 y data/qa-network-react.sqlite3: se guardó b43af485-8322-4654-a4cb-f6a15ce9e4a4 con expediente revisión 1 y filtro Vecinos; se conservaron 3 entidades y 2 vínculos. Editar el título después de revisar deshabilita guardar. Una segunda versión bfa9b53b-de14-41ae-92ce-49a1c06abf94 permite volver a consultar la primera con su título y fundamento originales. No se guardaron redes de prueba en la base principal.

Fase 2 en curso. Pendientes: edición de redes en React, evidencia por vínculo y controles de IA local. Informe ejecutivo unificado: fase 6.
