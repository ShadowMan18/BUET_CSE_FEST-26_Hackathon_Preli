## 1. locations

Stores all warehouse locations used by the logistics network.

| COLUMN_NAME   | DATA_TYPE     | NULLABLE | DATA_DEFAULT  | CONSTRAINTS                          | COMMENTS 
|---------------|---------------|----------|---------------|--------------------------------------|----------
| id            | SERIAL        | No       | auto          | PRIMARY KEY                          |Primary key of location table
| name          | VARCHAR(100)  | No       | null          |     -                                |Warehouse Name
| cold_capacity | INTEGER       | No       | null          | CHECK (cold_capacity ≥ 0)            |Cold storage capacity of the location.

### Purpose
Represents warehouses that store temperature-sensitive goods.  
Cold capacity is used to ensure storage limits are not exceeded.

---

## 2. products

Stores all products that can be transported in the network.

| COLUMN_NAME   | DATA_TYPE     | NULLABLE | DATA_DEFAULT | CONSTRAINTS               | COMMENTS 
|---------------|---------------|----------|--------------|---------------------------|----------
| id            | SERIAL        | No       | auto         | PRIMARY KEY               | Primary key of products table. 
| name          | VARCHAR(100)  | No       | null         | —                         | Name of the product. 
| required_temp | INTEGER       | No       | null         | —                         | Required temperature for this product. 

### Purpose
Defines what products exist and their temperature requirements.  
Used to validate route compatibility.

---

## 3. clients

Stores delivery destination entities such as hospitals or retailers.

| COLUMN_NAME| DATA_TYPE    | NULLABLE | DATA_DEFAULT | CONSTRAINTS  | COMMENTS
|------------|--------------|----------|--------------|--------------|----------
| id         | SERIAL       | No       | auto         | PRIMARY KEY  | Primary key of clients table. 
| name       | VARCHAR(100) | No       | null         | —            | Name of the client. 
| type       | VARCHAR(50)  | No       | null         | —            | Type of client (Hospital, Retailer, etc.). 

### Purpose
Represents clients who receive deliveries.

---

## 4. routes

Stores transportation routes between locations.

| COLUMN_NAME   | DATA_TYPE | NULLABLE | DATA_DEFAULT | CONSTRAINTS | COMMENTS 
|---------------|-----------|----------|--------------|-------------|----------
| id            | SERIAL    | No       | auto         | PRIMARY KEY | Primary key of routes table. 
| from_location | INTEGER   | No       | null         | FK → locations(id) | Source location of the route. 
| to_location   | INTEGER   | No       | null         | FK → locations(id) | Destination location of the route. 
| max_capacity  | INTEGER   | No       | null         | CHECK (max_capacity ≥ 0) | Maximum transport capacity of the route. 
| min_temp      | INTEGER   | No       | null         | CHECK (min_temp ≤ max_temp) | Minimum supported temperature. 
| max_temp      | INTEGER   | No       | null         | CHECK (max_temp ≥ min_temp) | Maximum supported temperature. 

### Purpose
Defines how goods move between locations.  
Used to ensure both **capacity limits** and **temperature constraints** are respected.

---

## 5. inventory

Stores available product quantities at each location.

| COLUMN_NAME | DATA_TYPE | NULLABLE | DATA_DEFAULT | CONSTRAINTS | COMMENTS 
|-------------|-----------|----------|--------------|-------------|----------
| id          | SERIAL    | No       | auto         | PRIMARY KEY | Primary key of inventory table. 
| location_id | INTEGER   | No       | null         | FK → locations(id), UNIQUE(location_id, product_id) | Location storing the product. 
| product_id  | INTEGER   | No       | null         | FK → products(id), UNIQUE(location_id, product_id) | Product stored at the location. 
| quantity    | INTEGER   | No       | null         | CHECK (quantity ≥ 0) | Available quantity of the product. 

### Purpose
Tracks how much of each product is available at each location.  
Ensures no duplicate inventory rows for the same location-product pair.

---

## 6. delivery_requests

Stores delivery requests submitted by clients.

| COLUMN_NAME| DATA_TYPE    | NULLABLE | DATA_DEFAULT |       CONSTRAINTS             | COMMENTS 
|------------|--------------|----------|--------------|-------------------------------|----------
| id         | SERIAL       | No       | auto         | PRIMARY KEY                   | Primary key of delivery_requests table. 
| product_id | INTEGER      | No       | null         | FK → products(id)             | Requested product. 
| route_id   | INTEGER      | No       | null         | FK → routes(id)               | Route used for delivery. 
| client_id  | INTEGER      | No       | null         | FK → clients(id)              | Client requesting the delivery. 
| quantity   | INTEGER      | No       | null         | CHECK (quantity > 0)          | Requested quantity. 
| status     | VARCHAR(20)  | No       | 'PENDING'    | CHECK (status IN ('PENDING',  | Current request status.
|            |              |          |              | 'APPROVED','REJECTED'))       |  

### Purpose
Represents delivery plans that must be validated before execution.  
Requests are approved or rejected based on capacity and temperature checks.

---

## 7. approved_shipments

Stores approved delivery requests.

| COLUMN_NAME | DATA_TYPE | NULLABLE | DATA_DEFAULT | CONSTRAINTS                         | COMMENTS 
|-------------|-----------|----------|--------------|-------------------------------------|----------
| id          | SERIAL    | No       | auto         | PRIMARY KEY                         | Primary key of approved_shipments table. 
| request_id  | INTEGER   | No       | null         | FK → delivery_requests(id), UNIQUE  | Approved delivery request. 
| approved_at | TIMESTAMP | No       | NOW()        | —                                   | Time when the request was approved. 

### Purpose
Confirms that a delivery request has passed validation.  
Guarantees that each request can be approved **only once**.

---
