# Datos externos revisados: Rscript aprendizaje.R datos.csv fin_desarrollo fin_validacion
# Columnas: unidad, disponible, observado, resultado (0/1), x1 [x2...]. Fechas ISO UTC.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=3) stop('Se requieren datos reales o sintéticos identificados y dos cortes temporales ISO.')
d <- read.csv(args[1], stringsAsFactors=FALSE)
stopifnot(all(c('unidad','disponible','observado','resultado') %in% names(d)),!anyDuplicated(d$unidad),all(d$resultado %in% c(0,1)))
fecha <- function(x) {
 stopifnot(all(grepl('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$',x)))
 as.POSIXct(x,format='%Y-%m-%dT%H:%M:%SZ',tz='UTC')
}
d$disponible <- fecha(d$disponible);d$observado <- fecha(d$observado)
cortes <- fecha(args[2:3]);stopifnot(!anyNA(d),!anyNA(cortes),cortes[1]<cortes[2],all(d$disponible<d$observado))
xs <- grep('^x[0-9]+$',names(d),value=TRUE)
stopifnot(length(xs)>0,all(vapply(d[xs],is.numeric,logical(1))))
stopifnot(all(is.finite(as.matrix(d[xs]))))
dev <- d[d$observado<=cortes[1],];val <- d[d$disponible>cortes[1]&d$observado<=cortes[2],];test <- d[d$disponible>cortes[2],]
stopifnot(nrow(dev)>=30,nrow(val)>=30,nrow(test)>=30,length(unique(dev$resultado))==2)
if(nrow(dev)+nrow(val)+nrow(test)!=nrow(d)) stop('Hay unidades que cruzan cortes temporales; no se omiten silenciosamente.')
# Sin normalización sobre validación/prueba; selección solo con validación.
set.seed(42)
formula <- reformulate(xs,response='resultado')
modelo <- glm(formula,data=dev,family=binomial())
referencia <- mean(dev$resultado)
pred_val <- list(referencia=rep(referencia,nrow(val)),logistica=predict(modelo,val,type='response'))
modelos <- list(logistica=modelo)
if(requireNamespace('caret',quietly=TRUE)&&requireNamespace('nnet',quietly=TRUE)) {
 red <- caret::train(formula,data=dev,method='nnet',trControl=caret::trainControl(method='none'),tuneGrid=data.frame(size=4,decay=.1),preProcess=c('center','scale'),linout=TRUE,trace=FALSE,maxit=200)
 pred_val$red <- pmin(1,pmax(0,predict(red,val)));modelos$red <- red
}
if(Sys.getenv('ESCENARIOS_KERAS')=='1') {
 stopifnot(requireNamespace('keras3',quietly=TRUE))
 keras3::set_random_seed(42)
 reticulate::py_run_string('import torch; torch.set_num_threads(1); torch.use_deterministic_algorithms(True)')
 centro <- vapply(dev[xs],mean,numeric(1));escala <- vapply(dev[xs],sd,numeric(1));escala[escala==0]<-1
 transformar <- function(d) sweep(sweep(as.matrix(d[xs]),2,centro),2,escala,'/')
 red_profunda <- keras3::keras_model_sequential(input_shape=c(length(xs))) |>
  keras3::layer_dense(units=16,activation='relu') |>
  keras3::layer_dense(units=8,activation='relu') |>
  keras3::layer_dense(units=1,activation='sigmoid')
 red_profunda |> keras3::compile(optimizer='adam',loss='binary_crossentropy')
 red_profunda |> keras3::fit(transformar(dev),dev$resultado,epochs=50,batch_size=16,shuffle=FALSE,verbose=0)
 pred_val$profunda <- as.numeric(predict(red_profunda,transformar(val),verbose=0))
}
brier <- function(p,y) mean((p-y)^2)
puntajes <- vapply(pred_val,brier,numeric(1),y=val$resultado)
elegido <- names(which.min(puntajes))
# Apertura final única por carpeta; no sobrescribe resultados finales.
if(dir.exists('evaluacion-final')) stop('Evaluación final ya conservada. Usá una carpeta nueva para otro protocolo.')
dir.create('evaluacion-final')
p <- if(elegido=='referencia') rep(referencia,nrow(test)) else if(elegido=='logistica') predict(modelo,test,type='response') else if(elegido=='profunda') as.numeric(predict(red_profunda,transformar(test),verbose=0)) else pmin(1,pmax(0,predict(modelos$red,test)))
stopifnot(all(is.finite(p)))
saveRDS(list(modelos=modelos,referencia=referencia,elegido=elegido,cortes=cortes,semilla=42),'evaluacion-final/modelos.rds')
if(exists('red_profunda')) {
 keras3::save_model(red_profunda,'evaluacion-final/red-profunda.keras')
 saveRDS(list(centro=centro,escala=escala,variables=xs),'evaluacion-final/normalizacion.rds')
 reticulate::py_run_string("import keras, torch, sys; open('evaluacion-final/entorno-python.txt','w').write('Python: '+sys.version+'\\nKeras: '+keras.__version__+'\\nTorch: '+torch.__version__)")
}
write.csv(data.frame(unidad=test$unidad,resultado=test$resultado,pronostico=p,referencia=referencia),'evaluacion-final/pronosticos.csv',row.names=FALSE)
write.csv(data.frame(metodo=names(puntajes),brier_validacion=puntajes),'evaluacion-final/validacion.csv',row.names=FALSE)
write.csv(data.frame(unidad=val$unidad,resultado=val$resultado,as.data.frame(pred_val)),'evaluacion-final/pronosticos-validacion.csv',row.names=FALSE)
if(requireNamespace('ggplot2',quietly=TRUE)) {
 library(ggplot2)
 v <- data.frame(metodo=names(puntajes),brier=as.numeric(puntajes))
 etiquetas <- c(referencia='Referencia',logistica='Regresión logística',red='Red pequeña',profunda='Red profunda')
 v$metodo <- unname(etiquetas[v$metodo])
 g <- ggplot(v,aes(reorder(metodo,brier),brier,fill=metodo))+geom_col(show.legend=FALSE)+scale_fill_manual(values=c('#19365a','#397e9c','#a16428','#686e89'))+labs(title='Comparación de modelos · validación',subtitle='Menor Brier es mejor; selección antes de abrir prueba',x='Método',y='Error Brier')+theme_minimal(base_size=12)
 ggsave('evaluacion-final/validacion.png',g,width=10,height=6,dpi=300);ggsave('evaluacion-final/validacion.pdf',g,width=10,height=6)
 g <- ggplot(data.frame(p=p,y=test$resultado),aes(p,y))+geom_point(alpha=.35,colour='#19365a',position=position_jitter(height=.03,width=0,seed=42))+labs(title='Pronósticos y resultados · prueba reservada',subtitle=paste('Modelo seleccionado:',etiquetas[elegido]),x='Probabilidad pronosticada',y='Resultado observado binario')+theme_minimal(base_size=12)
 ggsave('evaluacion-final/pronosticos.png',g,width=10,height=6,dpi=300);ggsave('evaluacion-final/pronosticos.pdf',g,width=10,height=6)
}
writeLines(c(paste('Método:',elegido),paste('Brier prueba:',brier(p,test$resultado)),paste('Brier referencia:',brier(rep(referencia,nrow(test)),test$resultado)),'No garantiza superioridad futura; revisión e incorporación al protocolo Python requeridas.'),'evaluacion-final/resumen.txt')
writeLines(capture.output(sessionInfo()),'evaluacion-final/entorno-R.txt')
