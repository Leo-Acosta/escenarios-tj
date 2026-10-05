# Verificación de versión 0.1

Fecha: 5 de octubre de 2026.

- Núcleo: valores conocidos, transición de equilibrio, empate, extremos y entradas no finitas.
- SQLite: creación y lectura desde conexiones distintas. Detectó conexiones sin cerrar que bloqueaban el archivo en Windows; corregido con cierre explícito.
- JavaScript: comprobación de sintaxis con Node.
- API: parámetros no finitos rechazados, Host no permitido bloqueado, rutas fuera de la lista cerrada devuelven 404 y escrituras desde otros orígenes devuelven 403. El servidor recalcula antes de guardar; no acepta una recomendación inventada enviada por el cliente. Seis pruebas automáticas pasaron.
- PDF: dos páginas A4 renderizadas con Poppler e inspeccionadas visualmente; tablas, árbol, red y barras sin recortes.

- Navegador: pasar costo de 3 a 1 cambia la alternativa a competir y sus utilidades de 1 a 3; guardado de instantánea #1, recuperación del historial y apertura del informe con parámetros consistentes. Selección del actor B actualiza su descripción. No se observó desbordamiento de los paneles en la medición DOM de escritorio.
- La captura visual de la interfaz mediante la herramienta de navegador no estuvo disponible; la revisión de esa pantalla se limita al DOM, interacción y mediciones de composición. El PDF sí fue inspeccionado visualmente.

Ningún caso histórico ha sido utilizado: estas pruebas no demuestran precisión predictiva.

## Panel gráfico interactivo

Verificado en navegador: selección directa de vector y nodo, selección por Enter, zoom 125 %, restablecimiento 100 %, plegado y expansión de rama (dos/cuatro hojas visibles). Selección sincronizada entre árbol, plano y lectura de pagos. Sin desbordamiento medido en los paneles de escritorio. Exportación SVG conserva el encuadre completo del árbol aunque se amplíe en pantalla. El plano usa igual escala por unidad en ambos ejes. Captura visual automatizada sigue sin estar disponible.
