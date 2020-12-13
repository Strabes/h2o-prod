Build the App with Maven
========================

The final step is to build our Java application with Maven. We need Maven to construct a single `.jar` file that contains our Java classes, the MOJO and all dependencies. Our `pom` file provides all the direction Maven needs to do this. Simply navigate to the directory containing the `pom` file and run the command:

```mvn clean compile assembly:single```

This command will produce a subdirectory `target/` in `lendingclub-app/`. `target/` will have several subdirectories itself, but more importantly it should contain a `.jar` file named something similar to `lendingclub-app-1.0-SNAPSHOT-jar-with-dependencies.jar`. This `.jar` file is what we will use for scoring.