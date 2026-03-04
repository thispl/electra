# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from datetime import date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Project No") + ":Link/Project:200",
        _("Project Reference") + ":Data/:200",
        _("Sales Order No") + ":Link/Sales Order:200",
        _("Project Description") + ":Data/:300",
        _("Contract Value") + ":Currency/:150",
        _("Revised Contract Value") + ":Currency/:200",
        _("Est Cost to Complete") + ":Currency/:200",
        _("Est Profit Margin") + ":Currency/:150",
        _("Actual Costs till Previous Year") + ":Currency/:230",
        _("Costs incurred during the year") + ":Currency/:230",
        _("Total Cost") + ":Currency/:160",
        _("Percentage of Completion") + ":Percentage/:200",
        _("Progress Bills Raised Previous Year") + ":Currency/:260",
        _("Progress Bills Raised Current Year") + ":Currency/:250",
        _("Total Progress Bills Raised") + ":Currency/:250",
        _("Revenue Recognised upto Previous Year") + ":Currency/:300",
        _("Revenue for the Current Year") + ":Currency/:240",
        _("Total Revenue") + ":Currency/:240",
        _("Short or Excess Revenue Over Billings") + ":Currency/:270",
        _("Percentage to be Completed") + ":Percentage/:250",
        _("Value to be Executed") + ":Currency/:170",
        _("Delivery Note Percentage to be Completed") + ":Percentage/:340",
        _("Task Percentage to be Completed") + ":Percentage/:250",
        _("Project Costing Amount") + ":Currency/:200",
        _("Project Percentage to be Completed") + ":Percentage/:270",
        _("Outstanding Amount") + ":Currency/:170",
        _("Outstanding Without Advance") + ":Currency/:260",
        _("Outstanding Without Retention") + ":Currency/:260",
    ]
    return columns

from datetime import datetime

