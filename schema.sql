-- schema.sql

-- Drop tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS invoice_items, invoices, order_items, orders, enquiry_items, enquiries, customers, users CASCADE;

-- Users Table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers Table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    unique_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20),
    gst_no VARCHAR(15),
    pan_no VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Enquiries Table
CREATE TABLE enquiries (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    enq_number VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Enquiry Items Table
CREATE TABLE enquiry_items (
    id SERIAL PRIMARY KEY,
    enquiry_id INTEGER REFERENCES enquiries(id) ON DELETE CASCADE,
    drawing_number VARCHAR(255),
    part_number VARCHAR(255),
    part_revision_number VARCHAR(50),
    material_type VARCHAR(100),
    material_specification VARCHAR(100),
    with_material BOOLEAN,
    unit_price NUMERIC(10, 2),
    quantity INTEGER,
    total_price NUMERIC(12, 2) GENERATED ALWAYS AS (unit_price * quantity) STORED,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    po_number VARCHAR(255) NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount NUMERIC(12, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Order Items Table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    enquiry_item_id INTEGER REFERENCES enquiry_items(id) ON DELETE SET NULL,
    wo_number VARCHAR(50) UNIQUE NOT NULL, -- Work Order Number
    drawing_number VARCHAR(255),
    part_number VARCHAR(255),
    material_type VARCHAR(100),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    total_price NUMERIC(12, 2) GENERATED ALWAYS AS (unit_price * quantity) STORED,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Invoices Table
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    dc_number VARCHAR(100),
    dc_date DATE,
    po_number VARCHAR(255),
    po_date DATE,
    gst_rate NUMERIC(5, 2),
    sub_total NUMERIC(12, 2),
    gst_amount NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    payment_terms VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP
);

-- Invoice Items Table
CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
    order_item_id INTEGER REFERENCES order_items(id) ON DELETE SET NULL,
    work_order_number VARCHAR(50),
    hsn_number VARCHAR(50)
);