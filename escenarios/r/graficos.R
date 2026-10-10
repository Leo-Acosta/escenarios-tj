# Ejecutar desde la carpeta extraída: Rscript graficos.R
stopifnot(requireNamespace('ggplot2', quietly=TRUE))
library(ggplot2)
set.seed(42)
dir.create('resultados', showWarnings=FALSE)
pagos <- read.csv('pagos.csv', fileEncoding='UTF-8', check.names=FALSE)
sensibilidad <- read.csv('sensibilidad.csv', fileEncoding='UTF-8')
rondas <- read.csv('rondas.csv', fileEncoding='UTF-8')
theme_set(theme_minimal(base_size=12) + theme(panel.grid.minor=element_blank(), plot.title=element_text(face='bold',colour='#19365a'), legend.position='bottom'))
colores <- c('#19365a','#a16428','#397e9c','#686e89')
guardar <- function(nombre, grafico) {
  ggsave(paste0('resultados/',nombre,'.pdf'),grafico,width=10,height=6)
  ggsave(paste0('resultados/',nombre,'.png'),grafico,width=10,height=6,dpi=300)
}
guardar('espacio_resultados', ggplot(pagos,aes(pago_a,pago_b,colour=resultado)) + geom_point(size=4) + geom_text(aes(label=resultado),vjust=-1,show.legend=FALSE) + scale_colour_manual(values=colores) + labs(title='Espacio de resultados estratégicos',subtitle='Pagos declarados; cada eje conserva la unidad de su actor',x=pagos$actor_a[1],y=pagos$actor_b[1],colour='Resultado'))
guardar('sensibilidad',ggplot(sensibilidad,aes(q,utilidad,colour=estrategia,linetype=estrategia)) + geom_line(linewidth=1) + scale_colour_manual(values=colores) + labs(title='Sensibilidad de las estrategias de A',subtitle='q es un supuesto exploratorio, no una probabilidad estimada',x='Probabilidad supuesta de primera estrategia de B',y='Utilidad de A',colour='Estrategia',linetype='Estrategia'))
# geom_col conserva valores, mientras geom_bar cuenta observaciones.
guardar('pagos',ggplot(pagos,aes(resultado,pago_a,fill=estrategia_a))+geom_col()+scale_fill_manual(values=colores)+labs(title='Pagos de A por resultado',x='Resultado',y='Pago de A',fill='Estrategia de A'))
if(requireNamespace('plotly',quietly=TRUE)&&requireNamespace('htmlwidgets',quietly=TRUE)) {
 # Tres variables con significado: q y las utilidades de ambas estrategias de A.
 estrategias <- unique(sensibilidad$estrategia)
 u1 <- sensibilidad[sensibilidad$estrategia==estrategias[1],]
 u2 <- sensibilidad[sensibilidad$estrategia==estrategias[2],]
 vista <- plotly::plot_ly(x=u1$q,y=u1$utilidad,z=u2$utilidad,type='scatter3d',mode='lines',line=list(color='#19365a',width=5))
 vista <- plotly::layout(vista,title='Sensibilidad conjunta · supuestos',scene=list(xaxis=list(title='q supuesto'),yaxis=list(title=estrategias[1]),zaxis=list(title=estrategias[2])))
 htmlwidgets::saveWidget(vista,'resultados/sensibilidad-3d.html',selfcontained=FALSE)
}
if(nrow(rondas)>0) {
 guardar('distribuciones',ggplot(rondas,aes(politica,pago,fill=politica))+geom_boxplot()+facet_wrap(~actor,scales='free_y')+scale_fill_manual(values=rep(colores,length.out=length(unique(rondas$politica))))+labs(title='Distribución de pagos por política',subtitle='Rondas dependientes dentro de cada corrida; no prueba estadística de superioridad',x='Política',y='Pago',fill='Política'))
 guardar('trayectorias',ggplot(rondas,aes(ronda,pago,group=interaction(corrida,actor),colour=politica))+geom_line(alpha=.7)+facet_wrap(~actor,scales='free_y')+labs(title='Trayectorias de pagos',x='Ronda',y='Pago',colour='Política'))
}
writeLines(capture.output(sessionInfo()),'resultados/entorno-R.txt')
