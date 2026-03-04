import frappe
import json
from frappe.utils import nowdate, add_days, fmt_money

@frappe.whitelist()
def get_supplier_insights(filters):
    filters = json.loads(filters)

    # Date Range Logic
    date_ranges = {
        "Last Week": -7,
        "Last Month": -30,
        "Last 3 Months": -90,
        "Last Year": -365
    }

    if filters.get("date_range") == 'Select Date Range':
        start_date, end_date = filters.get("selected_date_range")
    else:
        start_date = add_days(nowdate(), date_ranges.get(filters.get("date_range"), -30))
        end_date = nowdate()

    # Fetch supplier based on filters
    supplier_filters = {"supplier_group": filters.get("supplier_group")} if filters.get("supplier_group") else {}
    if filters.get("supplier"):
        supplier_filters["name"] = ["in", filters.get("supplier")]
    suppliers = frappe.get_all("Supplier", filters=supplier_filters, fields=["name", "supplier_name", "mobile_no", "email_id"])

    results = []

    for supplier in suppliers:
        supplier_name = supplier.name
        
        # Fetch data from different doctypes for each supplier
        purchase_order = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount, SUM(total_qty) as total_qty
            FROM `tabPurchase Order`
            WHERE supplier=%s AND docstatus=1 AND transaction_date >= %s AND transaction_date <= %s
        """, (supplier_name, start_date, end_date), as_dict=True)[0]

        purchase_receipt = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount, SUM(total_qty) as total_qty
            FROM `tabPurchase Receipt`
            WHERE supplier=%s AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (supplier_name, start_date, end_date), as_dict=True)[0]

        purchase_invoice = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount,
                   SUM(total_qty) as total_qty,
                   SUM(grand_total - outstanding_amount) as paid_amount, SUM(outstanding_amount) as pending_amount
            FROM `tabPurchase Invoice`
            WHERE supplier=%s AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (supplier_name, start_date, end_date), as_dict=True)[0]

        payment_request = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(grand_total) as total_amount
            FROM `tabPayment Request`
            WHERE party=%s AND party_type='Supplier' AND docstatus=1 AND creation >= %s AND creation <= %s
        """, (supplier_name, start_date, end_date), as_dict=True)[0]

        payment_entry = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(paid_amount) as total_amount
            FROM `tabPayment Entry`
            WHERE party=%s AND party_type='Supplier' AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (supplier_name, start_date, end_date), as_dict=True)[0]

        # Format amounts and exclude empty sections
        def format_data(data):
            if data["total_records"] and data["total_records"] > 0:
                result = {
                    "total_records": data["total_records"],
                    "total_amount": fmt_money(data["total_amount"] or 0),
                    "total_qty": int(data.get("total_qty", 0)),
                    "paid_amount": fmt_money(data.get("paid_amount", 0)),
                    "pending_amount": fmt_money(data.get("pending_amount", 0))
                }
                if "total_taxable_amount" in data:
                    result["total_taxable_amount"] = fmt_money(data["total_taxable_amount"] or 0)

                return result
            return None

        purchase_order = format_data(purchase_order)
        purchase_receipt = format_data(purchase_receipt)
        purchase_invoice = format_data(purchase_invoice)
        payment_request = format_data(payment_request)
        payment_entry = format_data(payment_entry)

        # Append data only if any doctype sections have data
        if any([purchase_order, purchase_receipt, purchase_invoice, payment_request, payment_entry]):
            results.append({
                "supplier_code": supplier.name,
                "supplier_name": supplier.supplier_name,
                "mobile_no": supplier.mobile_no,
                "email_id": supplier.email_id,
                "purchase_order": purchase_order,
                "purchase_receipt": purchase_receipt,
                "purchase_invoice": purchase_invoice,
                "payment_request": payment_request,
                "payment_entry": payment_entry
            })

    return results


@frappe.whitelist()
def get_supplier_details(supplier_code, doctype, details, filters=None):
    # Fetching Doctype Details Based On Supplier And Doctype Wise
    filters = json.loads(filters)
    details = json.loads(details)

    # Date Range Logic
    date_ranges = {
        "Last Week": -7,
        "Last Month": -30,
        "Last 3 Months": -90,
        "Last Year": -365
    }
    
    if filters.get("date_range") == 'Select Date Range':
        start_date, end_date = filters.get("selected_date_range")
    else:
        start_date = add_days(nowdate(), date_ranges.get(filters.get("date_range"), -30))  # Default to Last Month if invalid
        end_date = nowdate()


    if doctype == "Purchase Order":
        return get_purchase_order_data(supplier_code, start_date, end_date, details)
    
    elif doctype == "Purchase Receipt":
        return get_purchase_receipt_data(supplier_code, start_date, end_date, details)
    
    elif doctype == "Purchase Invoice":
        return get_purchase_invoice_data(supplier_code, start_date, end_date, details)

    elif doctype == "Payment Request":
        return get_payment_request_data(supplier_code, start_date, end_date, details)

    elif doctype == "Payment Entry":
        return get_payment_entry_data(supplier_code, start_date, end_date, details)


