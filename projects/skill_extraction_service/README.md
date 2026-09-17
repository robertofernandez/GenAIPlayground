# Skill Extraction Service

Backend service for extracting technical skills from job descriptions using Large Language Models (LLMs).

The project is being developed as a **professional-style learning project**, with the goal of exploring modern Java, Spring Boot, relational and NoSQL persistence, external APIs, local AI models, distributed systems, containerization, observability, resilience, Kubernetes and AWS.

The initial implementation is a **modular monolith** that is intentionally designed so that selected modules can later be extracted into independent microservices.

---

# 1. Goals

The main goals of the project are:

- Build a production-oriented backend using Java and Spring Boot.
- Extract skills from job descriptions using an LLM.
- Persist normalized skills in a relational database.
- Persist LLM prompts and responses for auditing and analysis.
- Reduce LLM API costs by detecting similar job descriptions.
- Experiment with locally hosted embedding/ML models.
- Explore vector search using Elasticsearch/OpenSearch.
- Learn asynchronous and event-driven architectures.
- Learn containerization with Docker.
- Deploy the application locally and later to AWS.
- Experiment with Kubernetes locally using WSL.
- Experiment with Kubernetes in AWS.
- Practice observability, resilience, scalability and distributed-system concepts.
- Keep infrastructure implementations replaceable whenever there is a meaningful reason to do so.

---

# 2. High-Level Architecture

The initial architecture is a **modular monolith using Hexagonal Architecture / Ports and Adapters principles**.

```text
                         ┌───────────────────┐
                         │      Client       │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    REST API       │
                         │   Spring MVC      │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Application     │
                         │     Services      │
                         └─────────┬─────────┘
                                   │
                  ┌────────────────┼─────────────────┐
                  │                │                 │
                  ▼                ▼                 ▼
             Skill Port       LLM Port        Similarity Port
                  │                │                 │
                  ▼                ▼                 ▼
              JPA/JDBC        LLM Services      Similarity
                  │                │              Provider
                  ▼                │                 │
              MariaDB              │                 │
                                   ▼                 ▼
                              Anthropic         Local Model
                              OpenAI            / Embeddings
                              Other LLMs             │
                                   │                 ▼
                                   ▼            OpenSearch /
                                MongoDB          Elasticsearch
```

The initial system is intentionally deployed as a single Spring Boot application.

As the project evolves, selected components may become independent services:

```text
                   ┌────────────────────┐
                   │    API Gateway      │
                   └──────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      Skill Service    Similarity Service   Other Services
             │                │
             ▼                ▼
         MariaDB        Local ML Model
             │                │
             │                ▼
             │          OpenSearch
             │
             ▼
          MongoDB
```

The transition from modular monolith to microservices is intentional and incremental.

---

# 3. Architectural Principles

## 3.1 Modular Monolith First

The project will initially be implemented as one Spring Boot application.

We will not introduce multiple deployable services until there is a clear architectural reason to do so.

This allows the project to explore distributed-system concepts progressively without introducing unnecessary operational complexity from the beginning.

The internal modules will nevertheless have clear boundaries.

---

## 3.2 Hexagonal Architecture

The application will use Ports and Adapters principles.

The core application should depend on interfaces rather than infrastructure implementations.

For example:

```java
public interface LLMProvider {

    SkillExtractionResponse extractSkills(
        String jobDescription
    );
}
```

The application knows about `LLMProvider`.

It does not know that the implementation happens to use Anthropic.

Possible implementations:

```text
LLMProvider
    │
    ├── AnthropicLLMProvider
    ├── OpenAILLMProvider
    └── LocalLLMProvider
```

The same principle applies to other infrastructure components when abstraction is useful.

---

# 4. Main Functional Flow

The primary operation is:

```text
POST /api/v1/skills/extract
```

The logical flow is:

