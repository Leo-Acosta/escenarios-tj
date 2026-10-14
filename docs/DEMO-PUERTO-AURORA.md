# Puerto Aurora · demostración ficticia

Caso completamente sintético, separado de EDESUR. Un municipio y un operador comparan inversión coordinada y postergación para proteger un hospital y un puerto. Horizonte hipotético 90 días; pagos cardinales declarados en escalas propias, sin conversión a dinero ni evidencia real.

## Recorrido

1. Centro de análisis: seleccionar el expediente Puerto Aurora y versión 1. Vectores, filtro de equilibrios y sensibilidad. Umbral del municipio q=50%: por debajo prefiere postergar; por encima cofinanciar. Este umbral deriva exclusivamente de la matriz ficticia.
2. Laboratorio de árboles: elegir Escenario base, Acuerdo protegido o Crisis de costos. Cada árbol tiene cuatro resultados terminales, rutas de equilibrio y 2500 repeticiones Monte Carlo (semilla 20261014, radio 3). Cambiar muestra actualiza pagos y rutas; zoom y detalle de nodos disponibles.
3. Laboratorios del expediente: agentes con memoria, 60 rondas y error de ejecución 12%. Reproducir decisiones, cambiar actor y recorrer rondas. Comparación de seis políticas: 36 combinaciones, ocho semillas comunes y 60 rondas por combinación. Consultar dispersión y cada repetición. Sensibilidad de incentivo entre -6 y 12.
4. Red de relaciones: seleccionar Aurora · mapa analítico ficticio en Red a consultar. 18 nodos, 26 vínculos con fundamentos sintéticos. Filtrar cooperación deja tres vínculos; seleccionar nodos/relaciones muestra detalle. No hay causalidad validada ni transferencia automática de la red a la matriz.
5. Observatorio científico R: ejecutar Gráficos y exploración de supuestos con revisión explícita. En la demostración local se ejecutó y terminó correctamente; gráficos conservados, sensibilidad 3D, exportación y resumen imprimible disponibles.
6. Informe ejecutivo: consultar la versión conservada con matriz, agentes, comparación, sensibilidad y los tres árboles/Monte Carlo. El informe inicial se congeló antes de la ejecución R: para incluir resultados científicos posteriores crear otro informe revisado.

## Reproducción

Desde la raíz del repositorio, con las dependencias instaladas:

```powershell
python -m scripts.demo_aurora data/demo-aurora-nueva.sqlite3
python -m escenarios.server --database data/demo-aurora-nueva.sqlite3 --port 8778
```

El generador rechaza bases existentes. Verifica repetición exacta de agentes, comparación y Monte Carlo, y reproducción del informe sin inferencia. Los identificadores y fechas cambian al crear otro expediente; los resultados deterministas conservan sus semillas/configuraciones. No ejecuta Ollama ni crea resultados observados artificialmente atribuidos a un caso real.

Se comprobó la navegación React, el cambio de muestra, filtros de red, reproducción de rondas y la presencia del widget 3D en el navegador integrado. La captura de pantalla integrada falló; no se declara revisión visual por captura ni rotación 3D nuevamente verificada en este recorrido. Gráfico PNG R exportado e inspeccionado.

## Evaluación de capacidad

La aplicación resuelve modelos acotados, compara políticas, explora incertidumbre de pagos y conserva resultados. La matriz es 2×2 y el árbol tiene dos etapas/dos actores; los otros nodos de la red no son agentes decisores. Los agentes de esta demostración son políticas Python, no LLM. Frecuencias Monte Carlo bajo distribuciones hipotéticas no son probabilidades reales de éxito. Esta demostración permite evaluar funcionamiento e interacción, sin acreditar predicción de crisis energéticas ni mejora empírica.
