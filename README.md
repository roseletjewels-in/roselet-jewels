# 👑 Roselet Jewels — Omni-Platform Suite

> **High-End Luxury Mobile-First Storefront & Cloud-Backed Admin ERP**  
> Tailored for Kerala-based imitation and anti-tarnish jewelry with Pan-India delivery.

---

## 🌟 Tech Stack & Architecture
- **Frontend / Fullstack:** Python, Streamlit (Custom Deep Navy `#0A1931` & Gold `#C5A059` luxury theme)
- **Database & Storage:** Supabase (Cloud PostgreSQL + Supabase Storage) with automatic zero-config **Local SQLite fallback** (`local_roselet.db`)
- **Invoicing:** `fpdf2` (Compliant GST Tax Invoice with HSN `7117`, 3% GST split, bank details, and amount in words)
- **Deployment:** Render.com (`render.yaml`) / Streamlit Community Cloud / Docker

---

## 🚀 Quick Start (Local Run)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Application:**
   ```bash
   streamlit run app.py --server.port 8520
   ```
   *The app is configured to run on free port **8520** (`http://localhost:8520`).*

---

## 📱 Dual-Interface Architecture

### 1. Public Mobile-First Storefront (`roseletjewels.com`)
- **Luxury Brand Aesthetics:** Deep Onyx Navy `#0A1931`, Champagne Gold `#DFC085`, and Crisp White.
- **Collections Filter:** Interactive filter bar for `All`, `Necklaces`, `Bangles`, `Earrings`, `Rings`, `Bridal Sets`, and `Anti-Tarnish`.
- **Product Cards:** High-resolution jewelry imagery, waterproof badges (`💧 100% Waterproof / Anti-Tarnish`), strikethrough MRP, and Selling Price (inclusive of 3% GST).
- **Shopping Bag & WhatsApp Checkout:**
  - Real-time cart calculation and stock deduction.
  - Automatic customer profile upsert into database.
  - **3% GST Tax Engine (HSN 7117):**
    - **Within Kerala:** 1.5% CGST + 1.5% SGST
    - **Interstate:** 3.0% IGST
  - Instant generation of formatted WhatsApp click-to-chat links transmitting order ID, recipient address, itemized summary, and total payable amount.

### 2. Password-Protected Admin ERP (`roseletjewels.com/admin`)
- **Executive Login:** Secured via `ADMIN_PASSWORD` (Default: `roseletadmin2026`).
- **Tab 1: Orders & GST Billing Dashboard:**
  - Status filters (`All`, `WhatsApp_Pending`, `Confirmed_Billed`, `Shipped`, `Delivered`).
  - 1-Click "Confirm & Bill" that records journal entries to the financial ledger.
  - Courier Tracking updater with 1-click WhatsApp tracking updates to customers.
- **Tab 2: Inventory & Stock Manager:**
  - Full catalog CRUD and low-stock indicators (`stock_qty <= 3`).
  - Direct product image uploader supporting Supabase Storage bucket `product-images` and local storage.
  - Fast replenishment tool.
- **Tab 3: Accounting, Expenses & Profit Ledger:**
  - Real-time financial reports: **Revenue – COGS – Operating Expenses = Net Profit**.
  - Expense voucher forms for ad spend, packaging materials, courier charges, and stock purchases.
- **Tab 4: Compliant GST Tax Invoice PDF Generator:**
  - 1-Click downloadable A4 PDF invoice formatted with brand headers, HSN 7117, state code (32 for Kerala), bank account details, and amount in words.
- **Tab 5: Omnichannel CRM & Social Chat:**
  - Customer directory with lifetime spend metrics and lead sources.
  - Integrated command center for WhatsApp Web, Instagram DMs, and optional Chatwoot Cloud iframe embed.

---

## ☁️ Supabase Cloud Configuration (Optional)

To connect your Supabase Cloud project:
1. Create a project at [supabase.com](https://supabase.com).
2. Run `database/schema.sql` in the Supabase SQL Editor.
3. Create a public storage bucket named `product-images`.
4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-or-service-role-key"
   ADMIN_PASSWORD = "your-secure-password"
   BUSINESS_WHATSAPP = "919847012345"
   ```

---

## 🌐 Cloud Deployment on Render.com

The repository includes a ready-to-use `render.yaml`:
1. Push this repository to GitHub.
2. In Render Dashboard, click **New +** -> **Blueprint**.
3. Select this repository and click **Apply**.
4. Set your production environment variables (`ADMIN_PASSWORD`, `BUSINESS_WHATSAPP`, `SUPABASE_URL`, `SUPABASE_KEY`).