```text
Job Description
       │
       ▼
REST Controller
       │
       ▼
Application Service
       │
       ├──────────────► Similarity Provider
       │                       │
       │                       ▼
       │                 Similar Jobs?
       │                       │
       │                ┌──────┴──────┐
       │                │             │
       │               YES            NO
       │                │             │
       │                │             ▼
       │                │        LLM Provider
       │                │             │
       │                │             ▼
       │                │       Skill Extraction
       │                │             │
       │                └──────┬──────┘
       │                       │
       ▼                       ▼
 Skill Repository        Prompt History
       │                       │
       ▼                       ▼
   MariaDB                  MongoDB
```

The similarity mechanism will initially be optional and can evolve independently.

---

# 5. Package Structure

The recommended project structure is:

```text
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── skillservice/
│   │
│   │               ├── SkillServiceApplication.java
│   │               │
│   │               ├── api/
│   │               │   ├── v1/
│   │               │   │   ├── SkillExtractionController.java
│   │               │   │   ├── HealthController.java
│   │               │   │   └── dto/
│   │               │   │       ├── JobDescriptionRequest.java
│   │               │   │       ├── SkillExtractionResponse.java
│   │               │   │       └── SkillResponse.java
│   │               │   │
│   │               │   └── ApiExceptionHandler.java
│   │               │
│   │               ├── application/
│   │               │   ├── SkillExtractionService.java
│   │               │   └── SimilarityService.java
│   │               │
│   │               ├── domain/
│   │               │   ├── model/
│   │               │   │   ├── Skill.java
│   │               │   │   ├── JobDescription.java
│   │               │   │   └── SkillExtraction.java
│   │               │   │
│   │               │   └── port/
│   │               │       ├── LLMProvider.java
│   │               │       ├── SkillRepository.java
│   │               │       ├── PromptHistoryRepository.java
│   │               │       └── SimilarityProvider.java
│   │               │
│   │               ├── infrastructure/
│   │               │   │
│   │               │   ├── llmservices/
│   │               │   │   ├── anthropic/
│   │               │   │   │   ├── AnthropicLLMProvider.java
│   │               │   │   │   ├── AnthropicClient.java
│   │               │   │   │   ├── AnthropicResponseParser.java
│   │               │   │   │   └── AnthropicConfiguration.java
│   │               │   │   │
│   │               │   │   ├── openai/
│   │               │   │   │   ├── OpenAILLMProvider.java
│   │               │   │   │   ├── OpenAIClient.java
│   │               │   │   │   └── OpenAIConfiguration.java
│   │               │   │   │
│   │               │   │   └── local/
│   │               │   │       └── LocalLLMProvider.java
│   │               │   │
│   │               │   ├── persistence/
│   │               │   │   ├── relational/
│   │               │   │   │   ├── entity/
│   │               │   │   │   │   └── SkillEntity.java
│   │               │   │   │   ├── repository/
│   │               │   │   │   │   └── JpaSkillRepository.java
│   │               │   │   │   └── adapter/
│   │               │   │   │       └── SkillRepositoryAdapter.java
│   │               │   │   │
│   │               │   │   └── mongodb/
│   │               │   │       ├── document/
│   │               │   │       │   └── PromptExecutionDocument.java
│   │               │   │       ├── repository/
│   │               │   │       │   └── MongoPromptHistoryRepository.java
│   │               │   │       └── adapter/
│   │               │   │           └── PromptHistoryRepositoryAdapter.java
│   │               │   │
│   │               │   ├── similarity/
│   │               │   │   └── LocalSimilarityProvider.java
│   │               │   │
│   │               │   ├── messaging/
│   │               │   │   └── ...
│   │               │   │
│   │               │   ├── cache/
│   │               │   │   └── ...
│   │               │   │
│   │               │   └── configuration/
│   │               │       ├── DatabaseConfiguration.java
│   │               │       ├── MongoConfiguration.java
│   │               │       └── ...
│   │               │
│   │               └── shared/
│   │                   ├── exception/
│   │                   ├── logging/
│   │                   └── validation/
│   │
│   └── resources/
│       ├── application.yml
│       ├── application-local.yml
│       ├── application-docker.yml
│       ├── application-test.yml
│       ├── application-aws.yml
│       │
│       ├── prompts/
│       │   └── skill-extraction-prompt.txt
│       │
│       └── db/
│           └── migration/
│               ├── V1__initial_schema.sql
│               ├── V2__...
│               └── ...
│
└── test/
    └── java/
        └── com/
            └── example/
                └── skillservice/
                    ├── unit/
                    ├── integration/
                    └── architecture/
```

