# Supporting Technologies
*Chapters 22–26 — XML Binding (JAXB), JSON-P/JSON-B, Jakarta Mail, Application Client, Scripting*

## Chapter 22: XML Binding (JAXB 4.0 / Jakarta XML Binding)

Jakarta XML Binding marshals/unmarshals Java objects to/from XML.

### Dependency (Jakarta EE 10 — standalone, not bundled with server)
```xml
<dependency>
  <groupId>jakarta.xml.bind</groupId>
  <artifactId>jakarta.xml.bind-api</artifactId>
  <version>4.0.0</version>
</dependency>
<dependency>
  <groupId>com.sun.xml.bind</groupId>
  <artifactId>jaxb-impl</artifactId>
  <version>4.0.3</version>
  <scope>runtime</scope>
</dependency>
```

> Note: JAXB was removed from the JDK in Java 11 and is no longer included in Jakarta EE app servers by default. Add it explicitly.

### Annotating a JAXB Class
```java
import jakarta.xml.bind.annotation.*;

@XmlRootElement(name="user")
@XmlAccessorType(XmlAccessType.FIELD)
public class User {

    @XmlAttribute
    private Long id;

    @XmlElement(name="full-name")
    private String name;

    @XmlElement
    private String email;

    @XmlTransient
    private String password;   // excluded from XML

    @XmlElementWrapper(name="roles")
    @XmlElement(name="role")
    private List<String> roles;

    @XmlElement
    @XmlSchemaType(name="date")
    private LocalDate created;
}
```

### Marshal (Object → XML)
```java
JAXBContext ctx = JAXBContext.newInstance(User.class);
Marshaller m = ctx.createMarshaller();
m.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);

// To string
StringWriter sw = new StringWriter();
m.marshal(user, sw);
String xml = sw.toString();

// To file
m.marshal(user, new File("user.xml"));
```

### Unmarshal (XML → Object)
```java
JAXBContext ctx = JAXBContext.newInstance(User.class);
Unmarshaller u = ctx.createUnmarshaller();

User user = (User) u.unmarshal(new File("user.xml"));
User user2 = (User) u.unmarshal(new StringReader(xmlString));
```

### JAXB with Jakarta REST
Jakarta REST (JAX-RS) auto-converts JAXB-annotated objects to/from XML when `Content-Type: application/xml`:
```java
@GET @Path("{id}")
@Produces({MediaType.APPLICATION_XML, MediaType.APPLICATION_JSON})
public User getUser(@PathParam("id") Long id) {
    return userService.findById(id);  // JAXB marshalling automatic
}
```

### Generating Classes from XSD
```bash
# Using xjc tool from JAXB RI
xjc -d src/main/java -p com.example.model schema.xsd
```

With Maven:
```xml
<plugin>
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>jaxb2-maven-plugin</artifactId>
  <configuration>
    <sources><source>src/main/xsd</source></sources>
    <packageName>com.example.model</packageName>
  </configuration>
</plugin>
```

---

## Chapter 23: JSON Handling (JSON-P 2.1 and JSON-B 3.0)

### JSON-P 2.1 — Low-Level JSON Processing

**Object Model API:**
```java
import jakarta.json.*;

// Build JSON
JsonObject obj = Json.createObjectBuilder()
    .add("name", "Alice")
    .add("age", 30)
    .add("active", true)
    .add("address", Json.createObjectBuilder()
        .add("city", "Berlin")
        .add("country", "DE"))
    .add("roles", Json.createArrayBuilder()
        .add("user").add("admin"))
    .build();

// Write to string
String json = obj.toString();
StringWriter sw = new StringWriter();
try (JsonWriter w = Json.createWriter(sw)) { w.write(obj); }

// Parse
JsonObject parsed = Json.createReader(new StringReader(json)).readObject();
String name = parsed.getString("name");
int age = parsed.getInt("age");
```

**Streaming API (memory-efficient for large JSON):**
```java
// Write
JsonGenerator gen = Json.createGenerator(outputStream);
gen.writeStartObject()
   .write("name", "Alice")
   .write("age", 30)
   .writeEnd()
   .close();

// Read/parse
JsonParser parser = Json.createParser(inputStream);
while (parser.hasNext()) {
    JsonParser.Event event = parser.next();
    if (event == JsonParser.Event.KEY_NAME && "name".equals(parser.getString())) {
        parser.next();
        System.out.println("Name: " + parser.getString());
    }
}
```

**JSON Merge Patch / JSON Patch (JSON-P 2.0+):**
```java
// JSON Merge Patch — update only specified fields
JsonMergePatch patch = Json.createMergePatch(
    Json.createObjectBuilder().add("email", "new@example.com").build());
JsonObject updated = patch.apply(originalObject).asJsonObject();

// JSON Patch — RFC 6902 operations
JsonPatch patch = Json.createPatchBuilder()
    .replace("/name", "Bob")
    .add("/roles/-", "manager")
    .remove("/temp")
    .build();
JsonObject patched = patch.apply(original);
```

---

