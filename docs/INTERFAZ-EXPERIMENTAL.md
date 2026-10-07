# Interfaz experimental · blanco y oliva

Implementada el 7 de octubre de 2026 en `/app/`, con React/TypeScript compilado a JavaScript. Python conserva los cálculos y SQLite los registros. No incorpora dependencias externas ni modifica matrices, evidencias o pronósticos.

La superficie utiliza blanco, oliva militar y tonos suaves de salvia, una retícula de fondo, navegación numerada y una franja de contexto con expediente, versión seleccionada y validación empírica pendiente. El indicador orbital es decorativo, no representa una simulación ni un estado de conexión. El modo inmersivo oculta la navegación y amplía el área de trabajo; su botón permite restaurarla sin descartar el expediente o borradores.

Se conservan los controles de descarte, navegación por teclado, foco visible, selección de versiones y módulos existentes. Las reglas adaptables contemplan 650 y 1000 píxeles. Los adornos y controles de presentación se excluyen de la impresión. Los PDF ejecutivos conservan su diseño propio anterior.

Verificación: compilación TypeScript/Vite correcta; 59 pruebas frontend aprobadas. Navegador local: contexto de expediente, navegación y activación/desactivación del modo inmersivo comprobados mediante el árbol de accesibilidad. Dos intentos de captura devolvieron «Unable to capture screenshot»; el acabado visual, todos los tamaños móviles y la salida física de impresión quedan pendientes de inspección visual. No se atribuye a esta intervención el cierre completo de la fase 4.

Siguiente desarrollo: ampliar gráficos vinculados a variables y versiones, unificar las paletas internas de todos los gráficos sin perder distinción entre actores y verificar composición visual en escritorio y móvil. Después: recuperación de borradores y respaldos (fase 5), evidencia independiente para fase 8 e instalación/calidad Windows (9–10).