The exact package names can be adjusted when the project is created.

---

# 6. Why `infrastructure/llmservices`

LLM providers are infrastructure adapters implementing the domain/application port:

```text
domain.port.LLMProvider
             │
             │ implemented by
             ▼
infrastructure.llmservices
             │
       ┌─────┼──────────┐
       ▼     ▼          ▼
   anthropic openai    local
```

This makes adding another provider straightforward:

```text
infrastructure/
└── llmservices/
    ├── anthropic/
    ├── openai/
    ├── google/
    └── local/
```

The application layer remains unchanged.

---

# 7. REST API

The API will use Spring MVC.

Example:

```text
POST /api/v1/skills/extract
```

Request:

```json
{
  "description": "Senior Java developer with Spring Boot, AWS and Docker experience"
}
```

Response:

```json
{
  "title": "Senior Java Developer",
  "skills": [
    {
      "name": "Java",
      "category": "PROGRAMMING_LANGUAGE",
      "confidence": 0.99
    },
    {
      "name": "Spring Boot",
      "category": "FRAMEWORK",
      "confidence": 0.97
    }
  ],
  "summary": "..."
}
```

API DTOs will not be used as persistence entities.

---

# 8. DTOs vs Domain vs Persistence Entities

These concepts will remain separate.

```text
REST DTO
   │
   ▼
Application / Domain Model
   │
   ▼
Persistence Entity
```

For example:

```java
public record JobDescriptionRequest(
    @NotBlank
    @Size(max = 20_000)
    String description
) {}
```

Persistence will use separate entities:

```java
@Entity
@Table(name = "skills")
public class SkillEntity {
    ...
}
```

This prevents the API contract from becoming coupled to the database schema.

---

# 9. Relational Persistence

The relational database will contain normalized business data.

Initial local database:

```text
MariaDB
```

Persistence stack:

```text
Spring Data JPA
       ↓
Hibernate
       ↓
JDBC
       ↓
MariaDB
```

The application should avoid MariaDB-specific SQL whenever possible.

The system should remain compatible with other relational databases such as:

- PostgreSQL
- MySQL
- potentially other JPA-supported databases

The objective is not to pretend all databases are identical, but to avoid unnecessary vendor coupling.

---

# 10. Hibernate and Schema Generation

Entities will use standard JPA annotations:

```java
@Entity
@Table(name = "skills")
public class SkillEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;
}
```

Hibernate will be used to generate/validate the database schema during development.

However, Hibernate schema generation will **not** be the production database migration mechanism.

---

# 11. Flyway

Flyway will be used to manage database schema evolution.

Example:

```text
db/migration/

V1__initial_schema.sql
V2__add_skill_category.sql
V3__add_skill_alias.sql
V4__add_embedding.sql
```

Development workflow:

```text
JPA Entities
     │
     ▼
Hibernate schema generation
     │
     ▼
Review generated SQL
     │
     ▼
Flyway migration
     │
     ▼
Database
```

Production:

```text
Flyway
   │
   ▼
Database
```

Production Hibernate configuration should use:

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

The objective is:

> Hibernate describes the object-relational model; Flyway manages schema evolution.

---

# 12. MongoDB

MongoDB will store LLM execution history.

Example document:

```json
{
  "requestId": "...",
  "timestamp": "...",
  "provider": "anthropic",
  "model": "...",
  "prompt": "...",
  "jobDescription": "...",
  "response": "...",
  "latencyMs": 1240,
  "status": "SUCCESS",
  "tokenUsage": {
    "input": 123,
    "output": 456
  }
}
```

This information is intentionally kept separate from the normalized relational model.

