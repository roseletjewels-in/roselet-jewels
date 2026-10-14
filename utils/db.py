"""
Database Connection & Abstraction Layer for Roselet Jewels.
Seamlessly switches between Supabase Cloud PostgreSQL and local SQLite fallback.
"""

import os
import json
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Any, Optional

# Attempt to load streamlit secrets or environment variables
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    from supabase import create_client, Client
    SUPABASE_LIB_AVAILABLE = True
except ImportError:
    SUPABASE_LIB_AVAILABLE = False
    Client = None

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_roselet.db")
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Global client cache
_supabase_client: Optional[Any] = None
_db_mode: str = "sqlite" # 'supabase' or 'sqlite'
_db_initialized: bool = False


def _get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from Streamlit secrets or OS env."""
    if STREAMLIT_AVAILABLE and hasattr(st, "secrets"):
        try:
            if key in st.secrets:
                return str(st.secrets[key])
            # Check nested dictionary if present
            if "supabase" in st.secrets and key in st.secrets["supabase"]:
                return str(st.secrets["supabase"][key])
        except Exception:
            pass
    return os.environ.get(key, default)


def get_supabase_client() -> Optional[Any]:
    """Initialize or return existing Supabase client if configured."""
    global _supabase_client, _db_mode
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_LIB_AVAILABLE:
        _db_mode = "sqlite"
        return None

    sb_url = _get_secret("SUPABASE_URL")
    sb_key = _get_secret("SUPABASE_KEY") or _get_secret("SUPABASE_ANON_KEY")

    if sb_url and sb_key and not sb_url.startswith("your_"):
        try:
            client = create_client(sb_url, sb_key)
            # Quick ping to verify connectivity
            test = client.table("products").select("id").limit(1).execute()
            _supabase_client = client
            _db_mode = "supabase"
            return _supabase_client
        except Exception as e:
            # Fall back to sqlite if Supabase is unreachable
            _db_mode = "sqlite"
            return None
    _db_mode = "sqlite"
    return None


def get_db_status() -> Dict[str, Any]:
    """Returns database backend engine and connection info."""
    client = get_supabase_client()
    if client is not None and _db_mode == "supabase":
        return {
            "engine": "Supabase (Cloud PostgreSQL)",
            "connected": True,
            "mode": "supabase",
            "url": _get_secret("SUPABASE_URL", "")[:25] + "..."
        }
    return {
        "engine": "Local SQLite Database",
        "connected": True,
        "mode": "sqlite",
        "path": DB_PATH
    }


def get_sqlite_conn():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create local SQLite tables and populate seed data if empty."""
    global _db_initialized
    if _db_initialized:
        return

    # Always ensure SQLite schema exists as fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        purchase_cost REAL DEFAULT 0.00,
        mrp REAL DEFAULT 0.00,
        selling_price REAL DEFAULT 0.00,
        stock_qty INTEGER DEFAULT 10,
        image_url TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        address TEXT,
        city TEXT,
        state TEXT DEFAULT 'Kerala',
        pincode TEXT,
        source TEXT DEFAULT 'Storefront',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE NOT NULL,
        customer_id INTEGER,
        items_json TEXT NOT NULL,
        subtotal REAL NOT NULL DEFAULT 0.00,
        cgst REAL DEFAULT 0.00,
        sgst REAL DEFAULT 0.00,
        igst REAL DEFAULT 0.00,
        shipping_charge REAL DEFAULT 0.00,
        net_total REAL NOT NULL DEFAULT 0.00,
        order_status TEXT DEFAULT 'WhatsApp_Pending',
        payment_mode TEXT DEFAULT 'UPI / GPay',
        tracking_no TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounting_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        txn_date TEXT NOT NULL,
        voucher_type TEXT NOT NULL,
        account_head TEXT NOT NULL,
        reference_no TEXT,
        debit REAL DEFAULT 0.00,
        credit REAL DEFAULT 0.00,
        narration TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_products = [
            (
                "RJ-NK-001",
                "Royal Kempu Temple Choker Necklace",
                "Necklaces",
                650.00,
                2499.00,
                1499.00,
                15,
                "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-BG-002",
                "Palakka Traditional Glass Bangles Set",
                "Bangles",
                420.00,
                1899.00,
                999.00,
                20,
                "https://images.unsplash.com/photo-1611591475152-473523dd665e?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-ER-003",
                "Kundan Pearl Jhumkas with Ruby Accents",
                "Earrings",
                310.00,
                1499.00,
                799.00,
                25,
                "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-RG-004",
                "Victorian Emerald Solitaire Statement Ring",
                "Rings",
                210.00,
                999.00,
                599.00,
                18,
                "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-BS-005",
                "Imperial Nagas Bridal Haram & Choker Set",
                "Bridal Sets",
                2200.00,
                8999.00,
                4999.00,
                6,
                "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-AT-006",
                "Dainty 18K PVD Waterproof Clover Chain",
                "Anti-Tarnish",
                340.00,
                1799.00,
                899.00,
                30,
                "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-NK-007",
                "Mulla Mottu Kerala Jasmine Bud Haram",
                "Necklaces",
                800.00,
                3299.00,
                1899.00,
                12,
                "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?auto=format&fit=crop&w=800&q=80",
                1
            ),
            (
                "RJ-AT-008",
                "Twisted Herringbone Waterproof Bracelet",
                "Anti-Tarnish",
                280.00,
                1599.00,
                749.00,
                22,
                "https://images.unsplash.com/photo-1611591475152-473523dd665e?auto=format&fit=crop&w=800&q=80",
                1
            ),
        ]

        cursor.executemany("""
        INSERT INTO products (sku, name, category, purchase_cost, mrp, selling_price, stock_qty, image_url, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_products)

        # Seed initial sample customer & order for demonstration
        cursor.execute("""
        INSERT INTO customers (phone, full_name, address, city, state, pincode, source)
        VALUES ('9847012345', 'Ananya Nair', 'Flat 4B, Skyvue Apartments, Panampilly Nagar', 'Kochi', 'Kerala', '682036', 'Instagram')
        """)
        cust_id = cursor.lastrowid

        sample_items = json.dumps([
            {
                "id": 1,
                "sku": "RJ-NK-001",
                "name": "Royal Kempu Temple Choker Necklace",
                "qty": 1,
                "price": 1499.00,
                "hsn": "7117"
            }
        ])

        cursor.execute("""
        INSERT INTO orders (order_no, customer_id, items_json, subtotal, cgst, sgst, igst, shipping_charge, net_total, order_status, payment_mode, tracking_no)
        VALUES ('RJ-1001', ?, ?, 1455.34, 21.83, 21.83, 0.00, 0.00, 1499.00, 'Confirmed_Billed', 'UPI / GPay', 'BLUEDART-KL987654')
        """, (cust_id, sample_items))

        # Seed initial accounting ledger entries
        today_str = date.today().isoformat()
        cursor.execute("""
        INSERT INTO accounting_ledger (txn_date, voucher_type, account_head, reference_no, debit, credit, narration)
        VALUES 
        (?, 'Sales', 'Sales Revenue', 'RJ-1001', 0.00, 1499.00, 'Order RJ-1001 paid via UPI - Ananya Nair'),
        (?, 'Receipt', 'Bank Account (UPI)', 'RJ-1001', 1499.00, 0.00, 'Payment received for Order RJ-1001'),
        (?, 'Purchase', 'Inventory Purchase', 'PO-2026-01', 15000.00, 0.00, 'Opening inventory stock lot - Anti-tarnish & temple ornaments'),
        (?, 'Expense', 'Packaging Materials', 'EXP-01', 1850.00, 0.00, 'Velvet gift boxes and courier bubble mailers')
        """, (today_str, today_str, today_str, today_str))

        conn.commit()

    conn.close()
    _db_initialized = True


# =====================================================================
# PRODUCT CRUD OPERATIONS
# =====================================================================

def get_products(category: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieve products with optional category and active filters."""
    init_db()
    client = get_supabase_client()

    if client and _db_mode == "supabase":
        try:
            query = client.table("products").select("*")
            if active_only:
                query = query.eq("is_active", True)
            if category and category != "All":
                query = query.eq("category", category)
            query = query.order("id", desc=False)
            res = query.execute()
            return res.data or []
        except Exception as e:
            pass # fallback to sqlite

    # SQLite
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if active_only:
        query += " AND is_active = 1"
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            res = client.table("products").select("*").eq("id", product_id).single().execute()
            return res.data
        except Exception:
            pass

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(data: Dict[str, Any]) -> int:
    init_db()
    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            res = client.table("products").insert(data).execute()
            if res.data:
                return res.data[0].get("id", 1)
        except Exception:
            pass

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (sku, name, category, purchase_cost, mrp, selling_price, stock_qty, image_url, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("sku"),
        data.get("name"),
        data.get("category"),
        data.get("purchase_cost", 0.0),
        data.get("mrp", 0.0),
        data.get("selling_price", 0.0),
        data.get("stock_qty", 10),
        data.get("image_url", ""),
        1 if data.get("is_active", True) else 0
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_product(product_id: int, data: Dict[str, Any]) -> bool:
    init_db()
    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            client.table("products").update(data).eq("id", product_id).execute()
            return True
        except Exception:
            pass

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(product_id)

    cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return True


def deduct_stock(product_id: int, qty: int) -> bool:
    """Deducts stock when an order is created."""
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock_qty = MAX(0, stock_qty - ?) WHERE id = ?", (qty, product_id))
    conn.commit()
    conn.close()

    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            prod = get_product_by_id(product_id)
            if prod:
                new_qty = max(0, int(prod.get("stock_qty", 0)) - qty)
                client.table("products").update({"stock_qty": new_qty}).eq("id", product_id).execute()
        except Exception:
            pass
    return True


# =====================================================================
# CUSTOMER OPERATIONS
# =====================================================================

def upsert_customer(phone: str, full_name: str, address: str, city: str, state: str, pincode: str, source: str = "Storefront") -> int:
    """Creates or updates customer profile and returns customer ID."""
    init_db()
    client = get_supabase_client()
    phone_clean = phone.strip().replace(" ", "").replace("-", "")

    if client and _db_mode == "supabase":
        try:
            existing = client.table("customers").select("id").eq("phone", phone_clean).execute()
            cust_data = {
                "phone": phone_clean,
                "full_name": full_name.strip(),
                "address": address.strip(),
                "city": city.strip(),
                "state": state.strip(),
                "pincode": pincode.strip(),
                "source": source
            }
            if existing.data and len(existing.data) > 0:
                cid = existing.data[0]["id"]
                client.table("customers").update(cust_data).eq("id", cid).execute()
                return cid
            else:
                res = client.table("customers").insert(cust_data).execute()
                if res.data:
                    return res.data[0]["id"]
        except Exception:
            pass

    # SQLite
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone_clean,))
    row = cursor.fetchone()

    if row:
        cust_id = row[0]
        cursor.execute("""
        UPDATE customers SET full_name = ?, address = ?, city = ?, state = ?, pincode = ?, source = ?
        WHERE id = ?
        """, (full_name.strip(), address.strip(), city.strip(), state.strip(), pincode.strip(), source, cust_id))
    else:
        cursor.execute("""
        INSERT INTO customers (phone, full_name, address, city, state, pincode, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (phone_clean, full_name.strip(), address.strip(), city.strip(), state.strip(), pincode.strip(), source))
        cust_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return cust_id


def get_customers() -> List[Dict[str, Any]]:
    init_db()
    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            res = client.table("customers").select("*").order("id", desc=True).execute()
            return res.data or []
        except Exception:
            pass

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# =====================================================================
# ORDERS OPERATIONS
# =====================================================================

def get_next_order_no() -> str:
    """Generates sequential order number like RJ-1001, RJ-1002."""
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()
    return f"RJ-{1001 + count}"


def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves order to DB and deducts inventory stock."""
    init_db()
    client = get_supabase_client()

    # Deduct stock for all ordered items
    items = order_data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []

    for item in items:
        pid = item.get("id")
        qty = item.get("qty", 1)
        if pid:
            deduct_stock(pid, qty)

    items_json_str = json.dumps(items) if not isinstance(order_data.get("items_json"), str) else order_data.get("items_json")

    # SQLite
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO orders (
        order_no, customer_id, items_json, subtotal, cgst, sgst, igst, 
        shipping_charge, net_total, order_status, payment_mode, tracking_no
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_data.get("order_no"),
        order_data.get("customer_id"),
        items_json_str,
        order_data.get("subtotal", 0.0),
        order_data.get("cgst", 0.0),
        order_data.get("sgst", 0.0),
        order_data.get("igst", 0.0),
        order_data.get("shipping_charge", 0.0),
        order_data.get("net_total", 0.0),
        order_data.get("order_status", "WhatsApp_Pending"),
        order_data.get("payment_mode", "UPI / GPay"),
        order_data.get("tracking_no", "")
    ))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    # Supabase cloud push
    if client and _db_mode == "supabase":
        try:
            sb_order = {
                "order_no": order_data.get("order_no"),
                "customer_id": order_data.get("customer_id"),
                "items_json": items_json_str,
                "subtotal": float(order_data.get("subtotal", 0.0)),
                "cgst": float(order_data.get("cgst", 0.0)),
                "sgst": float(order_data.get("sgst", 0.0)),
                "igst": float(order_data.get("igst", 0.0)),
                "shipping_charge": float(order_data.get("shipping_charge", 0.0)),
                "net_total": float(order_data.get("net_total", 0.0)),
                "order_status": order_data.get("order_status", "WhatsApp_Pending"),
                "payment_mode": order_data.get("payment_mode", "UPI / GPay"),
                "tracking_no": order_data.get("tracking_no", "")
            }
            client.table("orders").insert(sb_order).execute()
        except Exception:
            pass

    order_data["id"] = order_id
    return order_data