def get_data(filters):
    data = []
    project = ""
    sales_order = ""
    
    from_date = datetime.strptime(str(filters.from_date), "%Y-%m-%d") if filters.get("from_date") else None
    to_date = datetime.strptime(str(filters.to_date), "%Y-%m-%d") if filters.get("to_date") else None

    # Initialize
    last_year_start_date, last_year_end_date = None, None
    current_year_start_date, current_year_end_date = None, None
    
    # Case 1: Both dates fall in the current year
    if from_date.year == to_date.year and to_date.year == datetime.today().year:
        current_year_start_date = from_date.strftime("%Y-%m-%d")
        current_year_end_date = to_date.strftime("%Y-%m-%d")

    # Case 2: Both dates fall in the previous year
    elif from_date.year == to_date.year and to_date.year == datetime.today().year - 1:
        last_year_start_date = from_date.strftime("%Y-%m-%d")
        last_year_end_date = to_date.strftime("%Y-%m-%d")

    # Case 3: Period spans across two years (previous → current)
    elif from_date.year != to_date.year and to_date.year == from_date.year + 1:
        last_year_start_date = from_date.strftime("%Y-%m-%d")
        last_year_end_date = f"{from_date.year}-12-31"
        current_year_start_date = f"{to_date.year}-01-01"
        current_year_end_date = to_date.strftime("%Y-%m-%d")

    # Default fallback (safety)
    else:
        current_year_start_date = from_date.strftime("%Y-%m-%d")
        current_year_end_date = to_date.strftime("%Y-%m-%d")
        
    frappe.log_error("from date",[current_year_start_date,current_year_end_date,last_year_start_date,last_year_end_date])

    # Filters
    conditions, sql_filters = get_conditions(filters)

    query = f"""
        SELECT pb.*, so.project
        FROM `tabProject Budget` pb
        JOIN `tabSales Order` so ON pb.sales_order = so.name
        WHERE pb.docstatus = 1  
        AND so.docstatus = 1
        AND so.status != 'Closed' 
        AND {conditions}
    """

    project_budgets = frappe.db.sql(query, sql_filters, as_dict=True)

    for pb in project_budgets:
        project = pb.project
        if not project:
            continue

        sales_order = frappe.db.get_value("Sales Order", {"project_budget": pb.name,"posting_date":("between",from_date,to_date)}, "name")
        project_name = frappe.db.get_value("Cost Estimation",
                                           {'name': pb.cost_estimation, "docstatus": 1},
                                           ['project_name'])
        
        project_start_date = frappe.get_value("Project", project, "creation")
        project_start_date = project_start_date.date() if project_start_date else last_year_start_date

        lead_customer = frappe.db.get_value("Cost Estimation",
                                            {'name': pb.cost_estimation, "docstatus": 1},
                                            ['lead_customer'])
        contract_value = round(frappe.db.get_value("Cost Estimation",
                                                   {'name': pb.cost_estimation, 'docstatus': 1},
                                                   ['total_bidding_price']) or 0, 2)
        revised_contract_value = round(frappe.db.get_value("Sales Order", sales_order, "net_bidding_price") or 0, 2)
        est_cost_to_complete = round(pb.total_cost_of_the_project or 0, 2)
        est_profit_margin = round(revised_contract_value - est_cost_to_complete, 2)

        # Costs
        cost_incurred_current_year = round(project_cost_till_date(project, current_year_start_date, current_year_end_date), 2) if current_year_start_date else 0
        if filters.from_date and filters.to_date:
            total_cost_incurred = round(project_cost_till_date(project, from_date,to_date), 2)
        else:
            total_cost_incurred = 0
        cost_incurred_upto_previous_year = total_cost_incurred - cost_incurred_current_year
        budget_doc = frappe.get_doc("Project Budget",pb.name)
        for i in budget_doc.item_table:
            total_qty += i.qty
            delivered_qty += i.delivered_qty

        if total_qty == delivered_qty:
            percentage_of_completion = 100
        else:
        # % completion
            percentage_of_completion = (total_cost_incurred / pb.total_cost_of_the_project * 100) if pb.total_cost_of_the_project else 0
        str_percentage_of_completion = f"{round(percentage_of_completion, 2)}%"

        percentage_of_completion_previous_year = (cost_incurred_upto_previous_year / pb.total_cost_of_the_project * 100) if pb.total_cost_of_the_project else 0
        percentage_of_completion_current_year = (cost_incurred_current_year / pb.total_cost_of_the_project * 100) if pb.total_cost_of_the_project else 0

        # Bills
        progress_bills_raised_previous_year = progress_bills(project, last_year_start_date, last_year_end_date) if last_year_start_date else 0
        progress_bills_raised_current_year = progress_bills(project, current_year_start_date, current_year_end_date) if current_year_start_date else 0

        if filters.from_date and filters.to_date:
            total_progress_bills_raised = progress_bills(project, filters.from_date, filters.to_date)
        else:
            total_progress_bills_raised = progress_bills_raised_previous_year + progress_bills_raised_current_year

        # Revenue
        if est_cost_to_complete:
            revenue_recognised_upto_previous_year = round((revised_contract_value * (cost_incurred_upto_previous_year / est_cost_to_complete)), 2)
            revenue_for_the_current_year = round((revised_contract_value * (cost_incurred_current_year / est_cost_to_complete)), 2)
        else:
            revenue_recognised_upto_previous_year = 0
            revenue_for_the_current_year = 0
        total_revenue = round((revenue_recognised_upto_previous_year + revenue_for_the_current_year), 2)
        
        budget_doc = frappe.get_doc("Project Budget",pb.name)
        for i in budget_doc.item_table:
            total_qty += i.qty
            delivered_qty += i.delivered_qty

        if total_qty == delivered_qty:
            short_excess_revenue_over_billings = 0
            percentage_to_be_completed = 0
        else:
            if filters.company == "MEP DIVISION - ELECTRA":
                short_excess_revenue_over_billings = round((revenue_for_the_current_year - total_progress_bills_raised), 2)
            else:
                short_excess_revenue_over_billings = round((revenue_for_the_current_year - progress_bills_raised_current_year), 2)

        percentage_to_be_completed = round(100 - percentage_of_completion, 2)
        str_percentage_to_be_completed = f"{percentage_to_be_completed}%"
        value_to_be_executed = round((revised_contract_value * percentage_to_be_completed) / 100, 2)

        # Delivery
        per_delivered = frappe.db.get_value("Sales Order", {"name": sales_order}, ['per_delivered']) or 0
        delivery_note_percentage_to_be_completed = round(100 - per_delivered, 2)
        str_delivery_note_percentage_to_be_completed = f"{delivery_note_percentage_to_be_completed}%"

        # Tasks
        task_count = frappe.db.count("Task", {"project": project})
        completed_count = frappe.db.count("Task", {"project": project, "status": "Completed"})
        task_percentage_to_be_completed = round(100 - ((completed_count / task_count) * 100 if task_count else 0), 2)
        str_task_percentage_to_be_completed = f"{task_percentage_to_be_completed}%"

        project_percentage_to_be_completed = (task_percentage_to_be_completed + delivery_note_percentage_to_be_completed) / 2
        str_project_percentage_to_be_completed = f"{project_percentage_to_be_completed}%"

        # Costing
        project_cost = frappe.db.sql("""
            SELECT SUM(td.costing_amount) AS total
            FROM `tabTimesheet Detail` td
            JOIN `tabTimesheet` t ON t.name = td.parent
            WHERE td.project = %s AND t.docstatus != 2
        """, project, as_dict=True)[0] or {}
        project_costing_amount = round(project_cost.get("total") or 0, 2)

        # Outstanding
        out_amount = round(frappe.db.get_value("Sales Invoice", {"project": project}, "outstanding_amount", order_by="posting_date desc") or 0, 2)
        out_retention = round(frappe.db.get_value("Sales Invoice", {"project": project}, "outstanding_amount__without_retention", order_by="posting_date desc") or 0, 2)
        advance = float(frappe.db.get_value("Sales Invoice", {"project": project}, "adv_amount", order_by="posting_date desc") or 0)
        out_advance = round((out_amount - advance), 2)

        # Final dict
        data.append({
            "project_no": project,
            "project_reference": lead_customer,
            "sales_order_no": sales_order,
            "project_description": project_name,
            "contract_value": contract_value,
            "revised_contract_value": revised_contract_value,
            "est_cost_to_complete": est_cost_to_complete,
            "est_profit_margin": est_profit_margin,
            "actual_costs_till_previous_year": cost_incurred_upto_previous_year,
            "costs_incurred_during_the_year": cost_incurred_current_year,
            "total_cost": total_cost_incurred,
            "percentage_of_completion": str_percentage_of_completion,
            "progress_bills_raised_previous_year": progress_bills_raised_previous_year,
            "progress_bills_raised_current_year": progress_bills_raised_current_year,
            "total_progress_bills_raised": total_progress_bills_raised,
            "revenue_recognised_upto_previous_year": revenue_recognised_upto_previous_year,
            "revenue_for_the_current_year": revenue_for_the_current_year,
            "total_revenue": total_revenue,
            "short_or_excess_revenue_over_billings": short_excess_revenue_over_billings,
            "percentage_to_be_completed": str_percentage_to_be_completed,
            "value_to_be_executed": value_to_be_executed,
            "delivery_note_percentage_to_be_completed": str_delivery_note_percentage_to_be_completed,
            "task_percentage_to_be_completed": str_task_percentage_to_be_completed,
            "project_costing_amount": project_costing_amount,
            "project_percentage_to_be_completed": str_project_percentage_to_be_completed,
            "outstanding_amount": out_amount,
            "outstanding_without_advance": out_advance,
            "outstanding_without_retention": out_retention,
        })
    return data