MongoDB is suitable for this use case because the execution record can evolve over time and may contain provider-specific metadata.

---

# 13. LLM Abstraction

The application will depend on:

```java
public interface LLMProvider {

    SkillExtractionResponse extractSkills(
        String jobDescription
    );
}
```

Implementations:

```text
LLMProvider
    │
    ├── AnthropicLLMProvider
    ├── OpenAILLMProvider
    └── LocalLLMProvider
```

The application layer must not directly instantiate provider implementations.

Spring dependency injection will select the appropriate implementation.

Configuration will determine which provider is active.

---

# 14. LLM Client vs LLM Provider

The provider and HTTP client will have different responsibilities.

```text
SkillExtractionService
          │
          ▼
   LLMProvider
          │
          ▼
AnthropicLLMProvider
          │
          ▼
    AnthropicClient
          │
          ▼
       HTTP API
```

`LLMProvider` represents the business capability:

> Extract skills using an LLM.

`AnthropicClient` represents the infrastructure:

> Communicate with Anthropic's HTTP API.

This separation makes testing and provider replacement easier.

---

# 15. Prompt Management

Prompts will not be hard-coded inside Java classes.

Initial location:

```text
src/main/resources/prompts/
```

Example:

```text
skill-extraction-prompt.txt
```

Future versions may introduce:

```text
prompt/
├── skill-extraction/
│   ├── v1.txt
│   ├── v2.txt
│   └── ...
```

Prompt versioning is important because changing a prompt can change the behavior of the system.

Prompt version should therefore be persisted with the LLM execution history.

---

# 16. Similarity Detection

A major objective is to reduce calls to external LLM APIs.

The system should eventually detect whether a job description is sufficiently similar to a previously processed job.

Instead of asking an LLM:

```text
"Are these two jobs similar?"
```

the preferred mechanism is embedding-based similarity.

```text
Job Description
       │
       ▼
Embedding Model
       │
       ▼
Vector
       │
       ▼
Vector Search
       │
       ▼
Similar Jobs
```

This avoids unnecessary token consumption.

---

# 17. Local Similarity Model

The initial similarity implementation may use a model running locally.

Possible architecture:

```text
Spring Boot
     │
     │ HTTP
     ▼
Similarity Service
     │
     ▼
Local Embedding Model
```

The model may eventually run in a separate container.

The exact model/runtime will be evaluated during implementation.

---

# 18. Similarity Service: Monolith First

Initially, similarity functionality may live inside the Spring Boot application.

Example:

```text
application/
└── SimilarityService.java

domain/
└── port/
    └── SimilarityProvider.java

infrastructure/
└── similarity/
    └── LocalSimilarityProvider.java
```

Later it may become:

```text
similarity-service
```

with its own deployment.

The application-facing interface remains:

```java
public interface SimilarityProvider {

    List<SimilarJob> findSimilar(
        JobDescription jobDescription
    );
}
```

The implementation can then change from:

```text
LocalSimilarityProvider
```

to:

```text
RemoteSimilarityProvider
```

without changing the application logic.

---

# 19. Why Similarity May Become a Microservice

The similarity component has different computational characteristics from the main API.

The main service is primarily:

```text
HTTP
DB
external LLM API
```

The similarity service may be:

```text
CPU intensive
RAM intensive
potentially GPU intensive
ML runtime
Python/model ecosystem
```

Therefore independent scaling may eventually be useful:

```text
Skill Service
     │
     │ 10 instances
     │
     ▼
Similarity Service
     │
     │ 2 instances
     ▼
ML Model
```

The disadvantage is additional distributed-system complexity:

- network latency
- service discovery
- retries
- timeouts
- circuit breakers
- deployment complexity
- monitoring
- version compatibility

Therefore extraction into a microservice will be delayed until it provides educational or architectural value.

---

# 20. Elasticsearch / OpenSearch

OpenSearch or Elasticsearch will eventually be evaluated for:

- full-text search
- filtering
- ranking
- similarity
- vector search

The relational database remains the source of truth.

Conceptually:

```text
MariaDB
   │
   │ source of truth
   ▼
Jobs / Skills
   │
   │ indexing
   ▼
OpenSearch
   │
   ├── text search
   ├── filters
   └── vector search
```

The search engine is not intended to replace the transactional relational database.

---

# 21. Caching

Redis may be introduced later.

Potential use cases:

- caching extraction results
- caching similarity results
- idempotency keys
- rate limiting
- temporary state

A possible flow:

```text
Job Description
       │
       ▼
Calculate input hash
       │
       ▼
     Redis
       │
    ┌──┴──┐
   HIT   MISS
    │      │
    │      ▼
    │     LLM
    │      │
    │      ▼
    └──► Cache
```

Caching will only be introduced when there is a clearly defined use case.

---

# 22. Idempotency

LLM requests may be expensive and external calls may be retried.

The service should eventually support idempotent processing.

Possible logical identity:

```text
jobId
+
promptVersion
+
inputHash
```

This prevents unnecessary repeated LLM calls.

Example:

```text
Request
   │
   ▼
inputHash
   │
   ▼
Already processed?
   │
 ┌─┴─┐
YES  NO
 │    │
 ▼    ▼
Reuse LLM call
result
```

---

# 23. Messaging and Event-Driven Architecture

Messaging will be introduced after the synchronous system is stable.

Possible technologies:

- RabbitMQ
- Kafka
- AWS SQS/SNS

The project will use messaging to learn:

- asynchronous processing
- eventual consistency
- retries
- dead-letter queues
- idempotency
- message ordering
- backpressure
- independent scaling

Example future architecture:

```text
Skill Service
      │
      ▼
JobProcessedEvent
      │
      ▼
 Message Broker
      │
      ├───────────────┐
      ▼               ▼
Similarity Worker   Search Indexer
      │               │
      ▼               ▼
 OpenSearch        OpenSearch
```

---

# 24. Resilience

External LLM providers are unreliable dependencies and must not be treated as guaranteed.

The service will eventually implement:

- timeouts
- retries
- exponential backoff
- circuit breakers
- bulkheads
- rate limiting

Resilience4j is the expected library for these capabilities.

Example:

```text
Spring Boot
     │
     ▼
LLM Provider
     │
     ├── timeout
     ├── retry
     ├── rate limit
     └── circuit breaker
```

Retries must be used carefully because LLM calls may have costs and side effects.

---

# 25. Concurrency

The project will be used to explore Java concurrency.

Relevant technologies:

- ExecutorService
- virtual threads
- CompletableFuture
- Semaphore
- Atomic classes
- structured/concurrent task patterns where appropriate

For example, if many jobs must be processed:

```text
500 jobs
   │
   ▼
Virtual Threads
   │
   ▼
Semaphore(10)
   │
   ▼
10 concurrent LLM requests
```

Virtual threads do not remove external service limits.

Concurrency will therefore be controlled independently from the number of available threads.

---

# 26. Observability

The application will use Spring Boot Actuator.

Initial capabilities:

```text
/actuator/health
/actuator/info
/actuator/metrics
```

Micrometer will be used for metrics.

Future observability:

```text
OpenTelemetry
     │
     ├── traces
     ├── metrics
     └── logs
```

An important objective is to be able to observe the complete request:

```text
POST /skills/extract
       │
       ├── DB lookup       10ms
       ├── similarity      35ms
       ├── Anthropic     1240ms
       ├── Mongo save       8ms
       └── total         1300ms
```

---

# 27. Logging

Application logging will use SLF4J/Logback through Spring Boot's standard logging infrastructure.

Sensitive information must not be logged.

In particular, the following must never be logged in production:

- API keys
- passwords
- secrets
- authentication tokens
- unnecessary personal data

LLM prompts and responses may contain sensitive job information and therefore must be handled carefully.

Development logging may be more verbose, but production logging should remain structured and controlled.

---

# 28. Configuration

Configuration will be externalized.

Expected profiles:

```text
local
docker
test
aws
```

Example:

```text
application.yml
application-local.yml
application-docker.yml
application-test.yml
application-aws.yml
```