### JSON-B 3.0 — JSON Binding (Object ↔ JSON)

Higher-level than JSON-P — binds Java objects automatically.

**Dependency:**
```xml
<dependency>
  <groupId>jakarta.json.bind</groupId>
  <artifactId>jakarta.json.bind-api</artifactId>
  <version>3.0.0</version>
</dependency>
<!-- Runtime: Yasson (reference impl) -->
<dependency>
  <groupId>org.eclipse</groupId>
  <artifactId>yasson</artifactId>
  <version>3.0.3</version>
  <scope>runtime</scope>
</dependency>
```

**Basic marshal/unmarshal:**
```java
Jsonb jsonb = JsonbBuilder.create();

// Object → JSON
String json = jsonb.toJson(user);

// JSON → Object
User user = jsonb.fromJson(json, User.class);

// List
List<User> users = jsonb.fromJson(jsonArray, new ArrayList<User>(){}.getClass().getGenericSuperclass());
// Or using TypeToken-style:
List<User> users = jsonb.fromJson(json, new ParameterizedCollectionType(List.class, User.class));
```

**Customizing JSON-B with Annotations:**
```java
public class User {
    @JsonbProperty("full_name")    // rename field
    public String name;

    @JsonbTransient                // exclude
    public String password;

    @JsonbDateFormat("yyyy-MM-dd")
    public LocalDate created;

    @JsonbNumberFormat("#,##0.00")
    public BigDecimal balance;

    @JsonbNillable                 // include null values
    public String optionalField;
}
```

**JSON-B Configuration:**
```java
JsonbConfig config = new JsonbConfig()
    .withPropertyNamingStrategy(PropertyNamingStrategy.LOWER_CASE_WITH_UNDERSCORES)
    .withNullValues(true)
    .withFormatting(true)
    .withDateFormat("yyyy-MM-dd'T'HH:mm:ssZ", Locale.getDefault());

Jsonb jsonb = JsonbBuilder.create(config);
```

**Custom Serializer/Deserializer:**
```java
public class MoneySerializer implements JsonbSerializer<Money> {
    @Override
    public void serialize(Money obj, JsonGenerator gen, SerializationContext ctx) {
        gen.writeStartObject();
        gen.write("amount", obj.getAmount());
        gen.write("currency", obj.getCurrency().getCurrencyCode());
        gen.writeEnd();
    }
}

JsonbConfig config = new JsonbConfig()
    .withSerializers(new MoneySerializer());
```

---

## Chapter 24: Jakarta Mail 2.1

### Dependency
```xml
<dependency>
  <groupId>jakarta.mail</groupId>
  <artifactId>jakarta.mail-api</artifactId>
  <version>2.1.0</version>
</dependency>
<!-- Runtime impl: Eclipse Angus Mail (successor to JavaMail) -->
<dependency>
  <groupId>org.eclipse.angus</groupId>
  <artifactId>angus-mail</artifactId>
  <version>1.1.0</version>
  <scope>runtime</scope>
</dependency>
```

### Sending Email
```java
@ApplicationScoped
public class EmailService {

    @Resource(name="mail/myMailSession")
    private Session mailSession;   // configured in server

    public void sendWelcome(String to, String name) throws MessagingException {
        Message msg = new MimeMessage(mailSession);
        msg.setFrom(new InternetAddress("noreply@example.com"));
        msg.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
        msg.setSubject("Welcome, " + name + "!");
        msg.setText("Thanks for joining!");
        Transport.send(msg);
    }

    public void sendHtmlEmail(String to, String subject, String html)
            throws MessagingException {
        Message msg = new MimeMessage(mailSession);
        msg.setFrom(new InternetAddress("noreply@example.com"));
        msg.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
        msg.setSubject(subject);
        msg.setContent(html, "text/html; charset=UTF-8");
        Transport.send(msg);
    }

    public void sendWithAttachment(String to, String subject,
                                    String body, File attachment)
            throws MessagingException {
        MimeMultipart multipart = new MimeMultipart();

        MimeBodyPart textPart = new MimeBodyPart();
        textPart.setText(body);
        multipart.addBodyPart(textPart);

        MimeBodyPart attachPart = new MimeBodyPart();
        attachPart.attachFile(attachment);
        multipart.addBodyPart(attachPart);

        Message msg = new MimeMessage(mailSession);
        msg.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
        msg.setSubject(subject);
        msg.setContent(multipart);
        Transport.send(msg);
    }
}
```

### Configuring Mail Session in WildFly
```bash
./bin/jboss-cli.sh --connect
/subsystem=mail/mail-session=MyMail:add(jndi-name="java:jboss/mail/MyMail", from="noreply@example.com")
/subsystem=mail/mail-session=MyMail/server=smtp:add(outbound-socket-binding-ref="mail-smtp", username="user", password="pass", tls=true)
```

Or in `standalone.xml`:
```xml
<mail-session name="MyMail" jndi-name="java:jboss/mail/MyMail" from="noreply@example.com">
  <smtp-server outbound-socket-binding-ref="mail-smtp" tls="true"
               username="smtp-user" password="smtp-pass"/>
</mail-session>
```

