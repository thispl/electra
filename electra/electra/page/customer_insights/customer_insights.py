import frappe
import json
from frappe.utils import nowdate, add_days, fmt_money

@frappe.whitelist()
def get_customer_insights(filters):
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

    # Fetch customers based on filters
    customer_filters = {"customer_group": filters.get("customer_group")} if filters.get("customer_group") else {}
    if filters.get("customer"):
        customer_filters["name"] = ["in", filters.get("customer")]
    customers = frappe.get_all("Customer", filters=customer_filters, fields=["name", "customer_name", "mobile_no", "email_id"])

    results = []

    for customer in customers:
        customer_name = customer.name
        
        # Fetch data from different doctypes for each customer
        sales_order = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount, SUM(total_qty) as total_qty
            FROM `tabSales Order`
            WHERE customer=%s AND docstatus=1 AND transaction_date >= %s AND transaction_date <= %s
        """, (customer_name, start_date, end_date), as_dict=True)[0]

        delivery_note = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount, SUM(total_qty) as total_qty
            FROM `tabDelivery Note`
            WHERE customer=%s AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (customer_name, start_date, end_date), as_dict=True)[0]

        sales_invoice = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(total) as total_taxable_amount, SUM(grand_total) as total_amount,
                   SUM(total_qty) as total_qty,
                   SUM(grand_total - outstanding_amount) as paid_amount, SUM(outstanding_amount) as pending_amount
            FROM `tabSales Invoice`
            WHERE customer=%s AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (customer_name, start_date, end_date), as_dict=True)[0]

        payment_request = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(grand_total) as total_amount
            FROM `tabPayment Request`
            WHERE party=%s AND party_type='Customer' AND docstatus=1 AND creation >= %s AND creation <= %s
        """, (customer_name, start_date, end_date), as_dict=True)[0]

        payment_entry = frappe.db.sql("""
            SELECT COUNT(*) as total_records, SUM(paid_amount) as total_amount
            FROM `tabPayment Entry`
            WHERE party=%s AND party_type='Customer' AND docstatus=1 AND posting_date >= %s AND posting_date <= %s
        """, (customer_name, start_date, end_date), as_dict=True)[0]

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

        sales_order = format_data(sales_order)
        delivery_note = format_data(delivery_note)
        sales_invoice = format_data(sales_invoice)
        payment_request = format_data(payment_request)
        payment_entry = format_data(payment_entry)

        # Append data only if any doctype sections have data
        if any([sales_order, delivery_note, sales_invoice, payment_request, payment_entry]):
            results.append({
                "customer_code": customer.name,
                "customer_name": customer.customer_name,
                "mobile_no": customer.mobile_no,
                "email_id": customer.email_id,
                "sales_order": sales_order,
                "delivery_note": delivery_note,
                "sales_invoice": sales_invoice,
                "payment_request": payment_request,
                "payment_entry": payment_entry
            })

    return results


@frappe.whitelist()
def get_customer_details(customer_code, doctype, details, filters=None):
    # Fetching Doctype Details Based On Customer And Doctype Wise
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


    if doctype == "Sales Order":
        return get_sales_order_data(customer_code, start_date, end_date, details)
    
    elif doctype == "Delivery Note":
        return get_delivery_note_data(customer_code, start_date, end_date, details)
    
    elif doctype == "Sales Invoice":
        return get_sales_invoice_data(customer_code, start_date, end_date, details)

    elif doctype == "Payment Request":
        return get_payment_request_data(customer_code, start_date, end_date, details)

    elif doctype == "Payment Entry":
        return get_payment_entry_data(customer_code, start_date, end_date, details)


def get_sales_order_data(customer_code, start_date, end_date, details):
    # Fetching Sales Order Details And Showcased In Table
    result = frappe.db.sql("""
        SELECT 
            soi.item_code,
            soi.item_name,
            SUM(soi.qty) AS total_qty, 
            SUM(soi.qty - soi.delivered_qty) AS pending_qty, 
            AVG(soi.rate) AS avg_rate, 
            SUM(soi.amount) AS total_amount
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON soi.parent = so.name
        WHERE so.customer = %s 
        AND so.docstatus = 1 
        AND so.transaction_date >= %s
        AND so.transaction_date <= %s
        GROUP BY soi.item_code
    """, (customer_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Customer Name - {customer_code}</h5>
        <h5>Total Sales Order: {details.get('total_records')}</h5>
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


def get_delivery_note_data(customer_code, start_date, end_date, details):
    # Fetching Delivery Note Details And Showcased In Table
    result = frappe.db.sql("""
            SELECT 
                dni.item_code,
                dni.item_name,
                SUM(dni.qty) AS total_qty,
                SUM(dni.rate) AS avg_rate,
                SUM(dni.amount) AS total_amount
            FROM `tabDelivery Note Item` dni
            JOIN `tabDelivery Note` dn ON dni.parent = dn.name
            WHERE dn.customer=%s 
            AND dn.docstatus=1 
            AND dn.posting_date >= %s
            AND dn.posting_date <= %s
            GROUP BY dni.item_code
        """, (customer_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Customer Name - {customer_code}</h5>
        <h5>Total Delivery Note: {details.get('total_records')}</h5>
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


def get_sales_invoice_data(customer_code, start_date, end_date, details):
    # Fetching Sales Invoice Details And Showcased In Table
    result = frappe.db.sql("""
            SELECT 
                sii.item_code,
                sii.item_name,
                SUM(sii.qty) AS total_qty,
                SUM(sii.rate) AS avg_rate,
                SUM(sii.amount) AS total_amount
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE si.customer=%s 
            AND si.docstatus=1 
            AND si.posting_date >= %s
            AND si.posting_date <= %s
            GROUP BY sii.item_code
        """, (customer_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Customer Name - {customer_code}</h5>
        <h5>Total Sales Invoice: {details.get('total_records')}</h5>
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


def get_payment_request_data(customer_code, start_date, end_date, details):
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
            pr.party_type='Customer'
            AND pr.party=%s 
            AND pr.docstatus=1 
            AND pr.transaction_date >= %s 
            AND pr.transaction_date <= %s
    """, (customer_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Customer Name - {customer_code}</h5>
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


def get_payment_entry_data(customer_code, start_date, end_date, details):
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
            pe.party_type='Customer'
            AND pe.party=%s 
            AND pe.docstatus=1 
            AND pe.posting_date >= %s 
            AND pe.posting_date <= %s
    """, (customer_code, start_date, end_date), as_dict=True)

    html = f"""
        <h5>Customer Name - {customer_code}</h5>
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