# Development Workflow
*Chapters 1–6 — Server Install, Eclipse, NetBeans, Git/SVN, CI, Maven Repos*

## Chapter 1: Installing a Development Server

### WildFly (Reference Implementation–compatible, Jakarta EE 10)
WildFly 27+ supports Jakarta EE 10.

**Download and start:**
```bash
# Download from wildfly.org
unzip wildfly-27.x.x.Final.zip
cd wildfly-27.x.x.Final
./bin/standalone.sh          # Linux/Mac
bin\standalone.bat           # Windows

# Management console: http://localhost:9990
# Application: http://localhost:8080
```

**Add admin user:**
```bash
./bin/add-user.sh
# Interactive — choose Management User, set username/password
```

**Deploy a WAR:**
```bash
# Copy to deployments folder (hot deploy)
cp myapp.war standalone/deployments/

# Or via CLI
./bin/jboss-cli.sh --connect
deploy /path/to/myapp.war
```

**Key directories:**
| Directory | Purpose |
|-----------|---------|
| `standalone/deployments/` | Hot-deploy folder |
| `standalone/configuration/standalone.xml` | Main server config |
| `standalone/log/server.log` | Application log |
| `modules/` | Server module system |

### GlassFish 7 / Payara 6
```bash
# GlassFish
./bin/asadmin start-domain domain1
./bin/asadmin deploy myapp.war

# Payara — same asadmin commands
./bin/asadmin start-domain
```

Admin console: http://localhost:4848

### Docker-Based Dev Server
```bash
# WildFly
docker run -p 8080:8080 -p 9990:9990 \
  -e WILDFLY_PASSWORD=admin \
  quay.io/wildfly/wildfly:latest

# GlassFish 7
docker run -p 8080:8080 -p 4848:4848 \
  eclipse/glassfish:7.0.0
```

---

## Chapter 2: Eclipse IDE Setup

### Eclipse IDE for Enterprise Java (Eclipse EE)
Download "Eclipse IDE for Enterprise Java and Web Developers" from eclipse.org.

### WildFly Server Adapter
1. **Help → Eclipse Marketplace** → search "JBoss Tools" → install
2. **Window → Preferences → Server → Runtime Environments → Add** → WildFly
3. Point to WildFly install directory

### Creating a Jakarta EE 10 Maven Project
**File → New → Maven Project → maven-archetype-webapp**, then convert:

Or use the Jakarta EE archetype:
```bash
mvn archetype:generate \
  -DarchetypeGroupId=org.eclipse.starter \
  -DarchetypeArtifactId=jakarta-starter \
  -DarchetypeVersion=2.1.0 \
  -DjakartaVersion=10 \
  -Dprofile=full
```

**Minimal `pom.xml` for Jakarta EE 10:**
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>myapp</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>war</packaging>

  <properties>
    <maven.compiler.release>11</maven.compiler.release>
    <failOnMissingWebXml>false</failOnMissingWebXml>
  </properties>

  <dependencies>
    <dependency>
      <groupId>jakarta.platform</groupId>
      <artifactId>jakarta.jakartaee-api</artifactId>
      <version>10.0.0</version>
      <scope>provided</scope>   <!-- server provides at runtime -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-war-plugin</artifactId>
        <version>3.4.0</version>
      </plugin>
    </plugins>
  </build>
</project>
```

### WildFly Maven Plugin (deploy from IDE / CLI)
```xml
<plugin>
  <groupId>org.wildfly.plugins</groupId>
  <artifactId>wildfly-maven-plugin</artifactId>
  <version>4.2.0.Final</version>
  <configuration>
    <hostname>localhost</hostname>
    <port>9990</port>
    <username>admin</username>
    <password>admin</password>
  </configuration>
</plugin>
```
```bash
mvn wildfly:deploy
mvn wildfly:undeploy
mvn wildfly:redeploy
```

---

## Chapter 3: NetBeans IDE

### Setup
Download **Apache NetBeans** (netbeans.apache.org) — Jakarta EE support is built-in.

**Add WildFly server:**
- Services panel → Servers → right-click → Add Server → WildFly Application Server → point to install dir

**New Jakarta EE project:**
File → New Project → Java with Maven → Web Application → select Jakarta EE 10, WildFly server

### Hot Deploy in NetBeans
NetBeans automatically redeploys on Save when the project is running in the IDE. Incremental deployment avoids full redeploy for class changes.

---

## Chapter 4: Git and Subversion

### Git Essentials for Jakarta EE Projects
```bash
# Initialize
git init
echo "target/" >> .gitignore
echo "*.class" >> .gitignore

# Standard workflow
git add src/ pom.xml
git commit -m "feat: add user registration endpoint"
git push origin main

