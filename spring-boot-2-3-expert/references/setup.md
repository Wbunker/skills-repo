# Spring Boot 2.3 — Project Setup & Build

## System Requirements

- Java 8 minimum (compatible through Java 15)
- Spring Framework 5.2.13.RELEASE or above
- Maven 3.3+ or Gradle 6.3+
- Servlet containers: Tomcat 9.0, Jetty 9.4, Undertow 2.0 (Servlet 3.1+)

---

## Spring Initializr

Visit [start.spring.io](https://start.spring.io):

1. Select **Maven** or **Gradle**
2. Set **Spring Boot** version to **2.3.9** (or 2.3.x)
3. Add dependencies: Web, Spring Data JPA, H2, Spring Security, Actuator, etc.
4. Download and unzip

---

## Maven Setup

### Minimal pom.xml (inheriting from spring-boot-starter-parent)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
             https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.3.9.RELEASE</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>myapp</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>11</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <!-- NOTE: In 2.3, validation is NO LONGER bundled in web starter -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### Without parent POM (using BOM import)

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>2.3.9.RELEASE</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

You must then explicitly add the plugin with version:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <version>2.3.9.RELEASE</version>
            <executions>
                <execution>
                    <goals><goal>repackage</goal></goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

---

## Gradle Setup

### build.gradle (Groovy)

```gradle
plugins {
    id 'org.springframework.boot' version '2.3.9.RELEASE'
    id 'io.spring.dependency-management' version '1.0.11.RELEASE'
    id 'java'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '11'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'com.h2database:h2'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

// DevTools: mark as developmentOnly so it doesn't end up in fat jar
configurations {
    developmentOnly
    runtimeClasspath {
        extendsFrom developmentOnly
    }
}
dependencies {
    developmentOnly 'org.springframework.boot:spring-boot-devtools'
}
```

### build.gradle.kts (Kotlin DSL)

```kotlin
plugins {
    id("org.springframework.boot") version "2.3.9.RELEASE"
    id("io.spring.dependency-management") version "1.0.11.RELEASE"
    kotlin("jvm") version "1.3.72"
    kotlin("plugin.spring") version "1.3.72"
}

group = "com.example"
version = "0.0.1-SNAPSHOT"
java.sourceCompatibility = JavaVersion.VERSION_11

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

---

## Key Starter Dependencies

| Starter | Purpose |
|---------|---------|
| `spring-boot-starter` | Core: auto-config, logging, YAML |
| `spring-boot-starter-web` | Spring MVC + embedded Tomcat |
| `spring-boot-starter-validation` | Bean Validation (JSR-380) — **separate in 2.3** |
| `spring-boot-starter-data-jpa` | Hibernate + Spring Data JPA |
| `spring-boot-starter-data-jdbc` | Spring Data JDBC |
| `spring-boot-starter-data-r2dbc` | Reactive data access (new in 2.3 GA) |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-actuator` | Production endpoints |
| `spring-boot-starter-test` | JUnit 5, Mockito, AssertJ, MockMvc |
| `spring-boot-starter-amqp` | RabbitMQ / Spring AMQP |
| `spring-boot-starter-kafka` | Apache Kafka |
| `spring-boot-starter-cache` | Spring Cache abstraction |
| `spring-boot-starter-data-redis` | Redis + Lettuce client |
| `spring-boot-starter-thymeleaf` | Thymeleaf template engine |
| `spring-boot-starter-webflux` | Reactive web (WebFlux + WebClient) |
| `spring-boot-devtools` | Dev-time: auto-restart, LiveReload |

---

## Project Structure (Recommended)

```
src/
└── main/
    ├── java/
    │   └── com/example/myapp/
    │       ├── MyApplication.java          ← main class at ROOT of package
    │       ├── config/
    │       │   └── SecurityConfig.java
    │       ├── controller/
    │       │   └── UserController.java
    │       ├── service/
    │       │   └── UserService.java
    │       ├── repository/
    │       │   └── UserRepository.java
    │       └── domain/
    │           └── User.java
    └── resources/
        ├── application.properties          ← default config
        ├── application-dev.properties      ← dev profile config
        ├── application-prod.properties     ← prod profile config
        └── db/migration/                   ← Flyway SQL scripts
            └── V1__init.sql
└── test/
    └── java/
        └── com/example/myapp/
            └── controller/
                └── UserControllerTest.java
```

**Critical rule:** Place `MyApplication.java` in the root package (`com.example.myapp`) so `@ComponentScan`, `@EntityScan`, and `@ConfigurationPropertiesScan` all work without explicit basePackages.

---

## Main Application Class

```java
package com.example.myapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
// equivalent to: @Configuration + @EnableAutoConfiguration + @ComponentScan
public class MyApplication {

    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

### @SpringBootApplication attributes

```java
// Disable specific auto-configurations
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})

// Exclude by name (when class not on classpath)
@SpringBootApplication(excludeName = {
    "org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration"
})

// Custom component scan packages
@SpringBootApplication(scanBasePackages = {"com.example.app", "com.example.shared"})
```

---

## Running the Application

```bash
# Maven
mvn spring-boot:run

# Gradle
./gradlew bootRun

# As packaged JAR
mvn package
java -jar target/myapp-0.0.1-SNAPSHOT.jar

# With profile
java -jar target/myapp.jar --spring.profiles.active=prod

# With debug logging
java -jar target/myapp.jar --debug
```

---

## Packaging as JAR

```bash
mvn clean package
# produces: target/myapp-0.0.1-SNAPSHOT.jar (executable fat jar)
# also keeps: target/myapp-0.0.1-SNAPSHOT.jar.original (thin jar)
```

The fat JAR is self-contained — run with `java -jar` anywhere Java is installed.

---

## Packaging as WAR (for external servlet container)

```xml
<!-- pom.xml: change packaging -->
<packaging>war</packaging>

<!-- Mark embedded Tomcat as provided -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-tomcat</artifactId>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

```java
// Extend SpringBootServletInitializer for WAR deployment
@SpringBootApplication
public class MyApplication extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(MyApplication.class);
    }

    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

---

## DevTools

```xml
<!-- Maven: mark optional so it doesn't propagate to dependents -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <optional>true</optional>
</dependency>
```

DevTools provides:
- **Automatic restart** on classpath changes (keeps third-party jar classloader, reloads app classloader)
- **LiveReload** server (port 35729) — triggers browser refresh
- **Property defaults** — disables template caching, enables web debug logging
- **Remote devtools** for cloud deployments (`spring.devtools.remote.secret=mysecret`)

Disable restart:
```properties
spring.devtools.restart.enabled=false
```

Use trigger file (useful for continuous-compilation IDEs):
```properties
spring.devtools.restart.trigger-file=.reloadtrigger
```
