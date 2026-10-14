"""
Compliant GST Tax Invoice PDF Generator for Roselet Jewels.
Built using fpdf2 adhering to Indian GST standards (HSN 7117 - Imitation Jewelry).
"""

import os
import json
from datetime import datetime
from fpdf import FPDF
from typing import Dict, Any


def num_to_words_inr(num: float) -> str:
    """Converts a numeric rupee amount to standard Indian English words."""
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def convert_below_thousand(n):
        res = ""
        if n >= 100:
            res += units[n // 100] + " Hundred "
            n %= 100
        if n >= 20:
            res += tens[n // 10] + " "
            n %= 10
        elif n >= 10:
            res += teens[n - 10] + " "
            n = 0
        if n > 0:
            res += units[n] + " "
        return res.strip()

    rupees = int(round(num))
    if rupees == 0:
        return "Zero Rupees Only"

    parts = []
    # Crores
    if rupees >= 10000000:
        cr = rupees // 10000000
        parts.append(convert_below_thousand(cr) + " Crore")
        rupees %= 10000000

    # Lakhs
    if rupees >= 100000:
        lk = rupees // 100000
        parts.append(convert_below_thousand(lk) + " Lakh")
        rupees %= 100000

    # Thousands
    if rupees >= 1000:
        th = rupees // 1000
        parts.append(convert_below_thousand(th) + " Thousand")
        rupees %= 1000

    if rupees > 0:
        parts.append(convert_below_thousand(rupees))

    return " ".join(parts).strip() + " Rupees Only"


class RoseletInvoicePDF(FPDF):
    def header(self):
        # Primary Brand Banner
        self.set_fill_color(10, 25, 49) # Deep Navy #0A1931
        self.rect(0, 0, 210, 36, 'F')

        # Gold Accent line
        self.set_fill_color(197, 160, 89) # Gold #C5A059
        self.rect(0, 36, 210, 2, 'F')

        # Company Title
        self.set_xy(14, 8)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(100, 10, "ROSELET JEWELS", ln=0)

        # Invoice Banner Tag
        self.set_xy(110, 8)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(197, 160, 89)
        self.cell(86, 10, "TAX INVOICE", align='R', ln=1)

        # Tagline
        self.set_xy(14, 18)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(220, 220, 230)
        self.cell(120, 5, "Luxury Anti-Tarnish & Designer Ornaments | Kerala, India", ln=1)

        self.set_xy(110, 18)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(200, 200, 210)
        self.cell(86, 5, "GSTIN: 32AABCU9603R1ZM | State Code: 32", align='R', ln=1)

        self.set_xy(110, 24)
        self.cell(86, 5, "PAN: AABCU9603R | roseletjewels.com", align='R', ln=1)

        self.ln(16)

    def footer(self):
        self.set_y(-24)
        self.set_draw_color(197, 160, 89)
        self.line(14, self.get_y(), 196, self.get_y())
        self.ln(2)

        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(120, 4, "Thank you for adorning with Roselet Jewels! Genuine Anti-Tarnish Lifetime Polish Guarantee.", ln=0)
        self.cell(62, 4, f"Page {self.page_no()}", align='R', ln=1)

        self.set_font('Helvetica', '', 7)
        self.set_text_color(130, 130, 130)
        self.cell(182, 4, "Registered Office: Roselet Tower, M.G. Road, Ernakulam, Kerala - 682016 | WhatsApp: +91 98470 12345", align='C')


def generate_gst_invoice_pdf(order_data: Dict[str, Any], output_path: str = None) -> bytes:
    """
    Generates an official GST Tax Invoice compliant with HSN 7117 rules.
    Returns bytes or writes to output_path.
    """
    pdf = RoseletInvoicePDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=26)
    pdf.add_page()

    order_no = order_data.get("order_no", "RJ-1001")
    created_at = order_data.get("created_at", datetime.now().strftime("%Y-%m-%d"))
    if isinstance(created_at, str) and "T" in created_at:
        invoice_date = created_at.split("T")[0]
    elif isinstance(created_at, str):
        invoice_date = created_at.split(" ")[0]
    else:
        invoice_date = datetime.now().strftime("%Y-%m-%d")

    # Customer info
    cust_name = order_data.get("customer_name") or order_data.get("full_name") or "Valued Customer"
    cust_phone = order_data.get("customer_phone") or order_data.get("phone") or "N/A"
    cust_address = order_data.get("customer_address") or order_data.get("address") or "Kerala, India"
    cust_city = order_data.get("customer_city") or order_data.get("city") or "Kochi"
    cust_state = order_data.get("customer_state") or order_data.get("state") or "Kerala"
    cust_pin = order_data.get("customer_pincode") or order_data.get("pincode") or ""
    is_kerala = (cust_state.strip().lower() == "kerala")

    payment_mode = order_data.get("payment_mode", "UPI / GPay")
    tracking_no = order_data.get("tracking_no") or "Dispatched via Express Courier"

    # 1. Invoice Meta & Customer Grid
    pdf.set_draw_color(220, 220, 225)
    pdf.set_fill_color(248, 249, 252)

    # Box left: Bill To
    pdf.rect(14, 42, 90, 36, 'DF')
    pdf.set_xy(17, 44)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(10, 25, 49)
    pdf.cell(84, 4, "BILLED TO / RECIPIENT:", ln=1)

    pdf.set_x(17)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(84, 5, str(cust_name), ln=1)

    pdf.set_x(17)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(70, 70, 70)
    addr_line = f"{cust_address}, {cust_city}"
    if len(addr_line) > 42:
        addr_line = addr_line[:40] + "..."
    pdf.cell(84, 4, addr_line, ln=1)

    pdf.set_x(17)
    pdf.cell(84, 4, f"State: {cust_state} (Code: {'32' if is_kerala else '99'}) - PIN: {cust_pin}", ln=1)

    pdf.set_x(17)
    pdf.cell(84, 4, f"Mobile/WhatsApp: +91 {cust_phone}", ln=1)

    # Box right: Invoice Details
    pdf.rect(106, 42, 90, 36, 'DF')
    pdf.set_xy(109, 44)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(10, 25, 49)
    pdf.cell(84, 4, "INVOICE DISPATCH SUMMARY:", ln=1)

    pdf.set_x(109)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(40, 4, "Invoice Number:", ln=0)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(44, 4, f"INV-{order_no}", ln=1)

    pdf.set_x(109)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(40, 4, "Invoice Date:", ln=0)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(44, 4, str(invoice_date), ln=1)

    pdf.set_x(109)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(40, 4, "Order Number:", ln=0)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(44, 4, str(order_no), ln=1)

    pdf.set_x(109)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(40, 4, "Payment Mode:", ln=0)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(44, 4, str(payment_mode), ln=1)

    pdf.set_x(109)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(40, 4, "Courier Tracking:", ln=0)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(44, 4, str(tracking_no)[:24], ln=1)

    # 2. Itemized Table
    pdf.set_xy(14, 82)
    pdf.set_fill_color(10, 25, 49)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)

    # Table columns:
    # # (8), Description (70), HSN (16), Qty (12), Unit Rate (24), Taxable (24), Total (28) = 182 mm
    pdf.cell(8, 7, "#", border=1, fill=True, align='C')
    pdf.cell(72, 7, "ITEM DESCRIPTION", border=1, fill=True)
    pdf.cell(16, 7, "HSN", border=1, fill=True, align='C')
    pdf.cell(12, 7, "QTY", border=1, fill=True, align='C')
    pdf.cell(24, 7, "RATE (INR)", border=1, fill=True, align='R')
    pdf.cell(24, 7, "TAXABLE", border=1, fill=True, align='R')
    pdf.cell(26, 7, "TOTAL (INR)", border=1, fill=True, align='R', ln=1)

    # Parse items
    raw_items = order_data.get("items_json") or order_data.get("items") or []
    if isinstance(raw_items, str):
        try:
            items_list = json.loads(raw_items)
        except Exception:
            items_list = []
    else:
        items_list = raw_items

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(40, 40, 40)
    pdf.set_draw_color(225, 225, 230)

    calculated_taxable_total = 0.0

    for idx, it in enumerate(items_list, 1):
        name = it.get("name", "Designer Ornament")
        qty = int(it.get("qty", 1))
        price = float(it.get("price", 0.0))
        item_total = price * qty
        hsn = it.get("hsn", "7117")

        # In India imitation jewelry retail prices include 3% GST
        # Taxable value = item_total / 1.03
        taxable_item = item_total / 1.03
        rate_item = price / 1.03
        calculated_taxable_total += taxable_item

        # Row shading
        if idx % 2 == 0:
            pdf.set_fill_color(250, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(8, 6.5, str(idx), border=1, fill=True, align='C')
        pdf.cell(72, 6.5, name[:38], border=1, fill=True)
        pdf.cell(16, 6.5, hsn, border=1, fill=True, align='C')
        pdf.cell(12, 6.5, str(qty), border=1, fill=True, align='C')
        pdf.cell(24, 6.5, f"{rate_item:,.2f}", border=1, fill=True, align='R')
        pdf.cell(24, 6.5, f"{taxable_item:,.2f}", border=1, fill=True, align='R')
        pdf.cell(26, 6.5, f"{item_total:,.2f}", border=1, fill=True, align='R', ln=1)

    # GST Calculation
    subtotal = float(order_data.get("subtotal", calculated_taxable_total))
    cgst = float(order_data.get("cgst", 0.0))
    sgst = float(order_data.get("sgst", 0.0))
    igst = float(order_data.get("igst", 0.0))
    shipping = float(order_data.get("shipping_charge", 0.0))
    net_total = float(order_data.get("net_total", subtotal + cgst + sgst + igst + shipping))

    # Summary section
    curr_y = pdf.get_y() + 4

    # Left: Bank & Notes Box
    pdf.set_xy(14, curr_y)
    pdf.set_fill_color(248, 249, 252)
    pdf.rect(14, curr_y, 102, 38, 'DF')

    pdf.set_xy(17, curr_y + 2)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(10, 25, 49)
    pdf.cell(96, 4, "OFFICIAL BANK & PAYMENT DETAILS:", ln=1)

    pdf.set_x(17)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(96, 3.5, "Bank: HDFC Bank Ltd | Account Name: ROSELET JEWELS", ln=1)
    pdf.set_x(17)
    pdf.cell(96, 3.5, "Account No: 50200088992211 | IFSC: HDFC0001234", ln=1)
    pdf.set_x(17)
    pdf.cell(96, 3.5, "UPI ID: roseletjewels@hdfcbank | WhatsApp Pay: +91 98470 12345", ln=1)
    pdf.set_x(17)
    pdf.cell(96, 3.5, "Declaration: We declare that this invoice shows the actual price of goods", ln=1)
    pdf.set_x(17)
    pdf.cell(96, 3.5, "described and that all particulars are true and correct.", ln=1)

    # Right: Calculations Table
    right_x = 120
    row_h = 5.2

    pdf.set_xy(right_x, curr_y)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(60, 60, 60)

    # Subtotal
    pdf.cell(46, row_h, "Taxable Value (Subtotal):", align='R')
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(30, row_h, f"INR {subtotal:,.2f}", align='R', ln=1)

    if is_kerala:
        # CGST 1.5%
        pdf.set_x(right_x)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(46, row_h, "CGST (1.5%):", align='R')
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(30, row_h, f"INR {cgst:,.2f}", align='R', ln=1)

        # SGST 1.5%
        pdf.set_x(right_x)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(46, row_h, "SGST (1.5%):", align='R')
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(30, row_h, f"INR {sgst:,.2f}", align='R', ln=1)
    else:
        # IGST 3.0%
        pdf.set_x(right_x)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(46, row_h, "IGST (3.0%):", align='R')
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(30, row_h, f"INR {igst:,.2f}", align='R', ln=1)

    # Shipping
    pdf.set_x(right_x)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(46, row_h, "Express Pan-India Shipping:", align='R')
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(30, row_h, "FREE" if shipping == 0 else f"INR {shipping:,.2f}", align='R', ln=1)

    # Net Total Highlighted Box
    pdf.set_x(right_x)
    pdf.set_fill_color(10, 25, 49)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(46, 7.5, "NET TOTAL (INCL. GST):", border=1, fill=True, align='R')
    pdf.set_text_color(197, 160, 89)
    pdf.cell(30, 7.5, f"INR {net_total:,.2f}", border=1, fill=True, align='R', ln=1)

    # Amount in words
    pdf.ln(4)
    pdf.set_x(14)
    pdf.set_fill_color(245, 245, 248)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(10, 25, 49)
    pdf.cell(34, 6, "Amount in Words: ", ln=0)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(148, 6, num_to_words_inr(net_total), ln=1)

    # Signature Block
    sig_y = pdf.get_y() + 6
    pdf.set_xy(130, sig_y)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(10, 25, 49)
    pdf.cell(66, 4, "For ROSELET JEWELS", align='C', ln=1)

    pdf.set_xy(130, sig_y + 14)
    pdf.set_font('Helvetica', 'I', 7.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(66, 4, "Authorized Signatory / Digital Stamp", align='C', ln=1)

    # Output
    if output_path:
        pdf.output(output_path)
    return bytes(pdf.output())
