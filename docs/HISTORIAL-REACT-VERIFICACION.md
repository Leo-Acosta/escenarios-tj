# Historial integrado del expediente

Avance de fase 2 · 6 de octubre de 2026.

La mesa del expediente incorpora las vistas **Edición** y **Versiones**. El historial permite elegir una versión conservada y ver su matriz, probabilidades, utilidades, equilibrios, supuestos y límites. La presentación de los resultados comparte el componente del Centro de análisis. Las consultas no actualizan ni recalculan versiones.

Abrir una versión en el Centro de análisis conserva la selección exacta. Mientras hay cambios locales, esta acción se deshabilita; se puede consultar el historial y volver al editor conservando esos cambios. Las peticiones se cancelan al cambiar de versión o salir del historial; incluye estados vacío, carga, error y reintento.

## Verificación

- 8 pruebas TypeScript aprobadas y compilación TypeScript/Vite correcta.
- Navegador: apertura del historial de tres versiones; versión 1 recupera q=50 %, Acuerdo/Competir y utilidades 1,5/3, mientras la versión 3 conserva q=0 % y sus nombres de estrategias. Abrir la versión 1 en el Centro de análisis mantiene la versión 1 seleccionada.
- Prueba de cambios locales: un título temporal se conserva al pasar al historial y volver; la acción para salir al Centro de análisis permanece deshabilitada. La prueba no guardó cambios en SQLite.
- No se alteraron API, cálculos Python o esquemas de datos. No se requirió migración.

## Fase actual y pendientes

**Fase 2 en curso: experiencia visual, navegación y contexto del expediente.** Este avance incorpora el historial al mismo espacio de trabajo. Todavía falta integrar árboles, agentes, exploraciones e IA en la nueva navegación y completar las comprobaciones de accesibilidad e impresión. No se considera cerrada la fase 2 ni las fases posteriores.
