# Ch 8 — Making Better Decisions (Drools / Red Hat Decision Services)

> **Book context:** Covered JBoss BRMS (Business Rules Management System). Current state:
> - Community project: **Drools 9/10** (KIE platform)
> - Enterprise product: **Red Hat Decision Manager** → rebranded to **Red Hat Decision Services**
> - Cloud-native: **Kogito** (Quarkus/Spring Boot based, rule engine as microservice)
> - Standalone: KIE Server (REST/JMS API for rules execution)

## Drools Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DROOLS RULE ENGINE                           │
│                                                                 │
│  Rule Sources:                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ DRL File │  │  DMN     │  │ Decision │  │  Spreadsheet │   │
│  │ (rules)  │  │ (model)  │  │  Table   │  │  (XLS rules) │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       └─────────────┴─────────────┴────────────────┘           │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    KIE Container                          │  │
│  │  (compiled rules, KIE Base → KIE Session)                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                     PHREAK algorithm                            │
│                     (efficient rule matching)                   │
│                              │                                  │
│                              ▼                                  │
│  Insert Facts → Match Rules (Agenda) → Fire Rules → Results    │
└─────────────────────────────────────────────────────────────────┘
```

## DRL (Drools Rule Language)

### Rule Structure

```drl
package com.example.rules;

import com.example.model.Order;
import com.example.model.Customer;
import com.example.model.Discount;

// Global variable (shared across rules)
global DiscountService discountService;

// Rule: standard format
rule "Apply VIP Discount"
    dialect "java"
    salience 10         // higher = fires first (default 0)
    when
        $customer : Customer(type == "VIP", active == true)
        $order    : Order(customer == $customer, total > 100.0)
    then
        Discount d = discountService.getVipDiscount();
        $order.applyDiscount(d);
        update($order);  // notify engine of change
        System.out.println("VIP discount applied: " + d.getRate());
end

// Rule with accumulate (aggregate)
rule "Bulk Order Discount"
    when
        $customer : Customer()
        $count : Long(this >= 5) from accumulate(
            Order(customer == $customer, status == "PENDING"),
            count($order)
        )
    then
        // $customer has 5+ pending orders
        modify($customer) { setEligibleForBulkDiscount(true); }
end

// Rule with not/exists
rule "Flag No Recent Activity"
    when
        $customer : Customer()
        not Order(customer == $customer, createdDate > "2025-01-01")
    then
        $customer.setActive(false);
        update($customer);
end
```

### Conditions (LHS Patterns)

```drl
// Property constraint
Customer(age > 18, name != null)

// Binding
$order : Order(total > $minTotal, $total : total)

// Field access
Order(customer.type == "PREMIUM")

// eval (avoid if possible — breaks indexing)
eval($order.getTotal() > calculateMinimum())

// Collections
Order(items.size > 0)
Order(items contains "WIDGET-A")

// from — derive facts from expression
$item : OrderItem() from $order.getItems()

// Nested from
$lowStock : Product(stock < 10) from stockService.getProducts()
```

## KIE API (Drools Java API)

```java
// Maven dependency:
// org.kie:kie-ci:9.x.Final
// org.drools:drools-core:9.x.Final

@ApplicationScoped
public class RulesEngine {

    private KieContainer kieContainer;

    @PostConstruct
    public void init() {
        KieServices ks = KieServices.Factory.get();
        // Loads from kmodule.xml in META-INF
        kieContainer = ks.getKieClasspathContainer();
    }

    public List<Discount> evaluateOrder(Order order, Customer customer) {
        KieSession session = kieContainer.newKieSession("OrderRulesSession");
        List<Discount> results = new ArrayList<>();

        try {
            // Set globals
            session.setGlobal("discountService", discountService);
            session.setGlobal("results", results);

            // Insert facts
            session.insert(order);
            session.insert(customer);

            // Fire all matching rules
            int fired = session.fireAllRules();
            log.debug("Fired {} rules", fired);

        } finally {
            session.dispose(); // always dispose stateful sessions
        }

        return results;
    }

    // Stateless session (no state between calls)
    public void validateOrder(Order order) {
        StatelessKieSession session = kieContainer.newStatelessKieSession();
        session.execute(Arrays.asList(order));
    }
}
```

### kmodule.xml

```xml
<!-- src/main/resources/META-INF/kmodule.xml -->
<kmodule xmlns="http://www.drools.org/xsd/kmodule">
  <kbase name="OrderRules"
         packages="com.example.rules.orders"
         default="false">
    <ksession name="OrderRulesSession" type="stateful" default="false"/>
    <ksession name="OrderValidation" type="stateless"/>
  </kbase>

  <kbase name="PricingRules"
         packages="com.example.rules.pricing"
         equalsBehavior="equality">
    <ksession name="PricingSession" type="stateful" default="true"/>
  </kbase>
