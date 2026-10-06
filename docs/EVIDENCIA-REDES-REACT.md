# Evidencia por vínculo en redes

Cada relación puede registrar una fuente (160 caracteres), referencia (500) y nota de respaldo (1200). La evidencia es opcional; al agregarla los tres campos son obligatorios. Python valida y conserva estos campos dentro de cada vínculo del payload de la versión, sin migrar registros anteriores. El editor permite agregar, modificar y quitar evidencia en el borrador; cualquier cambio invalida la revisión.

La consulta del mapa muestra fuente, referencia y nota al seleccionar una relación. Los vínculos sin evidencia se identifican como hipótesis. Las referencias se presentan como texto, sin abrir ni verificar documentos automáticamente. No se incorporan adjuntos, probabilidades ni afirmaciones de causalidad validada.

La copia editable clona la evidencia para no modificar el origen. La eliminación de entidades remapea vínculos con su evidencia; quitar un vínculo elimina su evidencia del borrador. El guardado crea otra versión, manteniendo versiones previas. El límite del cuerpo HTTP continúa en 100000 bytes; redes con texto extenso pueden excederlo.

Validación: 32 pruebas frontend; 107 pruebas Python; compilación TypeScript/Vite aprobada. Pruebas nuevas cubren evidencia completa/parcial, límites, copia independiente y persistencia de versiones originales. Navegador con base aislada qa-network-react.sqlite3, puerto 8768: copia de 27b7533d-7c1e-4561-bcf2-3b7fc5509d73, evidencia de Cooperación entre Municipio y Vecinos organizados, guardada como 450d8165-15d1-44fe-b1c3-551217e0c470. El detalle muestra Acta de prueba del analista, Documento QA · folio 12 y la nota. Lectura de SQLite confirma que el origen sigue sin evidencia. Sin escrituras de prueba en la base principal.

Fase 2 en curso, avance de trazabilidad documental para fase 3. Pendiente integración de IA local. Informe ejecutivo unificado: fase 6.
