# Laboratorio de árboles en React

Acceso: /app/ → Laboratorio de árboles.

Consulta las últimas 30 versiones de /api/sequential. React Flow 12.12.0 (MIT) se carga en un módulo separado al abrir el laboratorio. No calcula equilibrios en JavaScript ni modifica la base de datos.

Incluye zoom, desplazamiento, minimapa, ajuste de vista, selección de nodos, filtro de rutas de equilibrio, planes completos de respuesta de B y tabla de los cuatro escenarios terminales. Los títulos y controles principales están en español. El PDF enlaza al informe existente de la versión conservada.

Validación: compilación TypeScript/Vite correcta, 13 pruebas frontend y 5 pruebas Python secuenciales aprobadas. Los contratos rechazan dimensiones e índices inválidos y números no finitos. La prueba de empates conserva ocho planes. En navegador se verificó el caso Entrada a un mercado: selección Acomodar, pagos 2 / 1, filtro del equilibrio, zoom y ajuste de vista. Captura en output/screenshots/laboratorio-arboles-react.png.

La compilación avisa que la directiva use client de React Flow se omite en este frontend cliente; no impide la compilación. La instalación informó cero vulnerabilidades en 44 paquetes.

Alcance pendiente: creación y edición de árboles desde React, integración del expediente con otros laboratorios, árboles más generales, gráficos de redes y sensibilidad. Los árboles actuales tienen dos actores, dos etapas y dos alternativas por nodo; pagos hipotéticos sin calibración predictiva. La fase 2 continúa en desarrollo y la fase 4 aún no está completa.

## Edición y creación en React

El laboratorio permite crear árboles vacíos o copiar el modelo de una versión. Define título, dos actores, seis alternativas, ocho pagos y supuestos. Cada modificación invalida la revisión previa; guardar exige una nueva confirmación. Las versiones se guardan mediante POST /api/sequential y se abren directamente en el gráfico. No se reemplaza el original ni se copian sus simulaciones/propuestas de IA. Los borradores permanecen en memoria; hay aviso al salir y todavía no hay autoguardado.

Validación del incremento: 16 pruebas frontend, 5 secuenciales y 13 API aprobadas; compilación correcta. En navegador, sobre data/qa-react-tree-editor.sqlite3 y puerto 8767, se rechazó un pago vacío y se comprobó que corregirlo desactiva guardar hasta renovar la revisión. El guardado produjo dos UUID distintos; el pago original quedó en 2 y la versión nueva en 4. La base principal no recibió escrituras de prueba.

Fase 2 en curso: creación, revisión, cálculo y consulta de árboles incorporados a React. Pendientes la integración con expedientes y otros laboratorios, y los demás gráficos de fase 4.
