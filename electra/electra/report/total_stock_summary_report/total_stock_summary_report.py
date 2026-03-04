import frappe
from frappe import _
from frappe.query_builder.functions import Sum, Max
import re


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    stock, total_amount = get_total_stock(filters)
    return columns, stock + [total_amount]


def get_columns(filters):
    columns = [
        _("Item") + ":Link/Item:150",
        _("Description") + "::300",
        _("UOM") + ":Link/UOM:100",
        _("Current Qty") + ":Float:100",
        _("Valuation Rate") + ":Currency:100",
        _("Amount") + ":Currency:150",
    ]

    if filters.get("group_by") == "Warehouse":
        columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
    else:
        columns.insert(0, _("Company") + ":Link/Company:250")

    return columns


def get_total_stock(filters):
    bin = frappe.qb.DocType("Bin")
    item = frappe.qb.DocType("Item")
    wh = frappe.qb.DocType("Warehouse")
    excluded_warehouse= ['Work In Progress - EED', 'Work In Progress - INE', 'Work In Progress - MEP']
    query = (
        frappe.qb.from_(bin)
        .inner_join(item)
        .on(bin.item_code == item.item_code)
        .inner_join(wh)
        .on(wh.name == bin.warehouse)
        .where((bin.actual_qty != 0)
        # Added by Nandini
          & (~bin.warehouse.isin(excluded_warehouse)))
    )

    if filters.get("group_by") == "Warehouse":
        if filters.get("company"):
            query = query.where(wh.company == filters.get("company"))

        query = query.select(bin.warehouse).groupby(bin.warehouse)
    else:
        query = query.select(wh.company).groupby(wh.company)

    query = query.select(
        item.item_code.as_("item"),
        item.description,
        item.stock_uom.as_("uom"),
        Sum(bin.actual_qty).as_("current_qty"),
        Max(bin.valuation_rate).as_("valuation_rate"),
        (Sum(bin.valuation_rate * bin.actual_qty)).as_("amount"),
    ).groupby(item.item_code)

    result = query.run(as_dict=True)
    total_amount = sum(row["amount"] for row in result)
    return result, {"warehouse":"Total","amount":total_amount}


