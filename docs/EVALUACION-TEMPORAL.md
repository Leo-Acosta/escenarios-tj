# Guía de evaluación temporal

En React (`/app/`), abrir **Evaluación y experimentos**. Ollama es opcional para registro y cálculos; obligatorio para agentes decisores y asesor. Crear ejemplos sintéticos en una base separada y marcarlos explícitamente.

## Incorporar observaciones reales

1. Preparar un expediente con matriz calculada y revisada. No inventar pagos para habilitar un experimento. Ampliar primero el modelo si el objetivo no cabe en dos actores y dos alternativas.
2. Definir resultado 1, horizonte, documento de constatación y unidad independiente. Formular una predicción observable; no equipararla con éxito judicial.
3. Conservar protocolo antes de pronosticar: referencia, fuentes, supuestos y tres cierres futuros ISO con zona, desarrollo < validación < prueba. La referencia fija opcional obliga a usar su valor; un método declarado requiere revisión externa. Brier binario, semilla 42 y 1000 remuestreos quedan predefinidos.
4. Registrar candidatos durante desarrollo: método, corte de entrenamiento y comparación IA opcional de la misma matriz. Revisar la relación entre decisión y probabilidad; utilidad no equivale a probabilidad.
5. Emitir cada pronóstico antes del plazo: unidad estable, corte de información y disponibilidad de fuentes. El servidor asigna emisión y partición. No se admiten fuentes posteriores al corte ni unidades repetidas entre particiones. Varios candidatos sobre la misma unidad necesitan igual plazo y referencia.
6. Conservar resultado después del plazo, con documento y fecha. Verificar autenticidad fuera del sistema. No se sobrescribe. Evitar datos personales innecesarios y no compartir archivos privados mediante Git.
7. Ajustar solo con desarrollo. El asesor propone reunir observaciones o calibrar cinco intervalos con prior entero 1–10 y mínimo técnico de cinco observaciones. La revisión explícita crea otra versión y congela entrenamiento; datos modificados durante la revisión invalidan la propuesta. No se ejecuta ni promueve automáticamente.
8. Tras cerrar validación, evaluar todos los resultados y fundamentar selección manual. Solo ese candidato emite y evalúa prueba. Reservar datos independientes y no usarlos para ajustar; el sistema no puede impedir conocimiento externo de información futura.
9. La prueba no admite observaciones antes del cierre de toda su ventana. Completar pendientes y conservar una única evaluación final por protocolo. Un estudio posterior requiere protocolo nuevo y datos independientes, no reutilizar prueba para ajustar.
10. Reproducir sin IA, exportar JSON y abrir resumen imprimible. La evaluación contiene protocolo, candidato, selección, conjunto y métricas congelados. Imprimir/guardar PDF desde navegador; es resumen individual, no informe unificado de fase 6.

## Batería de simulaciones

Fijar referencias, rivales, semillas, rondas y perturbaciones antes de ejecutar. Hasta 12 condiciones distintas, 1–5 semillas únicas por condición, 1–20 rondas y 120 decisiones IA totales. Una batería extensa puede tardar horas. Cada comparación conserva trabajo hijo; fallos permanecen visibles. Reproducir recalcula decisiones registradas sin consultar Ollama.

Ajuste y evaluación: máximo 2000 observaciones. Pantalla: hasta 100 protocolos y 2000 eventos por protocolo. Historial de baterías/asesores: últimos cinco trabajos; decisiones: veinte. Ampliar volúmenes requiere paginación y evaluación de rendimiento. No es un servicio multiusuario ni autentica fuentes.

## Interpretar resultados

Brier menor es mejor; diferencia candidato menos referencia negativa favorece al candidato. Desarrollo y validación no reciben acreditación final. Datos sintéticos siempre se etiquetan como prueba funcional. En datos reales finales, diferencia favorable con intervalo totalmente negativo y al menos treinta eventos obtiene solo **mejora provisional**: revisar independencia, potencia, selección y validez externa.

Python verifica estructura, acciones, restricciones explícitas, fechas, cálculos y reproducción. No garantiza toda la coherencia semántica, autenticidad ni rendimiento futuro. Dos roles del mismo modelo no son revisores independientes. Ninguna evaluación modifica pagos, sustituye evidencias o promueve políticas automáticamente.

Las pruebas usan reloj controlado y datos sintéticos. Producción usa reloj real sin endpoint para alterarlo. No incorporar scripts locales de QA con reloj simulado.
