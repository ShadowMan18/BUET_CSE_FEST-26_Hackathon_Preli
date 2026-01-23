CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cold_capacity INTEGER NOT NULL CHECK (cold_capacity >= 0)
);


CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    required_temp INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    from_location INTEGER NOT NULL,
    to_location INTEGER NOT NULL,
    max_capacity INTEGER NOT NULL CHECK (max_capacity >= 0),
    min_temp INTEGER NOT NULL,
    max_temp INTEGER NOT NULL,
    CONSTRAINT fk_route_from FOREIGN KEY (from_location) REFERENCES locations(id),
    CONSTRAINT fk_route_to FOREIGN KEY (to_location) REFERENCES locations(id),
    CONSTRAINT chk_temp_range CHECK (min_temp <= max_temp)
);


CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    CONSTRAINT fk_inventory_location FOREIGN KEY (location_id) REFERENCES locations(id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT uq_inventory UNIQUE (location_id, product_id)
);


CREATE TABLE IF NOT EXISTS delivery_requests (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','APPROVED','REJECTED')),
    CONSTRAINT fk_request_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_request_route FOREIGN KEY (route_id) REFERENCES routes(id),
    CONSTRAINT fk_request_client FOREIGN KEY (client_id) REFERENCES clients(id)
);


CREATE TABLE IF NOT EXISTS approved_shipments (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL UNIQUE,
    approved_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_approved_request FOREIGN KEY (request_id) REFERENCES delivery_requests(id)
);
