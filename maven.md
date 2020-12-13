Apache Maven
============

Apache Maven is a build automation tool for Java applications. If you do not already have maven installed on your machine, you can download it [here](https://maven.apache.org/download.cgi).

The first step in our project is to create a new, empty directory for our maven build. Having created this directory, open a terminal and `cd` into it.

To initialize a new maven project, you will need:

1. A `DgroupId`, which will serve as your package name. Since I will be building a model on the Lending Club data, I'll choose `com.lendingclub.app`. If you work for `somecompany`, you will likely choose `com.somecompany.app`.
2. A `DartifactId` - this is the root directory of your app. I'll choose `lendingclub-app`.

Now I'll run the following maven command (from my project directory)

```
mvn -B archetype:generate -DgroupId=com.lendingclub.app -DartifactId=lendingclub-app -DarchetypeArtifactId=maven-archetype-quickstart -DarchetypeVersion=1.4
```

This command created the following directory and structures for me:

```
lendingclub-app
|-- pom.xml
`-- src
    |-- main
    |   `-- java
    |       `-- com
    |           `-- lendingclub
    |               `-- app
    |                   `-- App.java
    `-- test
        `-- java
            `-- com
                `-- lendingclub
                    `-- app
                        `-- AppTest.java
```

The next step is to edit the `pom` file.