# Feature branch
git checkout -b feature/user-auth
# ... develop ...
git merge --no-ff feature/user-auth
```

**`.gitignore` for Maven/Jakarta EE:**
```
target/
*.class
*.war
*.ear
.classpath
.project
.settings/
nbproject/private/
```

### Subversion (SVN) — still used in legacy enterprise setups
```bash
# Checkout
svn checkout https://svn.example.com/repos/myapp/trunk myapp

# Commit
svn add src/
svn commit -m "Add feature X"

# Branch
svn copy trunk/ branches/feature-x -m "Create feature-x branch"
```

---

## Chapter 5: Continuous Integration

### Jenkins Pipeline for Jakarta EE
```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
            post {
                always {
                    junit 'target/surefire-reports/*.xml'
                }
            }
        }
        stage('Deploy to WildFly') {
            steps {
                sh 'mvn wildfly:redeploy'
            }
        }
    }
}
```

### Arquillian — In-Container Testing
Arquillian lets tests run inside a real application server:

```xml
<!-- pom.xml test dependencies -->
<dependency>
  <groupId>org.jboss.arquillian.junit5</groupId>
  <artifactId>arquillian-junit5-container</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.wildfly.arquillian</groupId>
  <artifactId>wildfly-arquillian-container-managed</artifactId>
  <version>5.0.0.Final</version>
  <scope>test</scope>
</dependency>
```

```java
@ExtendWith(ArquillianExtension.class)
public class UserServiceTest {

    @Deployment
    public static WebArchive createDeployment() {
        return ShrinkWrap.create(WebArchive.class, "test.war")
            .addClasses(UserService.class, User.class)
            .addAsWebInfResource(EmptyAsset.INSTANCE, "beans.xml");
    }

    @Inject UserService userService;

    @Test
    public void testCreateUser() {
        User u = userService.create("alice@example.com");
        assertNotNull(u.getId());
    }
}
```

### GitHub Actions
```yaml
# .github/workflows/build.yml
name: Jakarta EE Build
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: mvn clean verify
      - uses: actions/upload-artifact@v4
        with:
          name: app-war
          path: target/*.war
```

---

## Chapter 6: Corporate Maven Repositories (Nexus / Artifactory)

### Why a Corporate Maven Repo?
- Proxy public Maven Central (cache artifacts, reduce internet dependency)
- Host internal/private artifacts
- Enforce artifact approval policies

### Nexus Repository Manager Setup
```bash
# Docker
docker run -d -p 8081:8081 --name nexus \
  sonatype/nexus3:latest
# Default credentials: admin / (check nexus-data/admin.password)
```

### Configuring Maven to Use Corporate Nexus
**`~/.m2/settings.xml`:**
```xml
<settings>
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>http://nexus.example.com:8081/repository/maven-public/</url>
    </mirror>
  </mirrors>
  <servers>
    <server>
      <id>nexus</id>
      <username>developer</username>
      <password>secret</password>
    </server>
    <server>
      <id>nexus-releases</id>
      <username>developer</username>
      <password>secret</password>
    </server>
  </servers>
</settings>
```

### Publishing to Nexus from `pom.xml`
```xml
<distributionManagement>
  <repository>
    <id>nexus-releases</id>
    <url>http://nexus.example.com:8081/repository/maven-releases/</url>
  </repository>
  <snapshotRepository>
    <id>nexus-snapshots</id>
    <url>http://nexus.example.com:8081/repository/maven-snapshots/</url>
  </snapshotRepository>
</distributionManagement>
```

```bash
mvn deploy          # publish SNAPSHOT or RELEASE
mvn release:prepare # bump version, tag
mvn release:perform # build + deploy tagged release
```

### Structuring Multi-Module Jakarta EE Projects
```xml
<!-- parent pom.xml -->
<modules>
  <module>myapp-model</module>      <!-- JPA entities, DTOs -->
  <module>myapp-service</module>    <!-- CDI services, EJBs -->
  <module>myapp-web</module>        <!-- WAR: Faces, REST -->
  <module>myapp-ear</module>        <!-- EAR assembler (optional) -->
</modules>

<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>jakarta.platform</groupId>
      <artifactId>jakarta.jakartaee-api</artifactId>
      <version>10.0.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

---

## Common Dev Workflow Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Server not starting | Port 8080/9990 in use | `lsof -i :8080`, kill process |
| WAR not deploying | CDI `beans.xml` missing | Add empty `WEB-INF/beans.xml` |
| ClassNotFoundException at runtime | Dependency not `provided` | Check scope; server already has the API |
| Maven can't download artifacts | Behind corporate proxy | Configure `~/.m2/settings.xml` proxy or mirror |
| Hot deploy not picking up changes | Eclipse not building before deploy | Project → Build Automatically |
| Tests failing in CI but not locally | Server not available | Use Arquillian managed container or Testcontainers |
