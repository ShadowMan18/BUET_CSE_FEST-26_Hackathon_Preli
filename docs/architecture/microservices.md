# FrostByte Microservices Architecture

## 1. Architectural Overview
To ensure the FrostByte platform is resilient, scalable, and capable of handling high-concurrency logistics planning, the system is designed as a distributed set of microservices.

This architecture follows **Domain-Driven Design (DDD)** principles, separating the static physical network from the dynamic flow of demands and the computational intensity of validation.

### System Diagram
`[Client API Gateway]` ➔ `[Microservices]` ➔ `[Database Shards]`

---

## 2. Service Definitions

### A. Network Infrastructure Service 
**Role:** The "Source of Truth" for the physical world.
**Responsibilities:**
* Manages the static graph of the logistics network.
* Handles CRUD operations for **Locations**, **Products**, and **Routes**.
* Manages **Storage Units** capacities within warehouses.
* **Why Microservice?** Infrastructure data is read-heavy (cached frequently) and changes rarely. Isolating it prevents read-operations from being blocked by heavy write-operations in the Demand service.

**Owned Database Tables:**
* `locations`
* `products`
* `storage_units`
* `routes`

**API Ownership:**
* `POST /locations`, `GET /locations`
* `POST /products`, `GET /products`
* `POST /storage-units`, `GET /storage-units`
* `POST /routes`, `GET /routes`
* `GET /network/summary`

---

### B. Demand Management Service 
**Role:** The Transactional Engine.
**Responsibilities:**
* Captures and manages daily **Delivery Demands**.
* Acts as the buffer for high-volume incoming orders.
* Ensures data consistency for client commitments before they are processed.
* **Why Microservice?** This service handles high-velocity writes. Decoupling it allows us to scale ingestion independently of the validation logic.

**Owned Database Tables:**
* `demands`

**API Ownership:**
* `POST /demands`
* `GET /demands`

---

### C. Validation & Feasibility Engine 
**Role:** The Stateless "Brain".
**Responsibilities:**
* Performs complex constraint satisfaction algorithms.
* Checks **Capacity Constraints** (Route limits, Storage limits).
* Checks **Temperature Constraints** (Product vs. Storage compatibility).
* **Why Microservice?** Validation is CPU-intensive. By isolating this into a stateless engine, we can horizontally scale the "computing power" without needing to duplicate the database.

**Dependencies:**
* Fetches graph data from **Network Infrastructure Service**.
* Fetches order batches from **Demand Management Service**.

**API Ownership:**
* `POST /temps/validate`
* `POST /network/validate`

---

## 3. Communication Patterns

### Synchronous (REST/gRPC)
* Used for the `validate` endpoints where the client expects an immediate "Go/No-Go" decision.
* **Flow:** `Validation Service` ➔ calls `Network Service` (to get limits) ➔ computes result ➔ returns response.

### Asynchronous (Event Bus - Future Scope)
* In a production environment, `Demands` would be published to a message queue (e.g., Kafka/RabbitMQ) for background processing, decoupling the ingestion from the validation entirely.