Secrets must come from environment variables or a secret-management mechanism.

Example:

```yaml
anthropic:
  api-key: ${ANTHROPIC_API_KEY}
```

Never commit credentials to source control.

---

# 29. Docker

The application will be containerized.

Initial local environment:

```text
Docker Compose

├── skill-service
├── mariadb
└── mongodb
```

Later:

```text
├── skill-service
├── similarity-service
├── mariadb
├── mongodb
├── redis
├── opensearch
└── message-broker
```

Components will only be added when needed by a project phase.

---

# 30. Local Development

The application must be runnable in Windows without requiring AWS.

Initial options:

```text
Windows
   │
   ├── Java
   ├── Maven
   └── MariaDB/MongoDB
```

and:

```text
Windows
   │
   ▼
Docker Compose
   │
   ├── Spring Boot
   ├── MariaDB
   └── MongoDB
```

Docker Compose will eventually become the preferred reproducible environment.

---

# 31. Testing Strategy

Testing will be divided into several levels.

## Unit tests

Use:

- JUnit
- Mockito

Examples:

```text
SkillExtractionService
AnthropicResponseParser
domain logic
validation logic
```

Unit tests should not require databases or external services.

---

## Integration tests

Use:

```text
@SpringBootTest
```

and Testcontainers.

Containers may include:

```text
MariaDB
MongoDB
Redis
OpenSearch
```

depending on the test.

This allows integration tests to run against real infrastructure implementations instead of mocks.

---

## Architecture tests

Architecture tests may eventually verify boundaries such as:

```text
domain
  cannot depend on
infrastructure
```

and:

```text
application
  cannot directly instantiate
LLM implementations
```

ArchUnit may be introduced for this purpose.

---

# 32. Database Testing

Integration tests should preferably use Testcontainers rather than an in-memory replacement when testing JPA/database behavior.

For example:

```text
JUnit
  │
  ▼
Testcontainers
  │
  ├── MariaDB
  └── MongoDB
```

This avoids differences between an in-memory database and the actual production-style database engine.

---

# 33. API Versioning

The API will initially use:

```text
/api/v1
```

Example:

```text
POST /api/v1/skills/extract
```

Breaking API changes should result in a new version.

---

# 34. Health and Readiness

The application will distinguish conceptually between:

```text
Liveness
```

and:

```text
Readiness
```

A service being alive does not necessarily mean that it is ready to process requests.

Future Kubernetes deployment will use these concepts for probes.

---

# 35. Kubernetes

Kubernetes will be introduced only after Docker deployment is stable.

The local environment will use WSL.

The expected progression is:

```text
Docker
   ↓
Docker Compose
   ↓
Kubernetes / WSL
   ↓
AWS Kubernetes
```

Kubernetes concepts to explore:

- Deployments
- Services
- ConfigMaps
- Secrets
- Configurations
- Liveness probes
- Readiness probes
- Horizontal Pod Autoscaling
- resource requests/limits
- rolling deployments
- service discovery
- persistent volumes

---

# 36. AWS

AWS deployment will be introduced after the local architecture is stable.

Possible AWS components to evaluate:

```text
Spring Boot
   │
   ├── ECS/Fargate
   │
   └── EKS
```

Relational database:

```text
RDS
```

Search:

```text
OpenSearch
```

Messaging:

```text
SQS / SNS
```

Secrets:

```text
AWS Secrets Manager
```

Observability:

```text
CloudWatch
```

The exact AWS architecture will be selected based on free-tier availability, cost and learning objectives.

---

# 37. Source of Truth

Different technologies have different responsibilities.

```text
MariaDB
    ↓
Transactional source of truth
```

```text
MongoDB
    ↓
LLM execution history / documents
```

```text
OpenSearch
    ↓
Search and vector index
```

```text
Redis
    ↓
Cache / temporary state
```

```text
Message Broker
    ↓
Asynchronous communication
```

No secondary system should accidentally become the authoritative source of business data.

---

# 38. Evolution Towards Microservices