@frappe.whitelist()
def cost_incurred(project, pb_name, start_date, end_date):
    pb = frappe.get_doc("Project Budget", pb_name)
    cost = 0
    for i in pb.item_table:
        dn_list = frappe.get_all("Delivery Note", {"project": project, "docstatus": 1, "posting_date": ["between", [start_date, end_date]]})
        for dn in dn_list:
            doc = frappe.get_doc("Delivery Note", dn.name)
            for row in doc.items:
                if row.item_code == i.item:
                    valuation_rate = get_valuation_rate(row.item_code, row.warehouse, end_date)
                    if valuation_rate:
                        cost += row.qty * valuation_rate
                        print([row.item_code, row.qty, valuation_rate, row.qty * valuation_rate])
        dn_wip_list = frappe.get_all("Delivery Note WIP", {"project": project, "docstatus": 1, "posting_date": ["between", [start_date, end_date]]})
        for dn_wip in dn_wip_list:
            doc = frappe.get_doc("Delivery Note WIP", dn_wip.name)
            for row in doc.items:
                if row.item_code == i.item:
                    valuation_rate = get_valuation_rate(row.item_code, row.target_warehouse, end_date)
                    if valuation_rate:
                        cost += row.qty * valuation_rate
    cost = round(cost, 2)
    return cost

