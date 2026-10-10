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
 pdf('resultados/red-estrategias.pdf');plot(g,vertex.color='#e5edf6',vertex.label.color='#19365a',edge.arrow.size=.3);dev.off()
 igraph::write_graph(g,'resultados/red.graphml',format='graphml')
}
if(requireNamespace('simmer',quietly=TRUE)) {
 # Ejemplo sintético independiente: cola de atención. No representa EDESUR.
 library(simmer)
 ruta <- trajectory('Atención sintética') |> seize('puesto',1) |> timeout(function() rexp(1,1/5)) |> release('puesto',1)
 entorno <- simmer('Ejemplo sintético') |> add_resource('puesto',1) |> add_generator('solicitud',ruta,function() rexp(1,1/8)) |> run(until=480)
 write.csv(get_mon_arrivals(entorno),'resultados/eventos-sinteticos.csv',row.names=FALSE)
}
if(file.exists('transacciones.csv')&&requireNamespace('arules',quietly=TRUE)) {
 # Columnas binarias de presencia de eventos, sin identificadores personales.
 d <- read.csv('transacciones.csv');stopifnot(all(vapply(d,function(x) all(x %in% c(0,1)),logical(1))))
 t <- as(as.matrix(d)==1,'transactions')
 reglas <- arules::apriori(t,parameter=list(supp=.1,conf=.8,minlen=2,maxlen=3))
 write.csv(as(reglas,'data.frame'),'resultados/asociaciones.csv',row.names=FALSE)
}
writeLines(capture.output(sessionInfo()),'resultados/entorno-exploracion.txt')
