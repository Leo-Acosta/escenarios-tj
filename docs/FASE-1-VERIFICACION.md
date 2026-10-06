# Fase 1 · verificación

6 de octubre de 2026.

- Compilación TypeScript y Vite correcta. JavaScript generado: 231,93 kB, 72,61 kB comprimidos con gzip; CSS: 6,22 kB. Son tamaños de compilación, no una prueba de velocidad en dispositivos reales.
- 95 pruebas Python correctas, incluyendo API, motor, exportaciones y contención de rutas de los archivos compilados.
- 3 pruebas TypeScript correctas: conservación de resultados recibidos, rechazo de matrices/probabilidades/índices inválidos y contratos de expedientes/biblioteca.
- `npm audit`: cero vulnerabilidades conocidas en el momento de la consulta.
- Navegador: apertura de `/app/`, expediente existente, versiones 3 y 1; versión 1 recupera q=50 %, estrategias Acuerdo/Competir y utilidades 1,5/3. Biblioteca muestra 11 versiones y enlaces PDF/CSV de los módulos existentes. Sin mensajes de error o advertencia en consola durante la comprobación.
- Comprobación del ancho del documento en las vistas reducidas, sin desbordamiento global. La captura automatizada dejó de funcionar después de cambiar el tamaño del navegador; la validación móvil visual exhaustiva queda pendiente.
- No se modificó el esquema de SQLite ni se migraron datos. La vista React realiza consultas de lectura.

Pendiente: pruebas de componentes con interacciones automatizadas, revisión formal de accesibilidad y de impresión, vinculación de documentos al expediente y las siguientes fases descritas en la arquitectura. La apariencia inicial y la compilación no acreditan por sí solas todos los criterios de producto premium.
