# Fase 12 · Estudio visual de análisis integrado

Cierre funcional: 17 de noviembre de 2026. Núcleo Python y SQLite; interfaz React/TypeScript con React Flow, blanca y azul marino. La integración no acredita mejora predictiva real.

## Auditoría y alcance

Se reutilizaron los motores de matrices 2×2, árboles de dos etapas con información perfecta, Monte Carlo, diccionarios de variables, informes ejecutivos y continuidad. Ya existían redes versionadas; faltaban fichas, dirección y semántica de relaciones, posiciones persistentes y un escenario que congelara referencias de varios laboratorios. No se duplicaron los motores ni se amplió su dimensión.

## Implementación

- Estudio con lienzo, inspector de actores/contactos, grupos, búsqueda, filtros, minimapa, zoom y distribuciones manual, circular, cuadrícula o grupos. Posiciones y cámara forman parte de la versión conservada. Deshacer/rehacer conserva hasta 80 estados del borrador; formularios y coordenadas ofrecen una alternativa a arrastrar o conectar puertos.
- Fichas con organización, función, descripción, contacto opcional, fuente y notas. Relaciones dirigidas o no dirigidas, etiqueta, estado de evidencia, fechas y peso opcional con unidad, significado y escala obligatorios. Un peso no se interpreta como probabilidad; una flecha no demuestra causalidad.
- Redes con esquema 2 y UID estable. Los registros antiguos se abren como nuevos borradores enriquecidos, sin sobrescribir históricos ni inferir pesos o dirección. Se validan duplicados, referencias, fechas, tamaños y valores finitos.
- Escenarios con revisión o clonación independientes, copias completas de matriz, red, árbol y diccionario opcional, variables, restricciones, escalas y asignaciones de actores. Advertencias sobre versiones nuevas sin actualizar las copias congeladas. Apertura del árbol exacto y retorno al estudio conservando contexto.
- Transformaciones de variables y restricciones son declaraciones revisadas, no fórmulas ejecutables. Los pagos cambian únicamente al elegir una matriz calculada y revisada. No hay propagación automática desde vínculos, evidencia o textos.
- Comparación de dos escenarios: diferencias de configuración, equilibrios y utilidades por actor. Deltas sólo con escalas explícitamente compatibles y mismas etiquetas de actores y alternativas. No se agregan utilidades de actores distintos.
- Informes unificados con escenarios, matrices, redes, árboles y simulaciones seleccionados. La comparación también queda congelada y verificada. HTML, PDF A4 vectorial, SVG de red y JSON completo. El informe usa referencias legibles; identificadores y huellas permanecen en JSON para auditoría.
- PDF: mapas en láminas de hasta 12 nodos, inventario completo y tabla de todos los vínculos, incluidos los que cruzan láminas. La distribución se adapta para imprimir; SVG/JSON conservan las posiciones originales. Perfiles, notas y evidencia completa se conservan en JSON. No se omiten nodos por reducir etiquetas.

## Persistencia, recuperación y privacidad

Tabla nueva `studio_scenarios(id, workflow_id, payload)`, integrada a la lista de tablas permitidas del respaldo. Antes de crearla en una base no vacía se guarda y verifica una copia SQLite en el directorio hermano `migration-backups`, con metadatos de integridad. Se conservan registros originales; no se reescriben análisis congelados.

El esquema global de continuidad sigue siendo 1; versiones anteriores de la aplicación pueden rechazar tablas desconocidas. Para abrir una base con escenarios visuales se necesita esta versión o una posterior compatible. La restauración se realiza en una base separada y fue probada con redes y escenarios.

La base principal se verificó mediante SHA-256 antes y después: no cambió. EDESUR no se utilizó en la demostración. Los datos, originales, PDFs privados, bases, respaldos e instaladores permanecen excluidos de Git. Los contactos se almacenan localmente y quien exporta JSON debe revisar su contenido antes de compartirlo.

## API y límites operativos

Lecturas: `/api/studio/catalog`, `/network`, `/record`, `/export`, `/replay`, `/compare`, `/svg`. Escrituras revisadas: `POST /api/studio`, acciones `network`, `scenario` y `report`. Se mantienen controles Host/Origin; estados 400/404/409 para errores o conflictos. Una revisión simultánea incompatible no sobrescribe el historial.

