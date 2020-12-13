library(rJava)
library(jsonlite)

.jinit()

.jaddClassPath("C:/Users/grego/Documents/h2o_prod/strabel-app/target/strabel-app-1.0-SNAPSHOT-jar-with-dependencies.jar")

.jclassPath()

#.jaddClassPath("C:/Users/grego/Documents/h2o_prod/strabel-app/")

whatever <- .jnew("com.strabel.app.MojoScoring")

whatever$createInput('{"sepal_length":5.8,"sepal_width":3,"petal_length":4.35,"petal_width":1.3}')

prediction <- whatever$predict('{"sepal_length":5.8,"sepal_width":3,"petal_length":4.35,"petal_width":1.3}')

fromJSON(prediction)