@frappe.whitelist()
def get_valuation_rate(item_code, warehouse, date):
    sle = frappe.get_all(
        "Stock Ledger Entry",
        filters={
            "item_code": item_code,
            "warehouse": warehouse,
            "docstatus": 1,
            "posting_date": ("<=", date)
        },
        fields=["valuation_rate"],
        order_by="posting_date DESC, creation DESC",
        limit=1
    )

    return sle[0]["valuation_rate"] if sle else 0

@frappe.whitelist()
def progress_bills(project, start_date, end_date):
    sales_invoices = frappe.get_all("Sales Invoice",
                                    {"project": project,
                                     "posting_date": ["between", [start_date, end_date]],
                                     "docstatus": 1
                                     },
                                    ["custom_total_invoice_amount", "discount_amount"])
    total_invoice = 0
    for si in sales_invoices:
        total_invoice += si.custom_total_invoice_amount - si.discount_amount
    sales_invoices_return = frappe.get_all("Sales Invoice",
                                    {"project": project,
                                     "posting_date": ["between", [start_date, end_date]],
                                     "docstatus": 1, "is_return":1
                                     },
                                    ["base_total", "discount_amount"])
    for si in sales_invoices_return:
        total_invoice += si.base_total - si.discount_amount
    return total_invoice

@frappe.whitelist()
def test_check():
    project = "ENG-PRO-2024-00038"
    from_date = "2024-04-01"
    to_date = "2025-12-31"
    total = (total_dn_cost(project, from_date, to_date) +
             total_dnwip_cost(project, from_date, to_date) +
             total_jl_cost(project, from_date, to_date) +
             total_cost_by_timesheet(project, from_date, to_date))
    print(total)

@frappe.whitelist()
def project_cost_till_date(name, from_date=None, to_date=None):
    project = name
    total = (total_dn_cost(project, from_date, to_date) +
             total_dnwip_cost(project, from_date, to_date) +
             total_jl_cost(project, from_date, to_date) +
             total_cost_by_timesheet(project, from_date, to_date))
    return total