Límites: 200 nodos y 1000 vínculos por red, 3 MiB por solicitud. El catálogo presenta hasta 30 redes y árboles, y 100 matrices y escenarios; no es un buscador paginado de archivos históricos ilimitados. Se conserva el límite de respaldo de continuidad existente. Sólo dos escenarios por comparación/informe del estudio; otros laboratorios siguen disponibles en el informe general.

## Demostración reproducible

Usar una base nueva; el generador rechaza una ruta existente:

```powershell
python -m scripts.demo_visual_studio data/demo-estudio-nuevo.sqlite3
python -m escenarios.server --database data/demo-estudio-nuevo.sqlite3 --port 8780
```

Abrir `http://127.0.0.1:8780/app/?view=studio`. Construir previamente `frontend` mediante `npm ci` y `npm run build`; PDF requiere ReportLab según README.

Puerto Aurora es completamente ficticio: 18 entidades y 26 relaciones iniciales; matriz base y variante de crisis; árboles y simulaciones conservados; escenarios comparables; informe y restauración separados. En la demostración de interfaz se agregó un equipo ficticio de seguimiento y su vínculo dirigido, formando una red de 19 entidades y 27 relaciones, sin alterar escenarios anteriores.

Recorrido: **Lienzo y contactos** → seleccionar actor, editar posición/ficha o crear conexión, revisar y conservar → **Escenarios conectados** → clonar, seleccionar versiones y revisar asignaciones → abrir árbol/matriz y volver → **Comparar e informar** → elegir dos versiones, comparar, revisar, emitir PDF/HTML/JSON y comprobar reproducción. Las exportaciones de una red conservada no incluyen borradores sin guardar.

## Verificación y criterios de aceptación

- 204 pruebas Python aprobadas; 85 pruebas TypeScript aprobadas; compilación tsc/Vite aprobada.
- Integración HTTP, Origin, referencias inválidas y cruzadas, conflictos de revisión, transformación sin fundamento, compatibilidad de escalas, integridad y manipulación de huellas probadas.
- Migración con respaldo, restauración separada, históricos, escenarios y reproducción del informe desde copias congeladas, incluso eliminando las fuentes originales en una base de prueba.
- Navegador integrado: edición por coordenadas, deshacer/rehacer, guardar/reabrir, actor y conexión por formulario, filtros, clonación y asignaciones revisadas, comparación, apertura del árbol exacto, emisión y reproducción del informe. Sin errores de consola observados al cerrar el recorrido.
- PDF de demostración: 23 páginas A4; renderizadas y revisadas en conjunto, con inspección ampliada de mapas/tablas y comparación. Se corrigió la colisión de valores negativos con etiquetas de estrategias. SVG/JSON y separación de mapas con más de 12 nodos cubiertos por pruebas.

Los criterios funcionales 1–7 están cubiertos. El criterio 8 tiene verificación de navegador/formularios y exportaciones, con los límites siguientes. El criterio 9 se cumple registrándolos; el criterio 10 mediante código, pruebas y esta documentación en GitHub.

### Límites de aceptación que permanecen visibles

La captura del navegador integrado devolvió un error. Se pudo observar y operar su árbol accesible, pero no certificar mediante captura la apariencia final del lienzo. El arrastre con puntero y la conexión física de puertos no se verificaron independientemente; sí su alternativa mediante formularios y coordenadas, persistencia y lógica de datos. No se certifican en esta fase móvil, tecnologías de asistencia completas, impresión nativa/física ni compatibilidad visual de todos los navegadores. El PDF generado se verificó de forma independiente de la impresión HTML.

La implementación funcional de la fase 12 queda cerrada con estos límites de verificación documentados. La aceptación visual manual pendiente no se presenta como aprobada. El instalador anterior no se reconstruyó para esta fase: debe actualizarse si se desea distribuir estas funciones en el paquete instalado.

## Qué sigue

P-EMP-01 permanece abierto: faltan observaciones reales independientes para acreditar predicción, con protocolo temporal y referencias congeladas. No hay nuevas inferencias de IA en reproducción ni probabilidades judiciales inventadas.

Una fase posterior separada puede ampliar matrices N×M, más actores, árboles de profundidad arbitraria y transformaciones matemáticas ejecutables; requiere especificación y validación propias. No se simulan esas capacidades en el lienzo actual.