### Reading Email (IMAP)
```java
Properties props = new Properties();
props.put("mail.store.protocol", "imaps");
Session session = Session.getInstance(props);
Store store = session.getStore("imaps");
store.connect("imap.example.com", 993, "user@example.com", "pass");

Folder inbox = store.getFolder("INBOX");
inbox.open(Folder.READ_ONLY);
Message[] messages = inbox.getMessages();
for (Message m : messages) {
    System.out.println("From: " + m.getFrom()[0]);
    System.out.println("Subject: " + m.getSubject());
}
inbox.close(false);
store.close();
```

---

## Chapter 25: Application Client (Groovy)

The Jakarta EE Application Client is a standalone Java SE client that can access Jakarta EE services (EJBs, JMS, JNDI) with container-managed security and injection.

### Groovy Client Accessing Jakarta EE Services
Groovy integrates naturally with Java EE — use it for rapid scripts, test clients, or DSL-based configurations.

**`build.gradle` for Groovy client:**
```groovy
dependencies {
    implementation 'org.codehaus.groovy:groovy-all:3.0.19'
    implementation 'org.wildfly:wildfly-client-all:27.0.0.Final'
    provided 'jakarta.platform:jakarta.jakartaee-api:10.0.0'
}
```

**Groovy EJB remote client:**
```groovy
import javax.naming.InitialContext

def props = new Properties()
props['java.naming.factory.initial'] = 'org.wildfly.naming.client.WildFlyInitialContextFactory'
props['java.naming.provider.url'] = 'remote+http://localhost:8080'

def ctx = new InitialContext(props)
def ejb = ctx.lookup('myapp/UserServiceBean!com.example.UserService')
def users = ejb.findAll()
users.each { println it.name }
```

**Groovy for configuration DSLs:**
```groovy
// Application configuration as Groovy DSL
application {
    name = "My App"
    datasource {
        url = "jdbc:postgresql://localhost/mydb"
        pool { maxSize = 20; minSize = 5 }
    }
    mail {
        smtp = "smtp.example.com"; port = 587; tls = true
    }
}
```

---

## Chapter 26: Adding Scripting Languages

### Scripting via JSR-223 (`javax.script` / `jakarta.script`)
The scripting API lets Jakarta EE apps embed and execute scripts at runtime.

**Groovy via ScriptEngine:**
```java
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("groovy");

// Eval string
engine.eval("println 'Hello from Groovy'");

// Bind Java objects to script
Bindings bindings = engine.createBindings();
bindings.put("userService", userService);
bindings.put("userId", 42L);
engine.eval("def u = userService.findById(userId); println u.name", bindings);

// Execute from file
engine.eval(new FileReader("scripts/process.groovy"));
```

**Supported engines:**
| Language | Engine name | Maven artifact |
|----------|-------------|---------------|
| Groovy | `groovy` | `org.codehaus.groovy:groovy-jsr223` |
| JavaScript (Nashorn) | `nashorn` | Bundled until Java 14 → use GraalJS for Java 17+ |
| Python (Jython) | `python` | `org.python:jython` |
| Ruby (JRuby) | `jruby` | `org.jruby:jruby` |
| Kotlin | `kotlin` | `org.jetbrains.kotlin:kotlin-script-runtime` |

**GraalJS for Java 17+ (replaces Nashorn):**
```xml
<dependency>
  <groupId>org.graalvm.js</groupId>
  <artifactId>js-scriptengine</artifactId>
  <version>23.1.0</version>
</dependency>
```
```java
ScriptEngine engine = manager.getEngineByName("graal.js");
engine.eval("var result = [1,2,3].map(x => x * 2); print(result)");
```

### Dynamic Business Rules with Scripts
```java
@ApplicationScoped
public class RuleEngine {
    private final ScriptEngine groovyEngine;

    public RuleEngine() {
        groovyEngine = new ScriptEngineManager().getEngineByName("groovy");
    }

    public boolean evaluate(String rule, Map<String, Object> context)
            throws ScriptException {
        Bindings b = groovyEngine.createBindings();
        b.putAll(context);
        return (Boolean) groovyEngine.eval(rule, b);
    }
}

// Usage
boolean eligible = ruleEngine.evaluate(
    "user.age >= 18 && order.total < 10000",
    Map.of("user", user, "order", order));
```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `ClassNotFoundException: JAXBContext` | JAXB removed from JDK 11+ | Add `jaxb-impl` dependency |
| XML namespace mismatch | Generated code uses old `javax` namespace | Update `@XmlRootElement` or use JAXB 4 annotations |
| JSON-B ignores `null` | Default behavior | Add `@JsonbNillable` or configure `withNullValues(true)` |
| Mail not sent | JNDI lookup fails or SMTP config wrong | Check `jndi-name` matches `@Resource` name |
| Groovy script not found | ScriptEngine name wrong | Print `manager.getEngineFactories()` to see available engines |
| Script execution sandbox needed | Security concern | Run in separate ClassLoader or use GraalVM sandbox |