</kmodule>
```

## Decision Model and Notation (DMN)

DMN is the OMG standard for decision modeling. Drools supports DMN 1.4.

### DMN Structure

```
┌─────────────────────────────────────────────────────┐
│                   DMN DIAGRAM                       │
│                                                     │
│  Input Data       Decision          Business        │
│  ┌─────────┐     ┌──────────┐      Knowledge       │
│  │ Age     │────▶│          │      ┌─────────────┐  │
│  └─────────┘     │ Discount │◀─────│ Discount    │  │
│  ┌─────────┐     │ Decision │      │ Table (DT)  │  │
│  │ Type    │────▶│          │      └─────────────┘  │
│  └─────────┘     └──────────┘                       │
└─────────────────────────────────────────────────────┘
```

### DMN Decision Table (XML excerpt)

```xml
<decision name="Determine Discount" id="discount_decision">
  <decisionTable hitPolicy="UNIQUE">
    <input label="Customer Type">
      <inputExpression typeRef="string">
        <text>customer.type</text>
      </inputExpression>
    </input>
    <input label="Order Total">
      <inputExpression typeRef="number">
        <text>order.total</text>
      </inputExpression>
    </input>
    <output label="Discount Rate" typeRef="number" name="discountRate"/>
    <rule>
      <inputEntry><text>"VIP"</text></inputEntry>
      <inputEntry><text>>= 100</text></inputEntry>
      <outputEntry><text>0.20</text></outputEntry>
    </rule>
    <rule>
      <inputEntry><text>"VIP"</text></inputEntry>
      <inputEntry><text>< 100</text></inputEntry>
      <outputEntry><text>0.10</text></outputEntry>
    </rule>
    <rule>
      <inputEntry><text>"STANDARD"</text></inputEntry>
      <inputEntry><text>-</text></inputEntry>   <!-- any -->
      <outputEntry><text>0.05</text></outputEntry>
    </rule>
  </decisionTable>
</decision>
```

### Execute DMN via API

```java
DMNRuntime runtime = KieRuntimeFactory.of(kieContainer.getKieBase()).get(DMNRuntime.class);
DMNModel model = runtime.getModel("http://example.com/decisions", "DiscountDecisions");

DMNContext context = runtime.newContext();
context.set("customer", Map.of("type", "VIP", "age", 35));
context.set("order", Map.of("total", 150.0));

DMNResult result = runtime.evaluateAll(model, context);
if (!result.hasErrors()) {
    DMNDecisionResult decision = result.getDecisionResultByName("Determine Discount");
    Number discountRate = (Number) decision.getResult(); // 0.20
}
```

## Decision Tables (Spreadsheet Rules)

Excel/CSV decision tables map to Drools rules at compile time.

```
| RuleSet     | DiscountRules                    |
| RuleTable   | Discount                         |
|-------------|----------------------------------|
| CONDITION   | CONDITION          | ACTION      |
| customer.type | order.total      | discount    |
|             |                    |             |
| "VIP"       | >= 100            | 0.20        |
| "VIP"       | < 100             | 0.10        |
| "STANDARD"  |                   | 0.05        |
```

Load:
```java
Resource resource = ResourceFactory.newClassPathResource("DiscountRules.xlsx");
KieHelper helper = new KieHelper();
helper.addResource(resource, ResourceType.DTABLE);
KieBase kbase = helper.build();
```

## KIE Server (Standalone Rule Execution)

KIE Server exposes rules via REST/JMS without embedding the engine in your app.

```bash
# Start KIE Server
java -jar kie-server.jar

# Deploy KJAR
curl -X PUT http://kie-server:8080/kie-server/services/rest/server/containers/my-rules \
  -H "Content-Type: application/json" \
  -u user:password \
  -d '{"container-id":"my-rules","release-id":{"group-id":"com.example","artifact-id":"discount-rules","version":"1.0.0"}}'

# Execute rules
curl -X POST http://kie-server:8080/kie-server/services/rest/server/containers/instances/my-rules \
  -H "Content-Type: application/json" \
  -u user:password \
  -d '{
    "commands": [{
      "insert": {"object": {"com.example.Order": {"total": 150.0}}}
    }, {
      "fire-all-rules": {}
    }]
  }'
```

## Kogito (Cloud-Native Rules)

For new projects, **Kogito** embeds Drools in a Quarkus or Spring Boot microservice:

```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.kie.kogito</groupId>
  <artifactId>kogito-quarkus-rules</artifactId>
</dependency>
```

Rules are auto-discovered from `src/main/resources/**/*.drl` and exposed as REST endpoints automatically.

## Rules Design Patterns

```
What type of decision are you modeling?
├── Simple if/then logic → DRL rules (programmatic control)
├── Tabular / matrix decisions → Decision Tables (Excel/CSV)
├── Business-user-friendly model → DMN diagram + decision table
├── Complex event processing → Drools Fusion (CEP) with event streams
└── Stateless scoring/validation → StatelessKieSession (no state)

When to use rules vs. code?
├── Rules change frequently (business users update them) → Rules engine
├── Rules are complex conditionals with many combinations → Decision tables
├── Logic is simple, rarely changes → Plain Java/code
└── Need business users to manage rules in UI → Business Central / KIE Workbench
```

## DMN Hit Policies

| Policy | Description | Returns |
|--------|-------------|---------|
| `UNIQUE` | One rule matches (default) | Single value |
| `FIRST` | First matching rule wins | Single value |
| `RULE ORDER` | All matching, in order | List |
| `COLLECT` | All matching, aggregated | List or aggregation |
| `ANY` | Multiple rules can match if same result | Single value |
| `PRIORITY` | Highest-priority matching rule | Single value |