The project will evolve incrementally.

Initial:

```text
┌───────────────────────────────┐
│       Spring Boot App         │
│                               │
│ REST                          │
│ Application                   │
│ Domain                        │
│ LLM                           │
│ Similarity                    │
│ Persistence                   │
└───────────────────────────────┘
```

Later:

```text
             ┌───────────────┐
             │ Skill Service │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │  Similarity   │
             │    Service    │
             └───────────────┘
```

Later still:

```text
                API Gateway
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Skill Service  Similarity     Search/Index
                   Service         Service
       │             │             │
       └─────────────┼─────────────┘
                     │
                Message Broker
```

Services will be extracted only when there is a meaningful boundary.

---

# 39. Development Stages

## Phase 1 — Spring Boot Foundation

Objectives:

- create Spring Boot project
- Maven configuration
- package structure
- Spring MVC
- REST Controller
- DTOs
- Bean Validation
- global exception handling
- configuration
- profiles
- Actuator

Expected endpoint:

```text
GET /api/v1/health
```

---

## Phase 2 — Domain and Application Layer

Implement:

```text
JobDescription
Skill
SkillExtraction
SkillExtractionService
```

Introduce ports:

```text
LLMProvider
SkillRepository
PromptHistoryRepository
SimilarityProvider
```

The application layer must remain independent of infrastructure implementations.

---

## Phase 3 — MariaDB / JPA / Hibernate

Implement:

- JPA entities
- Hibernate
- Spring Data JPA
- MariaDB
- repository adapters
- transactions

Generate and review initial SQL.

---

## Phase 4 — Flyway

Introduce:

```text
V1__initial_schema.sql
```

Configure:

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

From this point forward, database evolution is handled through Flyway migrations.

---

## Phase 5 — MongoDB

Implement:

```text
PromptExecutionDocument
PromptHistoryRepository
```

Store:

- prompt
- provider
- model
- response
- timestamp
- latency
- status
- token usage
- prompt version

---

## Phase 6 — Anthropic Provider

Implement:

```text
LLMProvider
    ↓
AnthropicLLMProvider
    ↓
AnthropicClient
```

Use Spring's HTTP client facilities.

Use Jackson for JSON serialization/deserialization.

Implement robust error handling.

---

## Phase 7 — Docker

Create:

```text
Dockerfile
docker-compose.yml
```

Run:

```text
skill-service
mariadb
mongodb
```

Verify that the entire system works without installing databases directly on the host.

---

## Phase 8 — Testing

Introduce:

```text
JUnit
Mockito
Spring Boot Test
Testcontainers
```

Create:

```text
unit tests
integration tests
API tests
persistence tests
```

---

## Phase 9 — Resilience

Introduce:

```text
timeouts
retries
backoff
circuit breakers
bulkheads
rate limiting
```

Evaluate behavior under:

```text
Anthropic unavailable
Anthropic slow
HTTP 429
HTTP 500
network failure
```

---

## Phase 10 — Concurrency

Experiment with:

```text
ExecutorService
virtual threads
CompletableFuture
Semaphore
```

Process batches of job descriptions while respecting external API limits.

---

## Phase 11 — Similarity

First implement similarity inside the monolith.

Introduce:

```text
SimilarityProvider
```

and a local embedding implementation.

Measure:

- latency
- memory
- CPU
- similarity accuracy
- cost savings

---

## Phase 12 — Similarity Microservice

Extract the similarity component into:

```text
similarity-service
```

Communicate using HTTP initially.

Introduce:

```text
timeouts
retries
circuit breakers
service configuration
```

---

## Phase 13 — Redis

Evaluate:

- extraction cache
- similarity cache
- idempotency
- rate limiting

Measure whether caching actually improves the system.

---

## Phase 14 — OpenSearch / Elasticsearch

Introduce:

- full-text search
- filtering
- vector search
- similarity queries

Keep MariaDB as the transactional source of truth.

---

## Phase 15 — Messaging

Introduce a message broker.

Evaluate:

