# Optimización acotada sobre utilidad de A. No suma pagos de unidades diferentes.
set.seed(42)
dir.create('resultados',showWarnings=FALSE)
s <- read.csv('sensibilidad.csv')
objetivo <- function(q) -max(s$utilidad[abs(s$q-q)==min(abs(s$q-q))])
grid <- seq(0,1,.01)
valores <- vapply(grid,objetivo,numeric(1))
# Comparación exhaustiva en el dominio discreto declarado, no óptimo universal.
write.csv(data.frame(q=grid,objetivo=valores),'resultados/busqueda-acotada.csv',row.names=FALSE)
recocido <- optim(.5,objetivo,gr=function(q) sample(grid,1),method='SANN',control=list(maxit=1000,temp=1))
saveRDS(list(recocido=recocido,mejor_grilla=grid[which.min(valores)],semilla=42),'resultados/optimizacion.rds')
writeLines('q es un supuesto sobre el rival, no una acción controlable. La búsqueda identifica escenarios favorables, no recomienda imponer esa probabilidad.','resultados/limites-optimizacion.txt')
# Relaciones de estrategias observadas en simulaciones; no vínculos causales reales.
if(requireNamespace('igraph',quietly=TRUE)) {
 p <- read.csv('pagos.csv')
 g <- igraph::graph_from_data_frame(data.frame(from=paste0('A: ',p$estrategia_a),to=paste0('B: ',p$estrategia_b)),directed=TRUE)
 nodos <- data.frame(nombre=igraph::V(g)$name)
 nodos$x <- ifelse(startsWith(nodos$nombre,'B:'),1,0)
 nodos$y <- ave(seq_len(nrow(nodos)),nodos$x,FUN=seq_along)
 enlaces <- igraph::as_data_frame(g,what='edges')
 enlaces$x <- .15;enlaces$fin_x <- .85
 enlaces$y <- nodos$y[match(enlaces$from,nodos$nombre)];enlaces$fin_y <- nodos$y[match(enlaces$to,nodos$nombre)]
 red <- ggplot2::ggplot()+ggplot2::geom_segment(data=enlaces,ggplot2::aes(x,y,xend=fin_x,yend=fin_y),colour='#a0b4ce',linewidth=.8,arrow=grid::arrow(length=grid::unit(.15,'inches')))+ggplot2::geom_label(data=nodos,ggplot2::aes(x,y,label=nombre),fill='#edf2f9',colour='#19365a',size=5,label.padding=grid::unit(.5,'lines'))+ggplot2::scale_x_continuous(limits=c(-.3,1.3))+ggplot2::scale_y_continuous(limits=c(.4,2.6))+ggplot2::labs(title='Relaciones entre estrategias · modelo declarado',subtitle='Alternativas de A y B; conexiones de la matriz, no causalidad empírica')+ggplot2::theme_void(base_size=12)+ggplot2::theme(plot.title=ggplot2::element_text(face='bold',colour='#19365a'),plot.margin=ggplot2::margin(20,20,20,20))
 ggplot2::ggsave('resultados/red-estrategias.pdf',red,width=10,height=6);ggplot2::ggsave('resultados/red-estrategias.png',red,width=10,height=6,dpi=300)
 igraph::write_graph(g,'resultados/red.graphml',format='graphml')
}
if(requireNamespace('simmer',quietly=TRUE)) {
 # Ejemplo sintético independiente: cola de atención. No representa EDESUR.
 library(simmer)
 ruta <- trajectory('Atención sintética') |> seize('puesto',1) |> timeout(function() rexp(1,1/5)) |> release('puesto',1)
 entorno <- simmer('Ejemplo sintético') |> add_resource('puesto',1) |> add_generator('solicitud',ruta,function() rexp(1,1/8)) |> run(until=480)
 write.csv(get_mon_arrivals(entorno),'resultados/eventos-sinteticos.csv',row.names=FALSE)
 if(requireNamespace('ggplot2',quietly=TRUE)) {
  datos <- get_mon_arrivals(entorno)
  g <- ggplot2::ggplot(datos,ggplot2::aes(start_time,end_time-start_time))+ggplot2::geom_point(colour='#19365a')+ggplot2::labs(title='Atención por eventos · ejemplo sintético',subtitle='Cola ilustrativa, no representa EDESUR',x='Tiempo de llegada (minutos)',y='Tiempo total en sistema (minutos)')+ggplot2::theme_minimal(base_size=12)
  ggplot2::ggsave('resultados/eventos.png',g,width=10,height=6,dpi=300);ggplot2::ggsave('resultados/eventos.pdf',g,width=10,height=6)
 }
}
if(file.exists('transacciones.csv')&&requireNamespace('arules',quietly=TRUE)) {
 # Columnas binarias de presencia de eventos, sin identificadores personales.
 d <- read.csv('transacciones.csv');stopifnot(all(vapply(d,function(x) all(x %in% c(0,1)),logical(1))))
 t <- as(as.matrix(d)==1,'transactions')
 reglas <- arules::apriori(t,parameter=list(supp=.1,conf=.8,minlen=2,maxlen=3))
 write.csv(as(reglas,'data.frame'),'resultados/asociaciones.csv',row.names=FALSE)
}
writeLines(capture.output(sessionInfo()),'resultados/entorno-exploracion.txt')
