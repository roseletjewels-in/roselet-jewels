"""
=====================================================================
ROSELET JEWELS - OMNI-PLATFORM SUITE
High-End Luxury Mobile-First Storefront & Cloud-Backed Admin ERP
=====================================================================
"""

import os
import json
import urllib.parse
from datetime import datetime, date
import pandas as pd
import streamlit as st

# Local modules
from utils.db import (
    init_db,
    get_db_status,
    get_products,
    get_product_by_id,
    add_product,
    update_product,
    deduct_stock,
    upsert_customer,
    get_customers,
    get_customer_by_id,
    get_next_order_no,
    create_order,
    get_orders,
    get_order_by_id,
    update_order_status,
    update_order_tracking,
    add_ledger_entry,
    get_ledger_entries,
    get_financial_summary,
    upload_product_image
)
from utils.gst_invoice import generate_gst_invoice_pdf

# =====================================================================
# CONFIGURATION & STREAMLIT SETUP
# =====================================================================

st.set_page_config(
    page_title="Roselet Jewels | Luxury Anti-Tarnish Ornaments",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Database (SQLite fallback or Supabase Cloud)
try:
    init_db()
except Exception as e:
    pass

# Secrets & Constants
def get_config(key: str, default: str = "") -> str:
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
        if hasattr(st, "secrets") and "supabase" in st.secrets and key in st.secrets["supabase"]:
            return str(st.secrets["supabase"][key])
    except Exception:
        pass
    return os.environ.get(key, default)

ADMIN_PASSWORD = get_config("ADMIN_PASSWORD", "roseletadmin2026")
BUSINESS_WHATSAPP = get_config("BUSINESS_WHATSAPP", "919847012345")
CHATWOOT_BASE_URL = get_config("CHATWOOT_BASE_URL", "https://app.chatwoot.com")
CHATWOOT_WEBSITE_TOKEN = get_config("CHATWOOT_WEBSITE_TOKEN", "")

INDIAN_STATES = [
    "Kerala", "Tamil Nadu", "Karnataka", "Maharashtra", "Delhi",
    "Telangana", "Andhra Pradesh", "Gujarat", "Uttar Pradesh", "West Bengal",
    "Rajasthan", "Madhya Pradesh", "Haryana", "Punjab", "Goa", "Odisha",
    "Assam", "Bihar", "Chhattisgarh", "Himachal Pradesh", "Jharkhand",
    "Jammu and Kashmir", "Uttarakhand"
]

# Initialize Session State
if "cart" not in st.session_state:
    st.session_state.cart = {} # {product_id: {"product": dict, "qty": int}}

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

if "last_order" not in st.session_state:
    st.session_state.last_order = None

# =====================================================================
# LUXURY CUSTOM CSS STYLING (FINE JEWELLERY MAISON AESTHETIC)
# =====================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800;900&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, .maison-title {
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.08em;
    }

    .editorial-serif {
        font-family: 'Playfair Display', Georgia, serif !important;
    }

    /* Background: Deep Midnight Obsidian with Warm Gold Radiance */
    .stApp {
        background: radial-gradient(ellipse at 50% -20%, #172B4D 0%, #091322 55%, #040810 100%) !important;
        color: #F8F9FA !important;
    }

    /* Top Festive Announcement Ribbon */
    .announcement-ribbon {
        background: linear-gradient(90deg, #8A6421 0%, #D4AF37 50%, #8A6421 100%);
        color: #070E1A;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        text-align: center;
        padding: 6px 12px;
        margin: -40px -40px 16px -40px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25);
    }

    /* Navigation Container */
    .nav-bar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0 16px 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 24px;
    }

    .brand-logo-text {
        font-family: 'Cinzel', serif;
        font-size: 1.45rem;
        font-weight: 800;
        color: #D4AF37;
        letter-spacing: 0.1em;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    }

    .brand-sub-badge {
        font-size: 0.65rem;
        color: #A0AEC0;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    /* Editorial Hero Showcase */
    .editorial-hero {
        text-align: center;
        padding: 36px 20px 24px 20px;
        background: linear-gradient(180deg, rgba(212, 175, 55, 0.08) 0%, rgba(13, 25, 46, 0.3) 100%);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 20px;
        margin-bottom: 28px;
        position: relative;
        box-shadow: inset 0 0 40px rgba(212, 175, 55, 0.05);
    }

    .hero-pretitle {
        font-size: 0.78rem;
        color: #DFC085;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .hero-headline {
        font-family: 'Cinzel', serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.06em;
        margin-bottom: 10px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    .hero-lead {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #CBD5E1;
        font-size: 1.05rem;
        max-width: 680px;
        margin: 0 auto 20px auto;
        line-height: 1.6;
    }

    /* Trust Chips */
    .trust-chips-row {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
    }

    .trust-chip {
        background: rgba(14, 25, 45, 0.85);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 30px;
        padding: 6px 16px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #F3E5AB;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }

    /* Luxury Product Card */
    .luxury-card {
        background: rgba(14, 25, 45, 0.75);
        border: 1px solid rgba(212, 175, 55, 0.22);
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 24px;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        backdrop-filter: blur(10px);
    }

    .luxury-card:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(212, 175, 55, 0.15);
    }

    .card-img-wrapper {
        position: relative;
        width: 100%;
        height: 240px;
        border-radius: 12px;
        overflow: hidden;
        background: #060B14;
    }

    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
    }

    .luxury-card:hover .card-img {
        transform: scale(1.06);
    }

    .floating-badge {
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(7, 14, 26, 0.88);
        border: 1px solid #D4AF37;
        color: #F3E5AB;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        backdrop-filter: blur(6px);
        z-index: 2;
        letter-spacing: 0.04em;
    }

    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.02rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 12px 0 4px 0;
        line-height: 1.35;
        min-height: 44px;
    }

    .card-sku {
        font-size: 0.72rem;
        color: #8C9BB0;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    .card-pricing-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-bottom: 4px;
    }

    .card-selling-price {
        font-size: 1.25rem;
        font-weight: 800;
        color: #D4AF37;
    }

    .card-mrp {
        font-size: 0.82rem;
        color: #7A889B;
        text-decoration: line-through;
    }

    .card-discount-tag {
        background: rgba(16, 185, 129, 0.18);
        color: #34D399;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .card-gst-text {
        font-size: 0.68rem;
        color: #94A3B8;
        margin-bottom: 10px;
        display: block;
    }

    /* Checkout & Bag Section */
    .bag-container-box {
        background: linear-gradient(145deg, #132442 0%, #0A1424 100%);
        border: 1px solid #D4AF37;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
        margin-top: 24px;
    }

    /* Bottom Floating Action Bar */
    .floating-bag-bar {
        position: fixed;
        bottom: 16px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 580px;
        background: linear-gradient(90deg, #14284B 0%, #0D1C35 100%);
        border: 1px solid #D4AF37;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(212, 175, 55, 0.25);
        border-radius: 40px;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 999;
    }

    /* Primary Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    /* Metric card for Admin */
    .metric-card {
        background: rgba(19, 39, 67, 0.8);
        border: 1px solid rgba(197, 160, 89, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #DFC085;
    }
    .metric-lbl {
        font-size: 0.8rem;
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# URL & QUERY PARAMETERS ROUTING
# =====================================================================

params = st.query_params
active_mode = params.get("mode", "store")

# Top Luxury Announcement Ribbon
st.markdown("""
    <div class="announcement-ribbon">
        ✦ FESTIVE CURATION • 100% WATERPROOF ANTI-TARNISH ORNAMENTS • FREE PAN-INDIA EXPRESS SHIPPING • 3% GST INCLUDED ✦
    </div>
""", unsafe_allow_html=True)

# Top Maison Navigation Bar
nav_c1, nav_c2, nav_c3 = st.columns([6, 3, 3])

cart_count = sum(item["qty"] for item in st.session_state.cart.values())
cart_total = sum(item["product"]["selling_price"] * item["qty"] for item in st.session_state.cart.values())

with nav_c1:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:1.8rem; filter:drop-shadow(0 0 10px rgba(212,175,55,0.5));">💎</span>
            <div>
                <div class="brand-logo-text">ROSELET JEWELS</div>
                <div class="brand-sub-badge">KERALA MAISON • ALL-INDIA DELIVERY</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with nav_c2:
    if active_mode == "store":
        if cart_count > 0:
            st.markdown(f"""
                <div style="text-align:right; padding-top:6px;">
                    <span style="background:rgba(212,175,55,0.18); border:1px solid #D4AF37; color:#F3E5AB; padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight:700;">
                        🛍️ Bag: <b>{cart_count} items</b> (₹{cart_total:,.0f})
                    </span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align:right; padding-top:6px; color:#8C9BB0; font-size:0.82rem;">
                    🛍️ Bag: 0 items
                </div>
            """, unsafe_allow_html=True)

with nav_c3:
    if active_mode == "store":
        if st.button("🔐 Admin ERP", key="btn_switch_admin", use_container_width=True):
            st.query_params["mode"] = "admin"
            st.rerun()
    else:
        if st.button("🛍️ Customer Store", key="btn_switch_store", use_container_width=True):
            st.query_params["mode"] = "store"
            st.rerun()


# =====================================================================
# PUBLIC MOBILE-FIRST STOREFRONT (CUSTOMER VIEW)
# =====================================================================

def render_storefront():
    # 1. Editorial Hero Section
    st.markdown("""
        <div class="editorial-hero">
            <div class="hero-pretitle">18K Anti-Tarnish & Traditional Ornaments</div>
            <div class="hero-headline">ELEGANCE THAT NEVER FADES</div>
            <div class="hero-lead">
                Fine jewelry inspired by traditional Kerala artistry, engineered with 18K real gold PVD coating that never fades, tarnishes, or loses its lustre. Wear daily with pride.
            </div>
            <div class="trust-chips-row">
                <span class="trust-chip">💧 100% Anti-Tarnish PVD</span>
                <span class="trust-chip">🚚 Free Pan-India Express Delivery</span>
                <span class="trust-chip">🇮🇳 3% GST Included (HSN 7117)</span>
                <span class="trust-chip">💬 WhatsApp Concierge (+91 98470 12345)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Category Pill Filter Bar
    categories = ["All", "Necklaces", "Bangles", "Earrings", "Rings", "Bridal Sets", "Anti-Tarnish"]
    cat_icons = {
        "All": "✨ All Collections",
        "Necklaces": "📿 Necklaces",
        "Bangles": "✨ Bangles",
        "Earrings": "💎 Earrings",
        "Rings": "💍 Rings",
        "Bridal Sets": "👑 Bridal Sets",
        "Anti-Tarnish": "💧 Anti-Tarnish"
    }

    st.markdown("<p style='font-size:0.85rem; color:#D4AF37; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.12em; font-weight:700;'>CURATED COLLECTIONS:</p>", unsafe_allow_html=True)
    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            is_active = (st.session_state.selected_category == cat)
            label = cat_icons.get(cat, cat)
            if st.button(label, key=f"cat_{cat}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.selected_category = cat
                st.rerun()

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 3. Product Catalog Grid (Full-Width Grand Showcase: 3 Columns)
    products = get_products(category=st.session_state.selected_category, active_only=True)

    if not products:
        st.info("No jewelry pieces currently available in this collection.")
    else:
        # Render 3 items per row for expansive desktop & tablet view
        num_cols = 3
        cols = st.columns(num_cols)

        for idx, p in enumerate(products):
            col_target = cols[idx % num_cols]
            with col_target:
                stock_qty = p.get("stock_qty", 0)
                is_low_stock = (0 < stock_qty <= 3)
                is_out_of_stock = (stock_qty <= 0)
                mrp_val = float(p.get("mrp", 0.0))
                sell_val = float(p.get("selling_price", 0.0))
                disc_pct = int(round((1.0 - sell_val / mrp_val) * 100)) if mrp_val > sell_val else 0

                with st.container():
                    st.markdown(f"""
                        <div class="luxury-card">
                            <div class="card-img-wrapper">
                                <div class="floating-badge">
                                    {'💧 18K Anti-Tarnish' if p.get('category') in ['Anti-Tarnish', 'Necklaces', 'Rings'] else '👑 Temple Classic'}
                                </div>
                                <img src="{p.get('image_url')}" class="card-img" 
                                     onerror="this.src='https://images.unsplash.com/photo-1599643477877-530eb83abc8e?auto=format&fit=crop&w=800&q=80';" />
                            </div>
                            <div class="card-title">{p.get('name')}</div>
                            <div class="card-sku">SKU: {p.get('sku')} • {p.get('category')}</div>
                            <div class="card-pricing-row">
                                <span class="card-selling-price">₹{sell_val:,.0f}</span>
                                <span class="card-mrp">₹{mrp_val:,.0f}</span>
                                {f'<span class="card-discount-tag">{disc_pct}% OFF</span>' if disc_pct > 0 else ''}
                            </div>
                            <span class="card-gst-text">Inclusive of 3% GST (HSN 7117)</span>
                            <div style="font-size:0.75rem; color:{'#EF4444' if is_out_of_stock else ('#F59E0B' if is_low_stock else '#10B981')}; font-weight:700; margin-bottom:10px;">
                                {'❌ Out of Stock' if is_out_of_stock else (f'⚠️ Only {stock_qty} pieces left!' if is_low_stock else '✅ In Stock • Ready to Dispatch')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    pid = p["id"]
                    if not is_out_of_stock:
                        cur_qty = st.session_state.cart.get(pid, {}).get("qty", 0)
                        if cur_qty == 0:
                            if st.button(f"✨ Add to Bag (₹{sell_val:,.0f})", key=f"add_{pid}", use_container_width=True, type="primary"):
                                st.session_state.cart[pid] = {"product": p, "qty": 1}
                                st.rerun()
                        else:
                            b_c1, b_c2, b_c3 = st.columns([1, 2, 1])
                            with b_c1:
                                if st.button("➖", key=f"dec_{pid}", use_container_width=True):
                                    if cur_qty > 1:
                                        st.session_state.cart[pid]["qty"] -= 1
                                    else:
                                        del st.session_state.cart[pid]
                                    st.rerun()
                            with b_c2:
                                st.markdown(f"<div style='text-align:center; padding:6px; font-weight:700; color:#DFC085;'>{cur_qty} in Bag</div>", unsafe_allow_html=True)
                            with b_c3:
                                if st.button("➕", key=f"inc_{pid}", use_container_width=True):
                                    if cur_qty < stock_qty:
                                        st.session_state.cart[pid]["qty"] += 1
                                        st.rerun()
                                    else:
                                        st.toast(f"Only {stock_qty} pieces available in inventory!", icon="⚠️")
                    else:
                        st.button("Sold Out", key=f"sold_{pid}", disabled=True, use_container_width=True)

    # 4. Shopping Bag & WhatsApp Checkout Section
    if st.session_state.cart:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='bag-container-box'>", unsafe_allow_html=True)
        
        bag_col1, bag_col2 = st.columns([6, 6])

        bag_gross = 0.0
        order_items_payload = []

        with bag_col1:
            st.markdown("<h3 style='color:#D4AF37; margin-top:0;'>🛍️ Your Selected Ornaments</h3>", unsafe_allow_html=True)

            for pid, item in list(st.session_state.cart.items()):
                prod = item["product"]
                qty = item["qty"]
                item_total = prod["selling_price"] * qty
                bag_gross += item_total

                order_items_payload.append({
                    "id": prod["id"],
                    "sku": prod["sku"],
                    "name": prod["name"],
                    "qty": qty,
                    "price": float(prod["selling_price"]),
                    "hsn": "7117"
                })

                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(212,175,55,0.15); padding:10px 0;">
                        <div style="display:flex; gap:12px; align-items:center;">
                            <img src="{prod.get('image_url')}" style="width:50px; height:50px; object-fit:cover; border-radius:8px; border:1px solid rgba(212,175,55,0.3);" />
                            <div>
                                <b style="font-size:0.92rem; color:#FFFFFF;">{prod['name']}</b><br/>
                                <span style="font-size:0.75rem; color:#94A3B8;">SKU: {prod['sku']} • ₹{prod['selling_price']:,.0f} × {qty}</span>
                            </div>
                        </div>
                        <div style="font-weight:700; color:#D4AF37; font-size:1.05rem;">
                            ₹{item_total:,.2f}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Clear cart button
            if st.button("🗑️ Empty Shopping Bag", key="btn_empty_bag"):
                st.session_state.cart = {}
                st.rerun()

        with bag_col2:
            st.markdown("<h3 style='color:#D4AF37; margin-top:0;'>📍 Delivery & WhatsApp Order</h3>", unsafe_allow_html=True)

            with st.form("checkout_form_enhanced"):
                cust_name = st.text_input("Full Name*", placeholder="e.g., Ananya Nair")
                cust_phone = st.text_input("WhatsApp Mobile Number* (10 digits)", placeholder="e.g., 9847012345")
                cust_address = st.text_area("Complete Delivery Address*", placeholder="House / Flat No., Landmark, Area")
                
                ck_c1, ck_c2 = st.columns(2)
                with ck_c1:
                    cust_city = st.text_input("City / District*", value="Kochi")
                with ck_c2:
                    cust_pincode = st.text_input("PIN Code*", placeholder="e.g., 682036")

                cust_state = st.selectbox("State / Union Territory*", INDIAN_STATES, index=0)

                # 3% GST calculation
                is_kerala = (cust_state.strip().lower() == "kerala")
                taxable_subtotal = round(bag_gross / 1.03, 2)
                total_gst = round(bag_gross - taxable_subtotal, 2)

                if is_kerala:
                    cgst = round(total_gst / 2.0, 2)
                    sgst = round(total_gst - cgst, 2)
                    igst = 0.0
                else:
                    cgst = 0.0
                    sgst = 0.0
                    igst = total_gst

                shipping_charge = 0.0
                net_total = bag_gross

                st.markdown(f"""
                    <div style="background:rgba(7,14,26,0.7); padding:14px; border-radius:12px; font-size:0.85rem; margin:12px 0; border:1px solid rgba(212,175,55,0.3);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span>Taxable Value:</span>
                            <span>₹{taxable_subtotal:,.2f}</span>
                        </div>
                        {f'''<div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span>CGST (1.5%):</span>
                            <span>₹{cgst:,.2f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span>SGST (1.5%):</span>
                            <span>₹{sgst:,.2f}</span>
                        </div>''' if is_kerala else f'''<div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span>IGST (3.0%):</span>
                            <span>₹{igst:,.2f}</span>
                        </div>'''}
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px; color:#10B981; font-weight:700;">
                            <span>Express Shipping:</span>
                            <span>FREE (All-India)</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-weight:800; font-size:1.15rem; color:#D4AF37; border-top:1px solid rgba(212,175,55,0.3); padding-top:8px; margin-top:6px;">
                            <span>Net Total Payable:</span>
                            <span>₹{net_total:,.2f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                submit_order = st.form_submit_button("💬 Confirm & Transmit Order via WhatsApp", use_container_width=True, type="primary")

                if submit_order:
                    if not cust_name.strip() or not cust_phone.strip() or not cust_address.strip() or not cust_pincode.strip():
                        st.error("Please fill in Name, WhatsApp Number, Address, and PIN Code.")
                    else:
                        clean_phone = cust_phone.strip().replace(" ", "").replace("-", "")
                        if len(clean_phone) < 10:
                            st.error("Please enter a valid 10-digit mobile number.")
                        else:
                            cid = upsert_customer(
                                phone=clean_phone,
                                full_name=cust_name.strip(),
                                address=cust_address.strip(),
                                city=cust_city.strip(),
                                state=cust_state,
                                pincode=cust_pincode.strip(),
                                source="Storefront"
                            )

                            order_no = get_next_order_no()

                            order_dict = {
                                "order_no": order_no,
                                "customer_id": cid,
                                "items": order_items_payload,
                                "items_json": json.dumps(order_items_payload),
                                "subtotal": taxable_subtotal,
                                "cgst": cgst,
                                "sgst": sgst,
                                "igst": igst,
                                "shipping_charge": shipping_charge,
                                "net_total": net_total,
                                "order_status": "WhatsApp_Pending",
                                "payment_mode": "UPI / GPay"
                            }
                            saved_order = create_order(order_dict)

                            items_summary_lines = []
                            for it in order_items_payload:
                                items_summary_lines.append(f"• {it['name']} (Qty: {it['qty']}) - ₹{it['price']*it['qty']:,.0f}")
                            items_text = "\n".join(items_summary_lines)

                            wa_msg = (
                                f"👑 *NEW ORDER - ROSELET JEWELS* 👑\n\n"
                                f"Order ID: *{order_no}*\n"
                                f"Customer: *{cust_name.strip()}*\n"
                                f"Phone: +91 {clean_phone}\n"
                                f"Delivery Address: {cust_address.strip()}, {cust_city.strip()}, {cust_state} - {cust_pincode.strip()}\n\n"
                                f"*Items Ordered:*\n{items_text}\n\n"
                                f"Taxable Value: ₹{taxable_subtotal:,.2f}\n"
                                f"GST (3% - HSN 7117): ₹{total_gst:,.2f}\n"
                                f"Shipping: FREE (Pan-India)\n"
                                f"---------------------------\n"
                                f"💰 *Net Total Payable: ₹{net_total:,.2f}*\n"
                                f"---------------------------\n"
                                f"Please confirm my order and share the official Roselet Jewels UPI QR code for payment! 🙏✨"
                            )

                            encoded_msg = urllib.parse.quote(wa_msg)
                            wa_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={encoded_msg}"

                            st.session_state.last_order = {
                                "order_no": order_no,
                                "wa_url": wa_url,
                                "net_total": net_total,
                                "cust_name": cust_name
                            }

                            st.session_state.cart = {}
                            st.rerun()

        # Success message with WhatsApp button
        if st.session_state.last_order:
            lo = st.session_state.last_order
            st.markdown(f"""
                <div style="background:rgba(16, 185, 129, 0.15); border:1px solid #10B981; border-radius:14px; padding:20px; margin-top:20px; text-align:center;">
                    <h3 style="color:#10B981; margin:0 0 8px 0;">🎉 Order Registered: {lo['order_no']}!</h3>
                    <p style="font-size:0.95rem; color:#E2E8F0; margin-bottom:14px;">
                        Thank you, <b>{lo['cust_name']}</b>! Total Payable: <b>₹{lo['net_total']:,.2f}</b>.<br/>
                        Click below to transmit your order details directly to our Kerala concierge team:
                    </p>
                    <a href="{lo['wa_url']}" target="_blank" style="text-decoration:none;">
                        <div style="background:#25D366; color:#FFFFFF; font-weight:800; padding:14px 28px; border-radius:30px; display:inline-block; font-size:1.05rem; box-shadow:0 6px 20px rgba(37,211,102,0.4); text-transform:uppercase; letter-spacing:0.06em;">
                            📲 Transmit Order on WhatsApp Now
                        </div>
                    </a>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Brand Guarantee & Kerala Heritage Footer
    st.markdown("""
        <div style="margin-top:48px; padding:32px 20px; border-top:1px solid rgba(212,175,55,0.2); text-align:center; background:rgba(7,14,26,0.6); border-radius:16px;">
            <div style="font-family:'Cinzel', serif; font-size:1.15rem; color:#D4AF37; margin-bottom:8px; font-weight:700;">
                ROSELET JEWELS • KERALA
            </div>
            <p style="font-size:0.82rem; color:#94A3B8; max-width:640px; margin:0 auto 16px auto; line-height:1.6;">
                100% Genuine 18K Anti-Tarnish & Traditional Ornaments. Tested against moisture, sweat, and perfumes. Compliant with Indian GST Standards under HSN 7117.
            </p>
            <div style="font-size:0.75rem; color:#64748B;">
                Registered Office: Roselet Tower, M.G. Road, Ernakulam, Kerala - 682016 • WhatsApp: +91 98470 12345
            </div>
        </div>
    """, unsafe_allow_html=True)



# =====================================================================
# PASSWORD-PROTECTED ADMIN ERP PANEL (ADMIN VIEW)
# =====================================================================

def render_admin_panel():
    st.markdown("""
        <div style="padding:16px 0 10px 0; border-bottom:1px solid rgba(197, 160, 89, 0.3); margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h2 style="color:#C5A059; margin:0; font-size:1.6rem;">🛡️ Roselet Jewels | Back-Office ERP</h2>
                    <span style="font-size:0.8rem; color:#94A3B8;">Inventory • GST Orders • Accounting Ledger • Omnichannel CRM</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Admin Authentication Check
    if not st.session_state.admin_authenticated:
        st.markdown("<div style='max-width:440px; margin:40px auto;'>", unsafe_allow_html=True)
        with st.container():
            st.markdown("""
                <div style="background:rgba(19,39,67,0.85); border:1px solid #C5A059; border-radius:14px; padding:24px; text-align:center;">
                    <div style="font-size:2.5rem; margin-bottom:8px;">🔐</div>
                    <h3 style="color:#C5A059; margin-bottom:4px;">Executive Access</h3>
                    <p style="font-size:0.82rem; color:#94A3B8; margin-bottom:16px;">Enter master credential to access administrative operations.</p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("admin_login_form"):
                pwd_input = st.text_input("Admin Password", type="password", placeholder="Enter ERP Password")
                login_btn = st.form_submit_button("Authenticate ERP", use_container_width=True, type="primary")

                if login_btn:
                    if pwd_input == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.success("Authentication successful!")
                        st.rerun()
                    else:
                        st.error("Invalid password. Access denied.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Authenticated Top Bar
    db_status = get_db_status()
    top_col1, top_col2 = st.columns([8, 4])
    with top_col1:
        st.markdown(f"""
            <div style="font-size:0.82rem; color:#CBD5E1; padding-top:4px;">
                🟢 <b>Database Engine:</b> {db_status['engine']} &nbsp;|&nbsp; 
                👤 <b>Role:</b> Master Store Administrator
            </div>
        """, unsafe_allow_html=True)
    with top_col2:
        if st.button("🚪 Logout of ERP", key="btn_admin_logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # ERP Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Orders & GST Billing",
        "💎 Inventory & Stock",
        "📊 Accounting & Profit",
        "🧾 GST Tax Invoices",
        "💬 Omnichannel CRM & Chat"
    ])

    # -----------------------------------------------------------------
    # TAB 1: ORDERS & GST BILLING DASHBOARD
    # -----------------------------------------------------------------
    with tab1:
        st.markdown("### 📦 Orders & Fulfillment Operations")

        all_orders = get_orders(status_filter="All")
        pending_count = sum(1 for o in all_orders if o.get("order_status") == "WhatsApp_Pending")
        billed_count = sum(1 for o in all_orders if o.get("order_status") == "Confirmed_Billed")
        shipped_count = sum(1 for o in all_orders if o.get("order_status") == "Shipped")
        total_rev = sum(float(o.get("net_total", 0.0)) for o in all_orders if o.get("order_status") != "Cancelled")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='metric-card'><div class='metric-val'>{len(all_orders)}</div><div class='metric-lbl'>Total Orders</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#F59E0B;'>{pending_count}</div><div class='metric-lbl'>WhatsApp Pending</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#10B981;'>{billed_count}</div><div class='metric-lbl'>Confirmed & Billed</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#60A5FA;'>{shipped_count}</div><div class='metric-lbl'>Dispatched / Shipped</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Status filter
        f_col1, f_col2 = st.columns([4, 8])
        with f_col1:
            order_filter = st.selectbox(
                "Filter by Order Status",
                ["All", "WhatsApp_Pending", "Confirmed_Billed", "Shipped", "Delivered"],
                index=0
            )

        filtered_orders = get_orders(status_filter=order_filter)

        if not filtered_orders:
            st.info("No orders found matching the selected filter.")
        else:
            for ord_row in filtered_orders:
                oid = ord_row["id"]
                ono = ord_row.get("order_no", f"RJ-{oid}")
                cname = ord_row.get("customer_name") or "Valued Customer"
                cphone = ord_row.get("customer_phone") or "N/A"
                cstate = ord_row.get("customer_state") or "Kerala"
                net_amt = float(ord_row.get("net_total", 0.0))
                status = ord_row.get("order_status", "WhatsApp_Pending")
                pmode = ord_row.get("payment_mode", "UPI / GPay")
                tracking = ord_row.get("tracking_no", "")

                status_color = "#F59E0B" if status == "WhatsApp_Pending" else ("#10B981" if status == "Confirmed_Billed" else ("#3B82F6" if status == "Shipped" else "#94A3B8"))

                with st.expander(f"Order {ono} • {cname} (+91 {cphone}) • ₹{net_amt:,.2f} • [{status}]", expanded=(status == "WhatsApp_Pending")):
                    o_c1, o_c2 = st.columns([7, 5])

                    with o_c1:
                        st.markdown(f"""
                            <b>Recipient:</b> {cname} | <b>Phone:</b> +91 {cphone}<br/>
                            <b>Address:</b> {ord_row.get('customer_address')}, {ord_row.get('customer_city')}, {cstate} - {ord_row.get('customer_pincode')}<br/>
                            <b>Payment Mode:</b> {pmode} | <b>Status:</b> <span style="color:{status_color}; font-weight:700;">{status}</span><br/>
                            <b>Tracking Number:</b> {tracking if tracking else '<i>Not yet assigned</i>'}
                        """, unsafe_allow_html=True)

                        # Parse items
                        raw_items = ord_row.get("items_json", "[]")
                        try:
                            items_list = json.loads(raw_items)
                        except Exception:
                            items_list = []

                        st.markdown("<p style='font-size:0.85rem; margin-top:8px; font-weight:600; color:#DFC085;'>Items in Order:</p>", unsafe_allow_html=True)
                        for itm in items_list:
                            st.markdown(f"• <b>{itm.get('name')}</b> (SKU: {itm.get('sku')}) × {itm.get('qty')} @ ₹{itm.get('price'):,.0f} each")

                        st.markdown(f"""
                            <div style="font-size:0.85rem; color:#CBD5E1; margin-top:6px;">
                                Taxable: ₹{ord_row.get('subtotal', 0):,.2f} | 
                                CGST: ₹{ord_row.get('cgst', 0):,.2f} | 
                                SGST: ₹{ord_row.get('sgst', 0):,.2f} | 
                                IGST: ₹{ord_row.get('igst', 0):,.2f}
                            </div>
                        """, unsafe_allow_html=True)

                    with o_c2:
                        st.markdown("<div style='background:rgba(10,25,49,0.5); padding:10px; border-radius:8px;'>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.85rem; font-weight:700; color:#DFC085; margin-bottom:8px;'>Actions & Fulfillment:</p>", unsafe_allow_html=True)

                        # 1-Click Confirm & Bill
                        if status == "WhatsApp_Pending":
                            assign_pmode = st.selectbox(
                                "Confirm Payment Mode",
                                ["UPI / GPay", "Bank Transfer", "Cash on Delivery (COD)"],
                                key=f"pmode_{oid}"
                            )
                            if st.button("✅ Confirm & Bill Order", key=f"bill_{oid}", use_container_width=True, type="primary"):
                                update_order_status(oid, "Confirmed_Billed", payment_mode=assign_pmode)
                                st.success(f"Order {ono} confirmed! Ledger entry recorded.")
                                st.rerun()

                        # Courier Tracking Updater
                        track_input = st.text_input("Courier Tracking AWB", value=tracking, key=f"track_{oid}", placeholder="e.g. BLUEDART-KL123456")
                        if st.button("🚚 Update Tracking & Mark Shipped", key=f"btn_track_{oid}", use_container_width=True):
                            if track_input.strip():
                                update_order_tracking(oid, track_input.strip())
                                st.success("Tracking updated and status set to Shipped!")
                                st.rerun()

                        # WhatsApp Tracking Dispatch Button
                        if track_input.strip():
                            track_wa_msg = (
                                f"Hello {cname}! ✨\n\n"
                                f"Great news from *Roselet Jewels*! Your order *{ono}* has been dispatched via express courier.\n\n"
                                f"📦 Tracking AWB: *{track_input.strip()}*\n"
                                f"Estimated delivery: 2-3 business days.\n\n"
                                f"Adorn with pride! 👑\nhttps://roseletjewels.com"
                            )
                            wa_track_url = f"https://wa.me/91{cphone}?text={urllib.parse.quote(track_wa_msg)}"
                            st.markdown(f"""
                                <a href="{wa_track_url}" target="_blank" style="text-decoration:none;">
                                    <div style="background:#25D366; color:#FFF; text-align:center; padding:6px; border-radius:6px; font-size:0.8rem; font-weight:700; margin-top:6px;">
                                        📲 Send Tracking Update on WhatsApp
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)

                        # PDF Invoice Download
                        pdf_bytes = generate_gst_invoice_pdf(ord_row)
                        st.download_button(
                            label=f"📄 Download Tax Invoice (PDF)",
                            data=pdf_bytes,
                            file_name=f"Tax_Invoice_{ono}.pdf",
                            mime="application/pdf",
                            key=f"dl_inv_{oid}",
                            use_container_width=True
                        )

                        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 2: INVENTORY & STOCK MANAGER
    # -----------------------------------------------------------------
    with tab2:
        st.markdown("### 💎 Inventory & Catalog Management")

        all_products = get_products(category="All", active_only=False)
        total_skus = len(all_products)
        total_units = sum(p.get("stock_qty", 0) for p in all_products)
        low_stock = [p for p in all_products if p.get("stock_qty", 0) <= 3]

        inv_c1, inv_c2, inv_c3 = st.columns(3)
        with inv_c1:
            st.markdown(f"<div class='metric-card'><div class='metric-val'>{total_skus}</div><div class='metric-lbl'>Active SKUs</div></div>", unsafe_allow_html=True)
        with inv_c2:
            st.markdown(f"<div class='metric-card'><div class='metric-val'>{total_units}</div><div class='metric-lbl'>Total Inventory Units</div></div>", unsafe_allow_html=True)
        with inv_c3:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:{'#EF4444' if low_stock else '#10B981'};'>{len(low_stock)}</div><div class='metric-lbl'>Low Stock Alerts (≤3)</div></div>", unsafe_allow_html=True)

        if low_stock:
            st.warning(f"⚠️ Critical Stock Alert: {len(low_stock)} items need immediate replenishment: " + ", ".join([p['name'] for p in low_stock]))

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Add New Product Form
        with st.expander("➕ Add New Ornament to Catalog", expanded=False):
            with st.form("add_product_form"):
                ap_c1, ap_c2 = st.columns(2)
                with ap_c1:
                    new_sku = st.text_input("SKU Code*", placeholder="e.g., RJ-NK-009")
                    new_name = st.text_input("Ornament Title*", placeholder="e.g., Antique Gold Lakshmi Haar")
                    new_cat = st.selectbox("Category*", ["Necklaces", "Bangles", "Earrings", "Rings", "Bridal Sets", "Anti-Tarnish"])
                    new_cost = st.number_input("Purchase Cost (₹)", min_value=0.0, value=500.0, step=50.0)

                with ap_c2:
                    new_mrp = st.number_input("MRP (₹)", min_value=0.0, value=1999.0, step=100.0)
                    new_price = st.number_input("Selling Price (₹ - Incl. 3% GST)*", min_value=0.0, value=1199.0, step=50.0)
                    new_stock = st.number_input("Initial Stock Quantity*", min_value=0, value=15, step=1)
                    new_img_url = st.text_input("Image URL (Unsplash or CDN)", placeholder="https://images.unsplash.com/...")

                uploaded_img = st.file_uploader("Or Upload Product Photo (Pushes to Supabase Storage)", type=["png", "jpg", "jpeg", "webp"])

                add_submit = st.form_submit_button("✨ Save Ornament to Catalog", use_container_width=True, type="primary")

                if add_submit:
                    if not new_sku.strip() or not new_name.strip():
                        st.error("Please provide both SKU and Product Name.")
                    else:
                        final_img = new_img_url.strip()
                        if uploaded_img is not None:
                            bytes_data = uploaded_img.getvalue()
                            final_img = upload_product_image(bytes_data, uploaded_img.name)

                        if not final_img:
                            final_img = "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80"

                        new_p_data = {
                            "sku": new_sku.strip(),
                            "name": new_name.strip(),
                            "category": new_cat,
                            "purchase_cost": new_cost,
                            "mrp": new_mrp,
                            "selling_price": new_price,
                            "stock_qty": int(new_stock),
                            "image_url": final_img,
                            "is_active": True
                        }
                        add_product(new_p_data)
                        st.success(f"Ornament '{new_name}' successfully added to catalog!")
                        st.rerun()

        # Existing Products Table & Fast Stock Updates
        st.markdown("#### 📋 Current Catalog")
        prod_table_data = []
        for p in all_products:
            prod_table_data.append({
                "ID": p["id"],
                "SKU": p["sku"],
                "Name": p["name"],
                "Category": p["category"],
                "Cost (₹)": p.get("purchase_cost", 0.0),
                "MRP (₹)": p.get("mrp", 0.0),
                "Selling Price (₹)": p.get("selling_price", 0.0),
                "Stock": p.get("stock_qty", 0),
                "Active": "✅ Yes" if p.get("is_active") else "❌ No"
            })
        st.dataframe(pd.DataFrame(prod_table_data), use_container_width=True)

        # Quick stock replenishment tool
        with st.expander("⚡ Quick Stock Replenishment Tool"):
            r_c1, r_c2, r_c3 = st.columns([5, 3, 4])
            with r_c1:
                p_opts = {f"{p['sku']} - {p['name']} (Current: {p['stock_qty']})": p["id"] for p in all_products}
                sel_p_key = st.selectbox("Select Ornament", list(p_opts.keys()))
                sel_p_id = p_opts[sel_p_key]
            with r_c2:
                add_qty = st.number_input("Add Units", min_value=1, value=10, step=1)
            with r_c3:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("➕ Replenish Stock", use_container_width=True, type="primary"):
                    curr_p = get_product_by_id(sel_p_id)
                    if curr_p:
                        new_tot = curr_p.get("stock_qty", 0) + add_qty
                        update_product(sel_p_id, {"stock_qty": new_tot})
                        st.success(f"Stock updated! New balance: {new_tot} units.")
                        st.rerun()

    # -----------------------------------------------------------------
    # TAB 3: ACCOUNTING, EXPENSES & PROFIT LEDGER
    # -----------------------------------------------------------------
    with tab3:
        st.markdown("### 📊 Financial Accounting & Profit / Loss Statement")

        fin = get_financial_summary()
        ac_c1, ac_c2, ac_c3, ac_c4 = st.columns(4)
        with ac_c1:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#10B981;'>₹{fin['revenue']:,.2f}</div><div class='metric-lbl'>Total Sales Revenue</div></div>", unsafe_allow_html=True)
        with ac_c2:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#F59E0B;'>₹{fin['inventory_purchase']:,.2f}</div><div class='metric-lbl'>Inventory Purchases</div></div>", unsafe_allow_html=True)
        with ac_c3:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#EF4444;'>₹{fin['expenses']:,.2f}</div><div class='metric-lbl'>Operating Expenses</div></div>", unsafe_allow_html=True)
        with ac_c4:
            st.markdown(f"<div class='metric-card'><div class='metric-val' style='color:#DFC085;'>₹{fin['net_profit']:,.2f}</div><div class='metric-lbl'>Calculated Net Profit</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Add Expense Voucher Form
        with st.expander("📝 Record Operating Expense / Stock Purchase Voucher", expanded=False):
            with st.form("expense_entry_form"):
                ex_c1, ex_c2 = st.columns(2)
                with ex_c1:
                    exp_date = st.date_input("Transaction Date", value=date.today())
                    exp_type = st.selectbox("Voucher Type", ["Expense", "Purchase", "Sales", "Receipt"])
                    exp_head = st.selectbox("Account Head", [
                        "Packaging Materials (Velvet Boxes, Pouches)",
                        "Courier & Logistics (Bluedart/Delhivery)",
                        "Meta & Instagram Ad Spend",
                        "Stock / Raw Material Purchase",
                        "Store Rent & Utilities",
                        "Office Stationery & Printing",
                        "Other Operational Expenses"
                    ])
                with ex_c2:
                    exp_amt = st.number_input("Amount (INR)*", min_value=0.0, value=500.0, step=100.0)
                    exp_ref = st.text_input("Reference / Bill No", placeholder="e.g., INV-META-9821")
                    exp_narr = st.text_input("Narration / Purpose", placeholder="e.g., Sponsored reels campaign for anti-tarnish rings")

                record_btn = st.form_submit_button("💾 Save Voucher to General Ledger", use_container_width=True, type="primary")

                if record_btn:
                    if exp_amt <= 0:
                        st.error("Amount must be greater than zero.")
                    else:
                        is_debit = (exp_type in ["Expense", "Purchase"])
                        add_ledger_entry(
                            txn_date=exp_date.isoformat(),
                            voucher_type=exp_type,
                            account_head=exp_head,
                            reference_no=exp_ref.strip() or "N/A",
                            debit=exp_amt if is_debit else 0.0,
                            credit=0.0 if is_debit else exp_amt,
                            narration=exp_narr.strip() or f"Recorded {exp_head}"
                        )
                        st.success("Voucher logged to general ledger successfully!")
                        st.rerun()

        # Ledger Transactions Table
        st.markdown("#### 📜 General Ledger Entries")
        ledger_rows = get_ledger_entries()
        if not ledger_rows:
            st.info("No ledger entries recorded yet.")
        else:
            df_ledger = pd.DataFrame(ledger_rows)
            st.dataframe(df_ledger[["id", "txn_date", "voucher_type", "account_head", "reference_no", "debit", "credit", "narration"]], use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 4: COMPLIANT GST TAX INVOICES
    # -----------------------------------------------------------------
    with tab4:
        st.markdown("### 🧾 Compliant GST Tax Invoice PDF Generator")
        st.markdown("Adheres to Indian GST Council specifications for HSN Code **7117** (Imitation Jewelry). Features 3% GST, official bank details, customer address, and amount in words.")

        all_orders = get_orders(status_filter="All")
        if not all_orders:
            st.info("No orders found to generate invoices.")
        else:
            order_map = {}
            for o in all_orders:
                ono_val = o.get('order_no') or f"RJ-{o.get('id')}"
                cname_val = o.get('customer_name') or "Customer"
                tot_val = float(o.get('net_total', 0.0))
                lbl = f"{ono_val} • {cname_val} (₹{tot_val:,.2f})"
                order_map[lbl] = o
            selected_key = st.selectbox("Select Order to Generate Tax Invoice", list(order_map.keys()))
            target_order = order_map[selected_key]

            ti_c1, ti_c2 = st.columns([7, 5])
            with ti_c1:
                st.markdown(f"""
                    <div style="background:rgba(19,39,67,0.7); border:1px solid #C5A059; border-radius:10px; padding:16px;">
                        <h4 style="color:#C5A059; margin-top:0;">Invoice Summary: {target_order.get('order_no')}</h4>
                        <b>Billed To:</b> {target_order.get('customer_name')}<br/>
                        <b>Address:</b> {target_order.get('customer_address')}, {target_order.get('customer_city')}, {target_order.get('customer_state')} - {target_order.get('customer_pincode')}<br/>
                        <b>State Code:</b> {'32 (Kerala)' if target_order.get('customer_state', '').lower() == 'kerala' else '99 (Inter-state)'}<br/>
                        <b>Tax Breakdown:</b> Subtotal ₹{target_order.get('subtotal', 0):,.2f} | CGST ₹{target_order.get('cgst', 0):,.2f} | SGST ₹{target_order.get('sgst', 0):,.2f} | IGST ₹{target_order.get('igst', 0):,.2f}<br/>
                        <div style="font-size:1.1rem; font-weight:700; color:#DFC085; margin-top:8px;">
                            Net Total: ₹{target_order.get('net_total', 0):,.2f}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with ti_c2:
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                pdf_bytes = generate_gst_invoice_pdf(target_order)

                st.download_button(
                    label=f"📥 Download A4 Tax Invoice PDF",
                    data=pdf_bytes,
                    file_name=f"Roselet_Tax_Invoice_{target_order.get('order_no')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )

                st.markdown("""
                    <div style="font-size:0.8rem; color:#94A3B8; margin-top:10px;">
                        ✅ Includes GSTIN: 32AABCU9603R1ZM<br/>
                        ✅ Automatic Amount-to-Words rendering<br/>
                        ✅ Authorized Signatory stamp section<br/>
                        ✅ Official HDFC Bank & UPI payment accounts
                    </div>
                """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 5: OMNICHANNEL CRM & CHAT INBOX
    # -----------------------------------------------------------------
    with tab5:
        st.markdown("### 💬 Omnichannel CRM & Social Chat Center")
        st.markdown("Centralize inquiries from Instagram DMs, Facebook Messenger, and WhatsApp Web in one place.")

        crm_sub1, crm_sub2 = st.tabs(["👥 Customer CRM Directory", "💬 Social Chat Center (Chatwoot / WhatsApp)"])

        with crm_sub1:
            customers = get_customers()
            orders_all = get_orders(status_filter="All")

            # Calculate customer lifetime spend
            spend_map = {}
            count_map = {}
            for o in orders_all:
                cid = o.get("customer_id")
                amt = float(o.get("net_total", 0.0))
                spend_map[cid] = spend_map.get(cid, 0.0) + amt
                count_map[cid] = count_map.get(cid, 0) + 1

            crm_data = []
            for c in customers:
                cid = c["id"]
                crm_data.append({
                    "ID": cid,
                    "Name": c["full_name"],
                    "Mobile / WhatsApp": f"+91 {c['phone']}",
                    "City": c.get("city", "Kochi"),
                    "State": c.get("state", "Kerala"),
                    "Total Orders": count_map.get(cid, 0),
                    "Lifetime Spend (₹)": f"{spend_map.get(cid, 0.0):,.2f}",
                    "Source": c.get("source", "Storefront")
                })

            if crm_data:
                st.dataframe(pd.DataFrame(crm_data), use_container_width=True)
            else:
                st.info("No customers registered yet.")

        with crm_sub2:
            if CHATWOOT_WEBSITE_TOKEN and CHATWOOT_BASE_URL:
                st.markdown(f"""
                    <div style="border-radius:12px; overflow:hidden; border:1px solid #C5A059;">
                        <iframe src="{CHATWOOT_BASE_URL}" width="100%" height="650px" frameborder="0"></iframe>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="background:rgba(19,39,67,0.7); border:1px solid rgba(197,160,89,0.3); border-radius:12px; padding:20px;">
                        <h4 style="color:#C5A059; margin-top:0;">⚡ Social Chat Hub & Direct Links</h4>
                        <p style="font-size:0.88rem; color:#CBD5E1;">
                            Connect your brand social accounts or plug in your Chatwoot Cloud Inbox by setting <code>CHATWOOT_WEBSITE_TOKEN</code> in <code>.streamlit/secrets.toml</code>.
                        </p>
                        
                        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:16px;">
                            <a href="https://web.whatsapp.com" target="_blank" style="text-decoration:none;">
                                <div style="background:#25D366; color:#FFF; font-weight:700; padding:10px 18px; border-radius:8px; font-size:0.9rem;">
                                    💬 Open WhatsApp Web (+91 {BUSINESS_WHATSAPP})
                                </div>
                            </a>
                            <a href="https://instagram.com" target="_blank" style="text-decoration:none;">
                                <div style="background:linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); color:#FFF; font-weight:700; padding:10px 18px; border-radius:8px; font-size:0.9rem;">
                                    📸 Open Instagram DMs (@roseletjewels)
                                </div>
                            </a>
                            <a href="https://business.facebook.com" target="_blank" style="text-decoration:none;">
                                <div style="background:#1877F2; color:#FFF; font-weight:700; padding:10px 18px; border-radius:8px; font-size:0.9rem;">
                                    📘 Open Meta Business Suite
                                </div>
                            </a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# =====================================================================
# MAIN ROUTING
# =====================================================================

if active_mode == "admin":
    render_admin_panel()
else:
    render_storefront()
