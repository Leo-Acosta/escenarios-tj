# Edición de redes en React

Desde Red de relaciones se puede crear una red o editar una copia del mapa global o una versión conservada. El borrador muestra una vista previa interactiva; permite nombrar y tipificar entidades, agregar o quitar vínculos y registrar título/fundamento. El guardado usa POST /api/graph/versions y crea otra versión con el expediente actualmente seleccionado, o independiente si se eligió la opción global.

Eliminar una entidad del borrador retira sus vínculos y remapea identificadores. La última entidad no puede quitarse; límites: 200 entidades y 1000 vínculos. El editor evita relaciones duplicadas del mismo tipo entre el mismo par, incluso invertidas. No se atribuye dirección causal a un vínculo. La revisión se invalida con cualquier cambio del modelo. Campos pendientes para agregar un vínculo no afectan el modelo hasta pulsar Agregar relación.

El borrador no se autoguarda. Cambiar expediente, versión o sección requiere descartar cambios explícitamente. Cancelar vuelve a la red consultada. Los errores de guardado conservan campos; el mapa global y las versiones anteriores permanecen intactos. El guardado no conserva posiciones manuales ni agrega evidencia por vínculo.

Validación: 30 pruebas frontend y compilación TypeScript/Vite aprobadas. Cuatro pruebas nuevas cubren eliminación con remapeo, copia independiente, duplicados/autovínculos/referencias y revisión/fundamento. Navegador en puerto 8768, base aislada qa-network-react.sqlite3: copiar b43af485-8322-4654-a4cb-f6a15ce9e4a4, renombrar Vecinos, agregar Comité de control y vínculo Influencia, revisar, modificar nombre e invalidar revisión, guardar 27b7533d-7c1e-4561-bcf2-3b7fc5509d73. Consulta muestra 4 entidades y 3 vínculos. Quitar Vecinos del siguiente borrador deja 3 entidades y cero relaciones; cancelar recupera la versión completa. Lectura de SQLite confirma versión original y red global intactas. No se escribieron pruebas en la base principal. No hubo cambios de backend en este incremento.

Fase 2 en curso. Pendientes: evidencia por relación e integración de IA local. Informe ejecutivo unificado: fase 6.