def total_dn_cost(project, from_date, to_date):
    if from_date and to_date:
        
        project_budget = frappe.db.get_value("Project", project, "budgeting")
        pb = frappe.get_doc("Project Budget", project_budget)
    
        data = {}
        project_name = project
        
        if pb.docname_updated_in_dn == 1:
            for item in pb.item_table:
                dn_data = frappe.db.sql(
                    """
                    SELECT 
                        dni.item_code, 
                        dni.qty,
                        (
                            SELECT sle.valuation_rate 
                            FROM `tabStock Ledger Entry` sle 
                            WHERE sle.item_code = dni.item_code 
                            AND sle.voucher_no = dn.name 
                            ORDER BY sle.creation DESC 
                            LIMIT 1
                        ) AS valuation_rate
                    FROM `tabDelivery Note` dn
                    LEFT JOIN `tabDelivery Note Item` dni 
                        ON dn.name = dni.parent
                    WHERE dni.item_code = %s 
                    AND dni.custom_docname = %s
                    AND dn.project = %s
                    AND posting_date BETWEEN %s AND %s 
                    """,
                    (item.item, item.docname, project_name, from_date, to_date),
                    as_dict=True
                ) or []

                # Process fetched data
                for i in dn_data:
                    item_code = i.item_code
                    qty = i.qty or 0
                    valuation_rate = i.valuation_rate or 0
                    amount = qty * valuation_rate

                    # Store data in dictionary
                    if item_code in data:
                        data[item_code]["total_qty"] += qty
                        data[item_code]["total_amount"] += amount
                    else:
                        data[item_code] = {
                            "total_qty": qty,
                            "total_amount": amount
                        }

            total_amount = sum(d["total_amount"] for d in data.values())
        else:
            for item in pb.item_table:
                dn_data = frappe.db.sql(
                    """
                    SELECT 
                        dni.item_code, 
                        dni.qty,
                        (
                            SELECT sle.valuation_rate 
                            FROM `tabStock Ledger Entry` sle 
                            WHERE sle.item_code = dni.item_code 
                            AND sle.voucher_no = dn.name 
                            ORDER BY sle.creation DESC 
                            LIMIT 1
                        ) AS valuation_rate
                    FROM `tabDelivery Note` dn
                    LEFT JOIN `tabDelivery Note Item` dni 
                        ON dn.name = dni.parent
                    WHERE dni.item_code = %s 
                    AND dn.project = %s 
                    AND posting_date BETWEEN %s AND %s 
                    """,
                    (item.item, project_name, from_date, to_date),
                    as_dict=True
                ) or []

                # Process fetched data
                for i in dn_data:
                    item_code = i.item_code
                    qty = i.qty or 0
                    valuation_rate = i.valuation_rate or 0
                    amount = qty * valuation_rate

                    # Store data in dictionary
                    if item_code in data:
                        data[item_code]["total_qty"] += qty
                        data[item_code]["total_amount"] += amount
                    else:
                        data[item_code] = {
                            "total_qty": qty,
                            "total_amount": amount
                        }

            total_amount = sum(d["total_amount"] for d in data.values())

    else:
        project_budget = frappe.db.get_value("Project", project, "budgeting")
        pb = frappe.get_doc("Project Budget", project_budget)
    
        data = {}
        project_name = project
        
        if pb.docname_updated_in_dn == 1:
            for item in pb.item_table:
                dn_data = frappe.db.sql(
                    """
                    SELECT 
                        dni.item_code, 
                        dni.qty,
                        (
                            SELECT sle.valuation_rate 
                            FROM `tabStock Ledger Entry` sle 
                            WHERE sle.item_code = dni.item_code 
                            AND sle.voucher_no = dn.name 
                            ORDER BY sle.creation DESC 
                            LIMIT 1
                        ) AS valuation_rate
                    FROM `tabDelivery Note` dn
                    LEFT JOIN `tabDelivery Note Item` dni 
                        ON dn.name = dni.parent
                    WHERE dni.item_code = %s 
                    AND dni.custom_docname = %s
                    AND dn.project = %s 
                    """,
                    (item.item, item.docname, project_name),
                    as_dict=True
                ) or []

                # Process fetched data
                for i in dn_data:
                    item_code = i.item_code
                    qty = i.qty or 0
                    valuation_rate = i.valuation_rate or 0
                    amount = qty * valuation_rate

                    # Store data in dictionary
                    if item_code in data:
                        data[item_code]["total_qty"] += qty
                        data[item_code]["total_amount"] += amount
                    else:
                        data[item_code] = {
                            "total_qty": qty,
                            "total_amount": amount
                        }

            total_amount = sum(d["total_amount"] for d in data.values())
        else:
            for item in pb.item_table:
                dn_data = frappe.db.sql(
                    """
                    SELECT 
                        dni.item_code, 
                        dni.qty,
                        (
                            SELECT sle.valuation_rate 
                            FROM `tabStock Ledger Entry` sle 
                            WHERE sle.item_code = dni.item_code 
                            AND sle.voucher_no = dn.name 
                            ORDER BY sle.creation DESC 
                            LIMIT 1
                        ) AS valuation_rate
                    FROM `tabDelivery Note` dn
                    LEFT JOIN `tabDelivery Note Item` dni 
                        ON dn.name = dni.parent
                    WHERE dni.item_code = %s 
                    AND dn.project = %s 
                    """,
                    (item.item, project_name),
                    as_dict=True
                ) or []

                # Process fetched data
                for i in dn_data:
                    item_code = i.item_code
                    qty = i.qty or 0
                    valuation_rate = i.valuation_rate or 0
                    amount = qty * valuation_rate

                    # Store data in dictionary
                    if item_code in data:
                        data[item_code]["total_qty"] += qty
                        data[item_code]["total_amount"] += amount
                    else:
                        data[item_code] = {
                            "total_qty": qty,
                            "total_amount": amount
                        }

            total_amount = sum(d["total_amount"] for d in data.values())
    return round(total_amount, 2)

