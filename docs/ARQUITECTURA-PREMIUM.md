# Migración premium · fase 1

## Arquitectura implementada

React y TypeScript en `frontend/` consumen la API local del servidor Python. Vite genera archivos estáticos en `frontend/dist/`, servidos por el mismo proceso en `/app/`. La interfaz previa permanece en `/`. SQLite y el motor matemático conservan sus esquemas y comportamiento; esta fase no requiere migración de datos.

El Centro de análisis consulta expedientes, abre versiones inmutables y muestra pagos, equilibrios, utilidades esperadas, supuestos y límites recibidos del núcleo. La mesa del expediente permite crear casos, responder las cinco preguntas de preparación, editar el modelo y sus fuentes, guardar borradores y calcular nuevas versiones con revisión explícita. La biblioteca enlaza los PDF y CSV ya existentes. Las matrices de expediente pueden imprimirse desde el navegador; todavía no tienen un PDF ejecutivo propio. Los documentos de otros módulos pertenecen a sus versiones guardadas y no se vinculan automáticamente al expediente elegido.

Contratos TypeScript con validación en tiempo de ejecución: `/api/workflows`, `/api/workflows?id=…`, `/api/workflows?id=…&version=…` y `/api/library`. Solicitudes cancelables evitan que una respuesta tardía sustituya la selección actual. Hay estados de carga, vacío, error y reintento. No se calculan utilidades en JavaScript.

## Construcción reproducible

Requisitos: Python del proyecto y Node >=22.12; Vite también admite Node 20.19 según sus metadatos, pero este proyecto fija el mínimo indicado arriba.

```powershell
cd frontend
npm ci
npm test
npm run build
cd ..
python -m escenarios.server --port 8766
```

Abrir `http://127.0.0.1:8766/app/`. La instalación inicial requiere el registro npm; la aplicación compilada funciona sin red externa. No usa CDN, fuentes remotas ni telemetría. `npm run dev` ofrece desarrollo con proxy, pero la validación de esta fase usa la compilación servida por Python.

## Dependencias directas verificadas en npm

| Paquete | Versión | Licencia | Uso |
|---|---|---|---|
| @xyflow/react | 12.12.0 | MIT | Laboratorio interactivo de árboles |
| React / React DOM | 19.3.0 | MIT | Interfaz |
| Vite | 8.3.3 | MIT | Compilación |
| TypeScript | 7.0.2 | Apache-2.0 | Contratos y tipado |
| @types/react / @types/react-dom | 19.3.0 | MIT | Tipos |

Versiones fijadas y dependencias transitivas registradas en `package-lock.json`. Inventario completo: `npm ls --all`; auditoría: `npm audit`. No se ha realizado una auditoría legal completa de todas las dependencias transitivas.

## Fases siguientes

2. Sistema visual y navegación integral; formularios de edición y contexto unificado.
3. Variables con unidades, fuentes y relación explícita con cálculos.
4. Árboles React Flow, redes Cytoscape y gráficos Plotly enlazados a versiones.
5. Autoguardado, respaldo y recuperación; migraciones verificables.
6. Informe ejecutivo del expediente, basado en una versión congelada.
7–8. Ampliación matemática y evaluación predictiva con datos observados.
9–10. Distribución Windows y validación integral de calidad y rendimiento.

La fase 1 incorporó la consulta. La fase 2 está en curso: agregó edición, cálculo, navegación por etapas e historial de versiones dentro del expediente. La navegación integral, los gráficos y los demás requisitos premium siguen en desarrollo. Ver `NAVEGACION-ETAPAS-VERIFICACION.md` y `HISTORIAL-REACT-VERIFICACION.md` para las comprobaciones de estos incrementos.

El laboratorio React consulta árboles conservados con React Flow, selección de nodos, rutas y planes completos. La fase 2 sigue en curso; este incremento inicia la base visual de árboles de la fase 4, sin completar esa fase. Ver `ARBOLES-REACT-VERIFICACION.md`.

La fase 2 incorpora también creación y edición de árboles como nuevas versiones desde React, con revisión obligatoria y guardado a través del núcleo Python. Los borradores de árboles aún no se autoguardan.

Los árboles pueden vincularse a expedientes con referencia histórica (ID, título, revisión) dentro de su payload JSON. GET /api/sequential?workflow_id=ID filtra antes del límite de 30 registros. La asociación se valida en Python y conserva la compatibilidad con árboles independientes. No constituye un informe ejecutivo unificado ni una derivación automática desde la matriz.

La fase 2 integra agentes, comparaciones e incentivos con expedientes en React. POST /api/laboratories recupera la matriz desde una versión calculada y conserva su referencia; GET /api/laboratories filtra por módulo y expediente. Ver LABORATORIOS-REACT-VERIFICACION.md. El informe ejecutivo unificado sigue pendiente en fase 6.

La sensibilidad Monte Carlo de árboles ya se configura, guarda y consulta desde React. Sus primeras 20 muestras alimentan el mismo diagrama interactivo con pagos y rutas conservadas por Python. Ver MONTE-CARLO-REACT-VERIFICACION.md; fase 2 en curso e informe unificado pendiente en fase 6.

La reproducción de agentes permite recorrer automáticamente rondas conservadas, con pausa, velocidad y navegación por teclado. Ver REPRODUCCION-AGENTES-REACT.md. Fase 2 en curso.

React incorpora consulta de la red global guardada, búsqueda, filtros y detalle de entidades y vínculos. Todavía sin edición, versiones ni asociación a expedientes. Ver REDES-REACT-VERIFICACION.md.

Las redes ahora se conservan como versiones con expediente opcional y contexto histórico (ID, título, revisión). El editor global previo no se modifica; sus cambios no alteran las copias guardadas. Ver VERSIONES-REDES-REACT.md.

El editor React de redes crea borradores o copias, edita entidades y relaciones con vista previa y guarda otra versión. Ver EDITOR-REDES-REACT.md. Fase 2 en curso.
