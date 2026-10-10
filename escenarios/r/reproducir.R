# Reproduce pronósticos desde modelos guardados, sin entrenamiento ni selección nueva.
stopifnot(requireNamespace('jsonlite',quietly=TRUE))
m <- readRDS('evaluacion-final/modelos.rds')
d <- read.csv('datos.csv',stringsAsFactors=FALSE)
fecha <- function(x) as.POSIXct(x,format='%Y-%m-%dT%H:%M:%SZ',tz='UTC')
test <- d[fecha(d$disponible)>m$cortes[2],]
guardados <- read.csv('evaluacion-final/pronosticos.csv',stringsAsFactors=FALSE)
stopifnot(identical(test$unidad,guardados$unidad))
if(m$elegido=='referencia') p <- rep(m$referencia,nrow(test))
if(m$elegido=='logistica') p <- predict(m$modelos$logistica,test,type='response')
if(m$elegido=='red') p <- pmin(1,pmax(0,predict(m$modelos$red,test)))
if(m$elegido=='profunda') {
 a <- readRDS('evaluacion-final/normalizacion.rds')
 modelo <- keras3::load_model('evaluacion-final/red-profunda.keras')
 x <- sweep(sweep(as.matrix(test[a$variables]),2,a$centro),2,a$escala,'/')
 p <- as.numeric(predict(modelo,x,verbose=0))
}
stopifnot(max(abs(p-guardados$pronostico))<1e-7)
# También comprobar que el modelo profundo conservado reproduce la validación.
if(file.exists('evaluacion-final/red-profunda.keras')) {
 a <- readRDS('evaluacion-final/normalizacion.rds');modelo <- keras3::load_model('evaluacion-final/red-profunda.keras')
 val <- d[fecha(d$disponible)>m$cortes[1]&fecha(d$observado)<=m$cortes[2],]
 v <- read.csv('evaluacion-final/pronosticos-validacion.csv')
 x <- sweep(sweep(as.matrix(val[a$variables]),2,a$centro),2,a$escala,'/')
 stopifnot(max(abs(as.numeric(predict(modelo,x,verbose=0))-v$profunda))<1e-7)
}
jsonlite::write_json(list(reproducido=TRUE,entrenamiento_nuevo=FALSE,tolerancia=1e-7,unidades=nrow(test)), 'evaluacion-final/reproduccion-modelo.json',auto_unbox=TRUE,pretty=TRUE)