def total_dnwip_cost(project, from_date, to_date):
    if from_date and to_date:
        sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
        pb_name = frappe.db.get_value("Project", project, "budgeting")
        pb = frappe.get_doc("Project Budget", pb_name)

        dn_wip_list = frappe.get_all(
            "Delivery Note WIP",
            filters={"sales_order": sales_order, "is_return": 0, "docstatus": 1,"posting_date": ["between", [from_date, to_date]]},
            pluck="name"
        )

        if not dn_wip_list:
            return 0

        dn_wip_items = frappe.db.sql("""
            SELECT dni.parent AS dn_wip_name, dni.item_code, dni.qty, dni.custom_against_pbsow
            FROM `tabDelivery Note Item` dni
            WHERE dni.parent IN %(dn_wip_list)s
        """, {"dn_wip_list": dn_wip_list}, as_dict=True)

        item_qty_map = {}
        for i in dn_wip_items:
            key = (i.dn_wip_name, i.item_code, i.custom_against_pbsow)
            item_qty_map[key] = item_qty_map.get(key, 0) + i.qty

        stock_entry_data = frappe.db.sql("""
            SELECT se.reference_number, sei.item_code, sei.basic_rate, sei.qty
            FROM `tabStock Entry` se
            JOIN `tabStock Entry Detail` sei ON se.name = sei.parent
            WHERE se.stock_entry_type = 'Material Transfer'
            AND se.docstatus = 1
            AND se.reference_number IN %(dn_wip_list)s
        """, {"dn_wip_list": dn_wip_list}, as_dict=True)

        stock_entries = {}
        for entry in stock_entry_data:
            key = (entry.reference_number, entry.item_code)
            if key in stock_entries:
                stock_entries[key]['total_value'] += entry.basic_rate * entry.qty
                stock_entries[key]['total_qty'] += entry.qty
            else:
                stock_entries[key] = {'total_value': entry.basic_rate * entry.qty, 'total_qty': entry.qty}

        stock_rates = {}
        for key, values in stock_entries.items():
            stock_rates[key] = values['total_value'] / values['total_qty'] if values['total_qty'] > 0 else 0

        amount = 0
    
        for child in pb.item_table:
            total_item_qty = 0
            weighted_rate_sum = 0
            total_rate_qty = 0

            for dn_wip in dn_wip_list:
                key = (dn_wip, child.item, child.docname)
                if key in item_qty_map:
                    item_qty = item_qty_map[key]
                    total_item_qty += item_qty

                    if (dn_wip, child.item) in stock_rates:
                        rate = stock_rates[(dn_wip, child.item)]
                        weighted_rate_sum += rate * item_qty
                        total_rate_qty += item_qty

            final_rate = weighted_rate_sum / total_rate_qty if total_rate_qty > 0 else 0

            amount += final_rate * total_item_qty

    else:
        sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
        pb_name = frappe.db.get_value("Project", project, "budgeting")
        pb = frappe.get_doc("Project Budget", pb_name)

        dn_wip_list = frappe.get_all(
            "Delivery Note WIP",
            filters={"sales_order": sales_order, "is_return": 0, "docstatus": 1},
            pluck="name"
        )

        if not dn_wip_list:
            return 0

        # Fetch all relevant Delivery Note WIP items in bulk
        dn_wip_items = frappe.db.sql("""
            SELECT dni.parent AS dn_wip_name, dni.item_code, dni.qty, dni.custom_against_pbsow
            FROM `tabDelivery Note Item` dni
            WHERE dni.parent IN %(dn_wip_list)s
        """, {"dn_wip_list": dn_wip_list}, as_dict=True)

        # Group quantities by (dn_wip_name, item_code, custom_against_pbsow)
        item_qty_map = {}
        for i in dn_wip_items:
            key = (i.dn_wip_name, i.item_code, i.custom_against_pbsow)
            item_qty_map[key] = item_qty_map.get(key, 0) + i.qty

        # Fetch Stock Entry rates in bulk
        stock_entry_data = frappe.db.sql("""
            SELECT se.reference_number, sei.item_code, sei.basic_rate, sei.qty
            FROM `tabStock Entry` se
            JOIN `tabStock Entry Detail` sei ON se.name = sei.parent
            WHERE se.stock_entry_type = 'Material Transfer'
            AND se.docstatus = 1
            AND se.reference_number IN %(dn_wip_list)s
        """, {"dn_wip_list": dn_wip_list}, as_dict=True)

        # Store stock rates in a dictionary with weighted rate calculation
        stock_entries = {}
        for entry in stock_entry_data:
            key = (entry.reference_number, entry.item_code)
            if key in stock_entries:
                stock_entries[key]['total_value'] += entry.basic_rate * entry.qty
                stock_entries[key]['total_qty'] += entry.qty
            else:
                stock_entries[key] = {'total_value': entry.basic_rate * entry.qty, 'total_qty': entry.qty}

        # Calculate the correct weighted average rate
        stock_rates = {}
        for key, values in stock_entries.items():
            stock_rates[key] = values['total_value'] / values['total_qty'] if values['total_qty'] > 0 else 0

        amount = 0

        # Calculate total amount using correct stock rates
        for child in pb.item_table:
            total_item_qty = 0
            weighted_rate_sum = 0
            total_rate_qty = 0  # Used for calculating weighted avg

            for dn_wip in dn_wip_list:
                key = (dn_wip, child.item, child.docname)
                if key in item_qty_map:
                    item_qty = item_qty_map[key]
                    total_item_qty += item_qty

                    if (dn_wip, child.item) in stock_rates:
                        rate = stock_rates[(dn_wip, child.item)]
                        weighted_rate_sum += rate * item_qty
                        total_rate_qty += item_qty

            # Compute weighted average rate
            final_rate = weighted_rate_sum / total_rate_qty if total_rate_qty > 0 else 0

            amount += final_rate * total_item_qty
    return amount