def get_orders(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch orders joined with customer profile."""
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()

    query = """
    SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone, 
           c.city AS customer_city, c.state AS customer_state, c.address AS customer_address, c.pincode AS customer_pincode
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.id
    WHERE 1=1
    """
    params = []
    if status_filter and status_filter != "All":
        query += " AND o.order_status = ?"
        params.append(status_filter)

    query += " ORDER BY o.id DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone, 
           c.city AS customer_city, c.state AS customer_state, c.address AS customer_address, c.pincode AS customer_pincode
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.id
    WHERE o.id = ?
    """, (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_order_status(order_id: int, new_status: str, payment_mode: Optional[str] = None, tracking_no: Optional[str] = None) -> bool:
    """Updates order status, records accounting ledger when Confirmed_Billed."""
    init_db()
    order = get_order_by_id(order_id)
    if not order:
        return False

    conn = get_sqlite_conn()
    cursor = conn.cursor()

    updates = ["order_status = ?"]
    params = [new_status]

    if payment_mode:
        updates.append("payment_mode = ?")
        params.append(payment_mode)
    if tracking_no is not None:
        updates.append("tracking_no = ?")
        params.append(tracking_no)

    params.append(order_id)
    cursor.execute(f"UPDATE orders SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()

    # If billing confirmed and previously not billed, log to accounting ledger!
    if new_status == "Confirmed_Billed" and order.get("order_status") != "Confirmed_Billed":
        net_val = float(order.get("net_total", 0.0))
        order_no = order.get("order_no", f"ORD-{order_id}")
        cust_name = order.get("customer_name", "Valued Customer")
        pmode = payment_mode or order.get("payment_mode", "UPI / GPay")
        today_str = date.today().isoformat()

        # Sales entry
        add_ledger_entry(
            txn_date=today_str,
            voucher_type="Sales",
            account_head="Sales Revenue",
            reference_no=order_no,
            debit=0.0,
            credit=net_val,
            narration=f"Billed order {order_no} ({cust_name}) via {pmode}"
        )

        # Receipt entry
        add_ledger_entry(
            txn_date=today_str,
            voucher_type="Receipt",
            account_head=f"Bank / Cash ({pmode})",
            reference_no=order_no,
            debit=net_val,
            credit=0.0,
            narration=f"Payment received for {order_no}"
        )

    # Sync with Supabase cloud
    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            up_data = {"order_status": new_status}
            if payment_mode:
                up_data["payment_mode"] = payment_mode
            if tracking_no is not None:
                up_data["tracking_no"] = tracking_no
            client.table("orders").update(up_data).eq("id", order_id).execute()
        except Exception:
            pass

    return True


def update_order_tracking(order_id: int, tracking_no: str) -> bool:
    """Updates courier tracking number and sets status to Shipped if appropriate."""
    return update_order_status(order_id, "Shipped", tracking_no=tracking_no)


# =====================================================================
# ACCOUNTING LEDGER OPERATIONS
# =====================================================================

def add_ledger_entry(txn_date: str, voucher_type: str, account_head: str, reference_no: str, debit: float, credit: float, narration: str) -> int:
    """Logs an entry to the financial accounting ledger."""
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO accounting_ledger (txn_date, voucher_type, account_head, reference_no, debit, credit, narration)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (txn_date, voucher_type, account_head, reference_no, debit, credit, narration))
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()

    client = get_supabase_client()
    if client and _db_mode == "supabase":
        try:
            client.table("accounting_ledger").insert({
                "txn_date": txn_date,
                "voucher_type": voucher_type,
                "account_head": account_head,
                "reference_no": reference_no,
                "debit": float(debit),
                "credit": float(credit),
                "narration": narration
            }).execute()
        except Exception:
            pass

    return entry_id


def get_ledger_entries() -> List[Dict[str, Any]]:
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounting_ledger ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_financial_summary() -> Dict[str, float]:
    """Calculates Revenue, COGS, Operating Expenses, and Net Profit."""
    init_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()

    # Total Sales Revenue (Credit in Sales vouchers or credit in Sales Revenue head)
    cursor.execute("""
    SELECT COALESCE(SUM(credit), 0.0) FROM accounting_ledger 
    WHERE voucher_type = 'Sales' OR account_head LIKE '%Sales%'
    """)
    revenue = cursor.fetchone()[0]

    # Inventory Purchases / Stock Cost
    cursor.execute("""
    SELECT COALESCE(SUM(debit), 0.0) FROM accounting_ledger 
    WHERE voucher_type = 'Purchase' OR account_head LIKE '%Inventory%'
    """)
    cogs = cursor.fetchone()[0]

    # Operating Expenses (packaging, courier, ad spend, utilities)
    cursor.execute("""
    SELECT COALESCE(SUM(debit), 0.0) FROM accounting_ledger 
    WHERE voucher_type = 'Expense'
    """)
    expenses = cursor.fetchone()[0]

    conn.close()

    net_profit = revenue - (cogs * 0.40) - expenses # Estimated COGS on sold units or gross profit margin
    return {
        "revenue": float(revenue),
        "inventory_purchase": float(cogs),
        "expenses": float(expenses),
        "net_profit": float(net_profit)
    }


# =====================================================================
# SUPABASE STORAGE / ASSETS HELPER
# =====================================================================

def upload_product_image(file_bytes: bytes, filename: str) -> str:
    """
    Uploads an image to Supabase Storage bucket 'product-images' if available,
    otherwise saves locally into assets/uploads/ and returns local relative path.
    """
    client = get_supabase_client()
    safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename.replace(' ', '_')}"

    if client and _db_mode == "supabase":
        try:
            # Upload to 'product-images' bucket
            res = client.storage.from_("product-images").upload(safe_name, file_bytes)
            # Retrieve public URL
            public_url = client.storage.from_("product-images").get_public_url(safe_name)
            return public_url
        except Exception as e:
            pass # Fall back to local file

    # Local storage fallback
    local_path = os.path.join(UPLOADS_DIR, safe_name)
    with open(local_path, "wb") as f:
        f.write(file_bytes)
    return f"assets/uploads/{safe_name}"
