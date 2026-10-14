-- =====================================================================
-- ROSELET JEWELS: Unified Omni-Platform Database Schema
-- Compatible with PostgreSQL (Supabase) and local SQLite fallback
-- =====================================================================

-- 1. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    purchase_cost NUMERIC(10, 2) DEFAULT 0.00,
    mrp NUMERIC(10, 2) DEFAULT 0.00,
    selling_price NUMERIC(10, 2) DEFAULT 0.00,
    stock_qty INTEGER DEFAULT 10,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100) DEFAULT 'Kerala',
    pincode VARCHAR(20),
    source VARCHAR(50) DEFAULT 'Storefront',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ORDERS TABLE
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    items_json TEXT NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    cgst NUMERIC(10, 2) DEFAULT 0.00,
    sgst NUMERIC(10, 2) DEFAULT 0.00,
    igst NUMERIC(10, 2) DEFAULT 0.00,
    shipping_charge NUMERIC(10, 2) DEFAULT 0.00,
    net_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    order_status VARCHAR(50) DEFAULT 'WhatsApp_Pending',
    payment_mode VARCHAR(50) DEFAULT 'UPI / GPay',
    tracking_no VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. ACCOUNTING LEDGER TABLE
CREATE TABLE IF NOT EXISTS accounting_ledger (
    id SERIAL PRIMARY KEY,
    txn_date DATE NOT NULL,
    voucher_type VARCHAR(50) NOT NULL, -- 'Sales', 'Purchase', 'Expense', 'Receipt'
    account_head VARCHAR(100) NOT NULL,
    reference_no VARCHAR(100),
    debit NUMERIC(10, 2) DEFAULT 0.00,
    credit NUMERIC(10, 2) DEFAULT 0.00,
    narration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for high-speed queries
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_cat ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_orders_order_no ON orders(order_no);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_ledger_head ON accounting_ledger(account_head);
