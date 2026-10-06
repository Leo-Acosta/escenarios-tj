# Reproducción de agentes en React

El laboratorio de agentes incorpora reproducción del historial conservado: iniciar, pausar, tres velocidades, pasos anterior/siguiente, reinicio y selección con deslizador accesible por teclado. La selección sincroniza pagos, acumulados, motivos y marcador del gráfico. No se recalculan decisiones ni se escribe en SQLite.

El temporizador se cancela al pausar, cambiar de ronda, desmontar el resultado o cambiar la velocidad. Se detiene en la última ronda, al ocultar la pestaña y antes de imprimir. No inicia automáticamente. Reproducir desde el final vuelve al inicio. Los controles se ocultan al imprimir.

## Validación

- 23 pruebas existentes de contratos y edición: aprobadas. No son pruebas automatizadas del reproductor.
- TypeScript y compilación Vite: aprobados.
- Navegador, análisis histórico de 50 rondas: paso a ronda 2, velocidad rápida, avance automático a ronda 6 y pausa; teclado End selecciona ronda 50 y deshabilita avance; reinicio; reproducción desde ronda 49 termina automáticamente en ronda 50.
- Verificación de consulta sobre un análisis existente, sin crear versiones ni modificar la base principal.

La fase 2 sigue en curso. La reproducción corresponde a políticas simuladas por el núcleo Python; no representa agentes de IA ni validación predictiva. IA local y redes siguen pendientes de integración. El informe ejecutivo unificado permanece en fase 6.
