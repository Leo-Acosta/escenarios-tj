# Mesa del expediente · avance de fase 2

6 de octubre de 2026.

## Funcionalidad

En `/app/`, elegir **Editar expediente**. Se puede abrir un expediente existente o crear uno nuevo. La preparación solicita objetivo, horizonte, datos, fundamento de pagos y fundamento de probabilidades. Después se habilita el modelo bimatricial 2×2, con actores, estrategias, ocho pagos, p/q, fuentes y supuestos.

**Guardar borrador** conserva campos incompletos sin inventar resultados. **Calcular y guardar versión** requiere preparación completa, valores válidos, supuestos y revisión explícita. Python valida y calcula; SQLite conserva una nueva versión y mantiene las anteriores.

La interfaz indica cambios sin guardar y evita cambiar el expediente mientras están pendientes. Al cambiar de sección o cerrar la página, advierte sobre esos cambios. No hay autoguardado todavía. Una respuesta HTTP 409 conserva los campos locales, bloquea la escritura y permite recargar la revisión actual. No hay fusión automática de conflictos.

## Verificación

- 95 pruebas Python correctas; 7 pruebas TypeScript de contratos, escritura, conflicto y validación de cálculo.
- Compilación TypeScript y Vite correcta.
- Flujo de navegador en una base independiente `data/qa-react-editor.sqlite3`, puerto 8767: creación, cinco respuestas, ocho pagos, borrador, fuente, revisión y versión 1.
- Recuperación después de recargar: pagos, fuentes y supuestos conservados.
- Escritura concurrente simulada: la revisión 8 se rechaza tras un guardado de revisión 9; el pago local 4 permanece visible y no sobrescribe el pago 3 del servidor.
- Recarga y cálculo de versión 2 con q=0,6. Comprobación de que la versión 1 conserva q=0,5 y utilidades 1,5/3; la segunda corresponde a 1,8/3,4 para el actor A.
- Sin errores o advertencias en consola durante el flujo.
- No se cambió el esquema ni se migraron datos de la aplicación principal. Los datos de prueba quedan fuera del repositorio.

## Pendiente

La fase 2 completa requiere navegación integral y edición de todos los módulos, además de accesibilidad y pruebas de componentes más amplias. Todavía se usan la interfaz anterior para árboles, agentes, IA local y exploraciones. El informe ejecutivo unificado, el autoguardado y la recuperación automática de conflictos corresponden a próximos avances.