def get_purchase_order_data(supplier_code, start_date, end_date, details):
    # Fetching Purchase Order Details And Showcased In Table
    result = frappe.db.sql("""
        SELECT 
            poi.item_code,
            poi.item_name,
            SUM(poi.qty) AS total_qty, 
            SUM(poi.qty - poi.received_qty) AS pending_qty, 
            AVG(poi.rate) AS avg_rate, 
            SUM(poi.amount) AS total_amount
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON poi.parent = po.name
        WHERE po.supplier = %s 
        AND po.docstatus = 1 
        AND po.transaction_date >= %s
        AND po.transaction_date <= %s
        GROUP BY poi.item_code
    """, (supplier_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Supplier Name - {supplier_code}</h5>
        <h5>Total Purchase Order: {details.get('total_records')}</h5>
        <br>
        <h4>Item Details</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Item Code</th>
                    <th>Item Name</th>
                    <th width="10%">Qty</th>
                    <th width="10%">Pending Qty</th>
                    <th width="15%">Rate</th>
                    <th width="15%">Total Taxable Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    pending_qty = 0
    total_amount = 0

    for item in result:
        html += f"""
            <tr>
                <td>{item.item_code}</td>
                <td>{item.item_name}</td>
                <td>{frappe.format_value(item.total_qty, "Float")}</td>
                <td>{frappe.format_value(item.pending_qty, "Float")}</td>
                <td>{frappe.format_value(item.avg_rate, "Currency")}</td>
                <td>{frappe.format_value(item.total_amount, "Currency")}</td>
            </tr>
        """
        pending_qty += item.pending_qty
        total_amount += item.total_amount

    html += f"""
        <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td>{frappe.format_value(details.get('total_qty'), "Float")}</td>
            <td>{frappe.format_value(pending_qty, "Float")}</td>
            <td></td>
            <td>{frappe.format_value(total_amount, "Currency")}</td>
    """

    html += "</tbody></table>"

    return html


def get_purchase_receipt_data(supplier_code, start_date, end_date, details):
    # Fetching Purchase Receipt Details And Showcased In Table
    result = frappe.db.sql("""
            SELECT 
                pri.item_code,
                pri.item_name,
                SUM(pri.qty) AS total_qty,
                SUM(pri.rate) AS avg_rate,
                SUM(pri.amount) AS total_amount
            FROM `tabPurchase Receipt Item` pri
            JOIN `tabPurchase Receipt` pr ON pri.parent = pr.name
            WHERE pr.supplier=%s 
            AND pr.docstatus=1 
            AND pr.posting_date >= %s
            AND pr.posting_date <= %s
            GROUP BY pri.item_code
        """, (supplier_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Supplier Name - {supplier_code}</h5>
        <h5>Total Purchase Receipt: {details.get('total_records')}</h5>
        <br>
        <h4>Item Details</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Item Code</th>
                    <th>Item Name</th>
                    <th width="10%">Qty</th>
                    <th width="15%">Rate</th>
                    <th width="15%">Total Taxable Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    total_amount = 0
    for item in result:
        html += f"""
            <tr>
                <td>{item.item_code}</td>
                <td>{item.item_name}</td>
                <td>{frappe.format_value(item.total_qty, "Float")}</td>
                <td>{frappe.format_value(item.avg_rate, "Currency")}</td>
                <td>{frappe.format_value(item.total_amount, "Currency")}</td>
            </tr>
        """
        total_amount += item.total_amount

    html += f"""
        <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td>{frappe.format_value(details.get('total_qty'), "Float")}</td>
            <td></td>
            <td>{frappe.format_value(total_amount, "Currency")}</td>
        </tr>
    """

    html += "</tbody></table>"

    return html


def get_purchase_invoice_data(supplier_code, start_date, end_date, details):
    # Fetching Purchase Invoice Details And Showcased In Table
    result = frappe.db.sql("""
            SELECT 
                pii.item_code,
                pii.item_name,
                SUM(pii.qty) AS total_qty,
                SUM(pii.rate) AS avg_rate,
                SUM(pii.amount) AS total_amount
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pi.supplier=%s 
            AND pi.docstatus=1 
            AND pi.posting_date >= %s
            AND pi.posting_date <= %s
            GROUP BY pii.item_code
        """, (supplier_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Supplier Name - {supplier_code}</h5>
        <h5>Total Purchase Invoice: {details.get('total_records')}</h5>
        <br>
        <h4>Item Details</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Item Code</th>
                    <th>Item Name</th>
                    <th width="10%">Qty</th>
                    <th width="15%">Rate</th>
                    <th width="15%">Total Taxable Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    total_amount = 0
    for item in result:
        html += f"""
            <tr>
                <td>{item.item_code}</td>
                <td>{item.item_name}</td>
                <td>{frappe.format_value(item.total_qty, "Float")}</td>
                <td>{frappe.format_value(item.avg_rate, "Currency")}</td>
                <td>{frappe.format_value(item.total_amount, "Currency")}</td>
            </tr>
        """
        total_amount += item.total_amount

    html += f"""
        <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td>{frappe.format_value(details.get('total_qty'), "Float")}</td>
            <td></td>
            <td>{frappe.format_value(total_amount, "Currency")}</td>
        </tr>
    """

    html += "</tbody></table>"

    return html


def get_payment_request_data(supplier_code, start_date, end_date, details):
    # Fetching Payment Request Details And Showcased In Table
    result = frappe.db.sql("""
        SELECT 
            pr.payment_request_type,
            pr.transaction_date, 
            pr.reference_doctype, 
            pr.reference_name,
            pr.grand_total
        FROM `tabPayment Request` pr
        WHERE
            pr.party_type='Supplier'
            AND pr.party=%s 
            AND pr.docstatus=1 
            AND pr.transaction_date >= %s 
            AND pr.transaction_date <= %s
    """, (supplier_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Supplier Name - {supplier_code}</h5>
        <h5>Total Payment Request: {details.get('total_records')}</h5>
        <br>
        <h4>Item Details</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Payment Request Type</th>
                    <th>Transaction Date</th>
                    <th width="25%">Reference Doctype</th>
                    <th width="25%">Reference Name</th>
                    <th width="15%">Total Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    total_amount = 0
    for item in result:
        html += f"""
            <tr>
                <td>{item.payment_request_type}</td>
                <td>{frappe.format_value(item.transaction_date, "Date")}</td>
                <td>{item.reference_doctype}</td>
                <td>{item.reference_name}</td>
                <td>{frappe.format_value(item.grand_total, "Currency")}</td>
            </tr>
        """
        total_amount += item.grand_total

    html += f"""
        <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td></td>
            <td></td>
            <td>{frappe.format_value(total_amount, "Currency")}</td>
        </tr>
    """

    html += "</tbody></table>"

    return html


def get_payment_entry_data(supplier_code, start_date, end_date, details):
    # Fetching Payment Entry Details And Showcased In Table
    result = frappe.db.sql("""
        SELECT 
            pe.payment_type,
            pe.posting_date,
            pe.mode_of_payment,
            pe.unallocated_amount,
            pe.paid_amount
        FROM `tabPayment Entry` pe
        WHERE
            pe.party_type='Supplier'
            AND pe.party=%s 
            AND pe.docstatus=1 
            AND pe.posting_date >= %s 
            AND pe.posting_date <= %s
    """, (supplier_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Supplier Name - {supplier_code}</h5>
        <h5>Total Payment Entry: {details.get('total_records')}</h5>
        <br>
        <h4>Item Details</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Payment Type</th>
                    <th>Transaction Date</th>
                    <th width="20%">Mode of Payment</th>
                    <th width="20%">Unallocated Amount</th>
                    <th width="20%">Paid Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    unllocated_amount = 0
    total_amount = 0
    for item in result:
        html += f"""
            <tr>
                <td>{item.payment_type}</td>
                <td>{frappe.format_value(item.posting_date, "Date")}</td>
                <td>{item.mode_of_payment}</td>
                <td>{frappe.format_value(item.unallocated_amount, "Currency")}</td>
                <td>{frappe.format_value(item.paid_amount, "Currency")}</td>
            </tr>
        """
        unllocated_amount += item.unallocated_amount
        total_amount += item.paid_amount

    html += f"""
        <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td></td>
            <td>{frappe.format_value(unllocated_amount, "Currency")}</td>
            <td>{frappe.format_value(total_amount, "Currency")}</td>
        </tr>
    """

    html += "</tbody></table>"

    return html