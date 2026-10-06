# Navegación del expediente por etapas

## Estado de fase

Fase 1: base React + TypeScript y consulta de expedientes implementadas.

Fase 2: en curso. Ya incluye creación y edición de expedientes, cálculo revisado y cuatro etapas de navegación. Falta integrar la navegación de árboles, agentes, exploraciones e IA, completar la coherencia entre módulos y ampliar la validación de accesibilidad e impresión. Las fases 3 a 10 no se consideran cerradas por estas entregas.

## Avance de esta entrega

- Preparación, Modelo, Fundamentos y Revisión se muestran como etapas separadas, conservando los cambios locales al cambiar de etapa.
- Expedientes con preparación pendiente mantienen bloqueadas las etapas posteriores. Al completar la última respuesta se abre el modelo.
- Pestañas con roles y relaciones ARIA; navegación con flechas, Inicio y Fin. Controles Anterior/Continuar y guardado de borrador en las etapas del modelo.
- Revisión muestra título, actores, número de fuentes, probabilidades, matriz completa y supuestos que se enviarán al motor. El resumen no calcula ni anticipa resultados.
- Las fuentes incompletas se detectan antes de guardar. La revisión conserva el requisito de confirmación explícita y se invalida cuando cambia el modelo.
- La impresión de la etapa Revisión conserva su resumen y oculta acciones; no equivale todavía al informe ejecutivo unificado. Pendiente la comprobación visual de impresión.

## Evidencia de verificación

6 de octubre de 2026: 95 pruebas Python y 8 TypeScript correctas; compilación TypeScript/Vite correcta.

En navegador: Modelo → Fundamentos con flecha derecha, Fundamentos → Revisión con Fin. En una base aislada, un pago cambiado a 4 aparece como 4/3 en el resumen; al regresar al modelo se conserva. Tras confirmar y modificar de nuevo ese pago, el cálculo vuelve a estar deshabilitado hasta una nueva confirmación. Guardar borrador desde Revisión mantiene esa etapa y conserva dos versiones previas. Sin errores o advertencias en consola durante este flujo.

La base principal conserva su esquema y datos. No hay migración en esta entrega. El servicio de prueba usa una base independiente fuera del repositorio.

La captura automatizada falló durante esta sesión; la evidencia disponible es la comprobación del estado visible del navegador y las pruebas anteriores. No se reemplazó con una captura de una versión anterior.
