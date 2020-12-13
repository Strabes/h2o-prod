Productionalizing H2O Models: Real-time Scoring
===============================================

This book provides a brief overview of the process of deploying an H2O model into a production application.

H2O is an open-source platform for building machine learning models and training them in a distributed environment. H2O is written in Java, with APIs for Python and R.

Although H2O models can score new observations both in a user-initialized H2O session itself and outside of a user-initialized H2O session using methods provided by the Python and/or R APIs, neither of these approaches is optimal for real-time scoring in production applications. The first approach depends on maintaining a running H2O session which is unlikely to be stable enough to meet production application SLAs. As far as I can tell, the second approach requires reloading the model into a new JVM for each scoring request which, for larger models, entails significant overhead that is unlikely to meet response-time SLAs for a production application.

The approach outlined in this book involves initializing a single JVM, instantiating a single scoring object, which loads the H2O model at instantiation and provides a simple method for parsing and scoring data from a JSON string.

## Outline

There are several steps involved in the process discussed above:

1. Install Apache Maven, a build automation tool for Java that will build our Java package and manage dependencies. Initialize a `maven` project for handling java dependencies and building artifacts.
2. Update the `maven` pom file to include dependencies from Maven central.
3. Fit a model using `h2o` and download the MOJO as zip file and the associated h2o-genmodel jar file.
4. Write one or more java classes to score using the MOJO. For deploying the model using R and `rJava`, a single class will do. For deploying the model using Python and `py4j` we will write a second java class that acts as a java gateway entry point for the JVM.
5. Use maven to build a single `.jar` file with all dependencies from maven central.
6. Score your model through a standalone JVM.
