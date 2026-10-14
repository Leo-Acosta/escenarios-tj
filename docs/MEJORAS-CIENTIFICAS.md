# Ampliación científica R · cierre funcional de etapas 1–2

Actualización: 10 de octubre de 2026. Estas etapas complementan la hoja de ruta;
no reinician la numeración de las fases anteriores.

## Estado

**Implementación funcional terminada y ejecutada en Windows.** R 4.6.1 instalado
localmente en `.tools/R`, paquetes en `.tools/R-library` y Keras en un entorno
aislado `.tools/keras-python`. Python mantiene matrices, restricciones y auditoría;
React/TypeScript mantiene la interfaz. No se utiliza un servicio remoto para inferir.

La evaluación empírica de la fase 8 permanece abierta: el ejemplo de aceptación
es sintético y no contiene datos EDESUR ni evidencia de precisión real.

## Etapa 1: gráficos científicos

Desde Centro de análisis → Observatorio de gráficos → Observatorio científico:

1. Seleccionar versión calculada y tipo de análisis.
2. Confirmar revisión y ejecutar el laboratorio local.
3. Consultar gráficos, abrir sensibilidad 3D, verificar reproducción o exportar.

ggplot2 genera puntos, líneas, barras de valores, boxplots y facetas por actor.
La paleta es azul marino, ocre y azul claro; leyendas y políticas están en español.
Salidas: nueve gráficos en el recorrido completo, PNG 300 dpi y PDF vectorial.
igraph construye la red de estrategias, presentada con ggplot2. Plotly genera
sensibilidad 3D de q y las dos utilidades de A; no se inventa una tercera variable.
El widget se presenta en un iframe aislado sin acceso a la red ni al origen de la
aplicación. RStudio es un IDE; Tableau y Power BI pueden importar los CSV.

Los PNG y páginas PDF se revisaron visualmente. El 13 de octubre se verificaron
renderizado y giro 3D en Chromium y Firefox, reproducción desde React y vista de
390 px sin desbordamiento. Se revisaron trece páginas A4 generadas por Chromium
y estilos de impresión Firefox. Ver [alcance y límites](CIERRE-CIENTIFICO-WINDOWS.md):
no se acredita vista previa nativa de otros navegadores, todos los GPU o impresión física.
Se conserva la salida 2D como alternativa.

## Etapa 2: modelos y análisis

Comparación entre referencia de prevalencia de desarrollo, regresión logística,
red pequeña caret/nnet y red profunda keras3 con backend PyTorch CPU. La red
pequeña usa salida numérica acotada a 0–1; no se acredita calibración real. Los
hiperparámetros están fijados en la receta, sin búsqueda sobre la prueba final.

- Desarrollo, validación y prueba separados por fechas UTC.
- Unidades únicas; mínimo 30 por partición. Se rechazan casos que cruzan cortes,
  información posterior al resultado, observaciones futuras y valores no finitos.
- Normalización aprendida solo en desarrollo. Selección por Brier de validación.
- Prueba evaluada con el candidato seleccionado y referencia explícita.
- Modelos perdedores conservados, pronósticos de validación, pronósticos de prueba,
  modelos RDS/Keras, semilla, código y versiones del entorno.
- Optimización: búsqueda exhaustiva en una grilla y recocido SANN. Optimizar q
  identifica supuestos favorables; no convierte la conducta rival en una acción
  controlable. No se modifica ningún pago.
- simmer: cola de atención sintética, sin atribuirla a EDESUR.
- arules: asociaciones de variables binarias, usando solo desarrollo; asociación
  no implica causalidad.

No se usa un supuesto paquete SBO++ sin respaldo oficial. La aplicación no
promociona modelos ni modifica automáticamente matrices o evidencia.

## Datos observados

Modo “Datos observados”: CSV hasta 1 MB / 2000 unidades con columnas `unidad`,
`disponible`, `observado`, `resultado`, `x1` y opcionales `x2`…`x20`. Fechas UTC
`AAAA-MM-DDTHH:MM:SSZ`, resultado 0/1 y características numéricas. Fuente e
independencia requieren revisión explícita. No incluir identificadores personales.

Esta integración realiza evaluación **retrospectiva**, no sustituye el protocolo
prospectivo existente. Los cortes, disponibilidad de características e independencia
son declaraciones del analista, no autenticación de evidencia. Repetir candidatos
tras conocer resultados impide considerar una prueba independiente. Para afirmar
mejora real se requiere reservar nuevas observaciones en la fase 8.

