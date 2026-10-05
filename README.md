# Escenarios TJ

Proyecto para construir un laboratorio de escenarios multiagente en Python, con interfaz y documentación en español y almacenamiento local.

Estado: versión 0.1 local implementada. Incluye mesa de análisis interactiva, dos actores seleccionables, matriz, equilibrios puros, árbol de consecuencias, tres escenarios, historial SQLite y vista ejecutiva imprimible.

## Ejecutar

Python 3.11 o superior. La aplicación base usa la biblioteca estándar:

```powershell
python -m escenarios.server
```

Abrir http://127.0.0.1:8765. El servidor escucha sólo en el equipo local.

Para descargar PDF vectorial, instalar la dependencia opcional:

```powershell
python -m pip install "reportlab>=4.0,<5"
python -m escenarios.report
```

La impresión del navegador funciona sin ReportLab. Muestra incluida: `output/pdf/informe-ejecutivo-demo.pdf`.

Pruebas:

```powershell
python -m unittest discover -s tests -v
```

Los datos son ilustrativos. No es todavía un motor multiagente autónomo ni un sistema de predicción calibrado. La licencia de distribución del código propio queda pendiente de elección.

- [Auditoría del repositorio de referencia](docs/AUDITORIA_MIRO_FISH.md)
- [Diseño propuesto y etapas de implementación](docs/ARQUITECTURA.md)

La copia original se conserva en `reference/Miro-Fish`, excluida del control de versiones. No se ejecutó su código ni se instalaron sus dependencias. Se conserva intacta con su licencia y atribuciones. No se incorporaron sus implementaciones, prompts ni imágenes a la aplicación propia.

### Casos propios sin IA
La mesa permite definir un juego simultáneo 2×2 con nombres, estrategias, ocho pagos y probabilidades supuestas. Calcula utilidades esperadas, mejores respuestas de A, equilibrios puros y un equilibrio mixto interior aislado, si existe. Compara tres supuestos de conducta de B y guarda versiones en SQLite. No interpreta automáticamente el texto del chat ni calibra pronósticos. Los casos propios alimentan un árbol de consecuencias interactivo, vectores de utilidad y un informe ejecutivo imprimible. El informe propio se exporta con Imprimir → Guardar como PDF del navegador; la descarga directa de PDF sigue disponible para el ejemplo institucional.