```text
RabbitMQ
Kafka
AWS SQS/SNS
```

Implement asynchronous processing.

Explore:

- events
- retries
- dead-letter queues
- idempotency
- eventual consistency

---

## Phase 16 — Observability

Introduce:

```text
Micrometer
OpenTelemetry
```

Implement:

- metrics
- distributed tracing
- structured logs
- correlation/request IDs

Measure the latency of:

```text
API
DB
Mongo
similarity
LLM
messaging
```

---

## Phase 17 — Kubernetes / WSL

Deploy locally using Kubernetes.

Introduce:

- Deployment
- Service
- ConfigMap
- Secret
- probes
- resource limits
- scaling
- rolling deployments

---

## Phase 18 — AWS

Evaluate AWS deployment options.

Potential architecture:

```text
                  AWS
                   │
             ┌─────┴─────┐
             │            │
          ECS/EKS     Load Balancer
             │
       ┌─────┴─────────────┐
       │                   │
 Skill Service       Similarity Service
       │                   │
       ▼                   ▼
      RDS              ML Runtime
       │
       ├───────────┐
       ▼           ▼
   Mongo/Atlas   OpenSearch
       │
       ▼
    SQS/SNS
```

AWS services will be selected according to cost, free-tier constraints and learning objectives.

---

# 40. Non-Goals

The project intentionally will not attempt to introduce every technology immediately.

Examples:

- No Kubernetes before Docker works.
- No microservices before the modular monolith works.
- No Kafka simply because it is popular.
- No Redis without a concrete caching/state use case.
- No Elasticsearch as a replacement for the relational database.
- No asynchronous processing everywhere.
- No abstraction whose only purpose is to hide a concrete implementation without a realistic possibility of change.

Every additional component should have a documented reason.

---

# 41. Technology Stack

Initial stack:

```text
Java
Spring Boot
Spring MVC
Spring Data JPA
Hibernate
MariaDB
Spring Data MongoDB
MongoDB
Jackson
Flyway
Maven
JUnit
Mockito
Testcontainers
Docker
Docker Compose
```

Future stack:

```text
Redis
OpenSearch / Elasticsearch
Resilience4j
Micrometer
OpenTelemetry
RabbitMQ / Kafka / AWS SQS
Kubernetes
AWS
Local embedding model
```

---

# 42. Main Architectural Objective

The central objective of this project is not to maximize the number of technologies.

The objective is to build a system that can evolve from:

```text
simple Spring Boot application
```

to:

```text
modular monolith
```

to:

```text
distributed system
```

without unnecessarily rewriting the business logic.

The most important boundaries are therefore:

```text
API
  ↓
Application
  ↓
Domain / Ports
  ↓
Infrastructure Adapters
```

and:

```text
LLMProvider
SimilarityProvider
SkillRepository
PromptHistoryRepository
```

These interfaces represent capabilities that may have multiple implementations.

---

# 43. Definition of Done

The project will be considered production-style when it can:

- expose a versioned REST API
- validate requests
- extract skills through an abstract LLM provider
- persist skills using JPA/Hibernate
- manage schema changes with Flyway
- persist LLM execution history in MongoDB
- run entirely using Docker Compose
- run automated unit and integration tests
- use Testcontainers
- handle external-service failures
- expose health and metrics endpoints
- support structured logging
- control LLM concurrency
- cache reusable results when appropriate
- detect similar jobs without an external LLM call
- perform vector search
- process asynchronous events
- run in Kubernetes
- be deployable to AWS
- replace infrastructure components without modifying the core application logic

---

# 44. Guiding Principle

The project should continuously answer one question:

> **If this component changes tomorrow, how much of the application do I have to rewrite?**

Examples:

```text
Anthropic → OpenAI
MariaDB → PostgreSQL
Local similarity → remote similarity service
Docker → Kubernetes
Local deployment → AWS
Synchronous → asynchronous processing
```

The architecture should make these changes possible without unnecessarily changing the business/application layer.

The goal is not to make everything abstract.

The goal is to make **meaningful architectural boundaries explicit**.