## Conservación y reproducción

Trabajos en segundo plano; una ejecución activa por base, con protección entre
procesos y recuperación de interrupciones. Solo recetas incluidas; no código R
arbitrario ni comandos suministrados por el cliente. Límite de diez minutos por
receta, archivo comprimido de 10 MB y controles del límite de respaldo SQLite.
Errores e intentos fallidos permanecen registrados. Se muestran veinte ejecuciones
recientes; no se eliminan las anteriores. Carpetas de trabajo quedan locales.

El ZIP conserva matriz/corridas congeladas, datos, scripts, modelos, gráficos y
entorno. El registro tiene huellas de integridad. La exportación puede incluir
datos aportados: revisar antes de compartir. Nada se sube automáticamente a GitHub.
El respaldo SQLite incluye los resultados, no solo rutas a archivos externos.

“Verificar reproducción” recalcula en Python Brier de validación, selección,
Brier final, mejoras/empates/pérdidas e intervalo pareado desde pronósticos
guardados, sin inferencia. `reproducir.R` recarga el modelo seleccionado y el
profundo para comparar pronósticos, sin entrenar; tolerancia 1e-7.
No se garantiza identidad entre versiones de backend o hardware diferentes.

El informe ejecutivo incorpora hasta tres laboratorios terminados de la versión
seleccionada. Conserva copias de datos/pronósticos para recalcular métricas sin
depender del laboratorio vivo. Resumen HTML A4 con gráficos y PDF ejecutivo
verificado en ocho páginas A4; los códigos técnicos permanecen en los registros.

## Evidencia de aceptación sintética

Recorrido reproducible: `python scripts/verify-scientific.py --output tmp/verificacion-nueva`.
Usar una carpeta nueva: no sobrescribe una aceptación anterior.

- 360 unidades sintéticas: 120 desarrollo, 120 validación, 120 prueba.
- Seis corridas de agentes: tres semillas y dos pares de políticas.
- Cuatro métodos entrenados/comparados, incluyendo Keras; 53 archivos conservados.
- Validación Brier: referencia 0,249444; logística 0,163259; red pequeña 0,162540;
  profunda 0,164182. Selección: red pequeña.
- Prueba: Brier 0,182973 frente a referencia 0,250833; diferencia -0,067861.
  Intervalo pareado aproximado [-0,105660; -0,025773]. 88 mejoras, 0 empates,
  32 pérdidas por unidad. Esto es un resultado sintético, no evidencia real.
- Dos ejecuciones completas reprodujeron los mismos puntajes y pronósticos.
- Recarga R de modelos conservados aprobada; reproducción Python sin inferencia
  aprobada; respaldo íntegro e informe congelado aprobados.
- Ejecución adicional de gráficos iniciada desde la interfaz: terminó correctamente.
- Pruebas automatizadas de rutas, versiones, tiempos, integridad, fallo conservado,
  recuperación entre instancias y manipulación de resúmenes.

Versiones verificadas: ggplot2 4.0.3, plotly 4.12.1, htmlwidgets 1.6.4,
igraph 2.3.3, simmer 4.4.7, arules 1.7.15, caret 7.0-1, nnet 7.3-20,
keras3 1.5.1, jsonlite 2.0.0; Keras Python 3.12.0 y PyTorch 2.14.1+cpu.

## Instalación en otra computadora

Windows: `scripts/install-scientific.ps1 -Python python` con Python 3.11–3.13.
El script descarga R desde CRAN y comprueba su huella, instala los paquetes y
crea el entorno CPU en `.tools`. Reiniciar el servidor para cargar el código nuevo.
También admite `SCENARIOS_RSCRIPT`, `R_LIBS_USER` y `RETICULATE_PYTHON` cuando no
existe el entorno local. La construcción científica admite `-IncludeScientific`
e incorpora R, paquetes CRAN y un intérprete independiente Keras/PyTorch CPU.
Ver [distribución y verificaciones](CIERRE-CIENTIFICO-WINDOWS.md). Los binarios
y datos personales permanecen excluidos de Git; Ollama no se incluye.

Fuentes: [CRAN Windows](https://cran.r-project.org/bin/windows/base/),
[ggplot2](https://ggplot2.tidyverse.org/reference/),
[optim](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/optim.html),
[simmer](https://r-simmer.org/), [keras3](https://keras3.posit.co/).