def total_jl_cost(project, from_date, to_date):
    if from_date and to_date:
        journal_entry = frappe.db.sql("""
            SELECT SUM(c.debit_in_account_currency) AS cost
            FROM `tabJournal Entry` jl
            INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name
            WHERE c.project = %s AND jl.docstatus = 1 AND posting_date BETWEEN %s AND %s
            GROUP BY c.project
        """, (project,from_date,to_date), as_dict=True)
    else:
        journal_entry = frappe.db.sql("""
            SELECT SUM(c.debit_in_account_currency) AS cost
            FROM `tabJournal Entry` jl
            INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name
            WHERE c.project = %s AND jl.docstatus = 1
            GROUP BY c.project
        """, (project,), as_dict=True)
    data = round(journal_entry[0].cost, 2) if journal_entry else 0
    return data

def total_cost_by_timesheet(project, from_date, to_date):
    if from_date and to_date:
        timesheet = frappe.db.sql("""
        SELECT SUM(c.costing_amount) AS cost
        FROM `tabTimesheet` p
        INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name
        WHERE c.project = %s AND p.docstatus = 1 AND start_date BETWEEN %s AND %s
        GROUP BY c.project
    """, (project,from_date,to_date), as_dict=True)
    else:
        timesheet = frappe.db.sql("""
            SELECT SUM(c.costing_amount) AS cost
            FROM `tabTimesheet` p
            INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name
            WHERE c.project = %s AND p.docstatus = 1
            GROUP BY c.project
        """, (project,), as_dict=True)
    data = round(timesheet[0].cost, 2) if timesheet else 0
    return data

@frappe.whitelist()
def get_conditions(filters):
    conditions = []
    sql_filters = {}

    if filters.get("sales_order"):
        conditions.append("pb.sales_order = %(sales_order)s")
        sql_filters["sales_order"] = filters["sales_order"]

    if filters.get("project"):
        conditions.append("so.project = %(project)s")
        sql_filters["project"] = filters["project"]

    # if filters.get("from_date") and filters.get("to_date"):
    #     conditions.append("pb.date_of_budget BETWEEN %(from_date)s AND %(to_date)s")
    #     sql_filters["from_date"] = filters["from_date"]
    #     sql_filters["to_date"] = filters["to_date"]


    if filters.get("company"):
        conditions.append("pb.company = %(company)s")
        sql_filters["company"] = filters["company"]

    conditions_sql = " AND ".join(conditions) if conditions else "1=1"

    return conditions_sql, sql_filters

