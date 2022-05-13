# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now, date_diff
from erpnext.stock.utils import add_additional_uom_columns
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition

from erpnext.stock.report.stock_ageing.stock_ageing import get_fifo_queue, get_average_age

from six import iteritems

def execute(filters=None):
    if not filters: filters = {}
    
    validate_filters(filters)
    stock_value_in_sc = 0

    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    include_uom = filters.get("include_uom")
    columns = get_columns(filters)
    items = get_items(filters)
    sle = get_stock_ledger_entries(filters, items)

    if filters.get('show_stock_ageing_data'):
        filters['show_warehouse_wise_stock'] = True
        item_wise_fifo_queue = get_fifo_queue(filters, sle)

    if not sle:
        return columns, []

    if filters.get("currency"):
        columns.extend([
            {"label": _("Currency"), "fieldname": "sc_currency", "fieldtype": "Data", "width": 80},
            {"label": _("Balance Value"), "fieldname": "sc_value", "fieldtype": "Float", "width": 100}
            ])

    if filters.get('warehouse'):
        filters.warehouse = frappe.parse_json(filters.get('warehouse'))

    iwb_map = get_item_warehouse_map(filters, sle)
    item_map = get_item_details(items, sle, filters)
    item_reorder_detail_map = get_item_reorder_details(item_map.keys())

    data = []
    test = []
    conversion_factors = {}

    _func = lambda x: x[1]
    item_head = []
    for (company, item, warehouse) in sorted(iwb_map):
        if not item in item_head:
            item_info = get_parent_details(item, filters)
            data.append({
                'item_code': frappe.get_value("Item",item,"item_name"),
                'bal_qty': item_info.bal_qty,
                'indent': 0
                })
            item_head.append(item)
        if item_map.get(item):
            qty_dict = iwb_map[(company, item, warehouse)]
            item_reorder_level = 0
            item_reorder_qty = 0
            if item + warehouse in item_reorder_detail_map:
                item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
                item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

            supplier = supplier_part_no = ''
            supplier_info = frappe.get_value('Item Supplier',{'parent':item},['supplier','supplier_part_no'])
            if supplier_info:
                supplier = supplier_info[0]
                supplier_part_no = supplier_info[1]
            report_data = {
                'item_code': item,
                # 'item_name':'test',
                'warehouse': warehouse,
                'company': company,
                'supplier': supplier,
                # 'indent': 1,
                'supplier_part_no': supplier_part_no,
                'bal_val_cur':frappe.db.get_value('Company',company, "default_currency"),
                'reorder_level': item_reorder_level,
                'reorder_qty': item_reorder_qty,
                'indent': 1
            }
            report_data.update(item_map[item])
            report_data.update(qty_dict)

            if include_uom:
                conversion_factors.setdefault(item, item_map[item].conversion_factor)

            if filters.get('show_stock_ageing_data'):
                fifo_queue = item_wise_fifo_queue[(item, warehouse)].get('fifo_queue')

                stock_ageing_data = {
                    'average_age': 0,
                    'earliest_age': 0,
                    'latest_age': 0
                }
                if fifo_queue:
                    fifo_queue = sorted(filter(_func, fifo_queue), key=_func)
                    if not fifo_queue: continue

                    stock_ageing_data['average_age'] = get_average_age(fifo_queue, to_date)
                    stock_ageing_data['earliest_age'] = date_diff(to_date, fifo_queue[0][1])
                    stock_ageing_data['latest_age'] = date_diff(to_date, fifo_queue[-1][1])

                report_data.update(stock_ageing_data)	
            data.append(report_data)

    add_additional_uom_columns(columns, data, include_uom, conversion_factors)
    sc_val_cur = ''
    sc_val = 0
    
    for d in data:
        status = 'Ideal Quantity'
        if d['indent'] != 0:
            if int(d['bal_qty']) <= int(d['reorder_level']):
                status = 'Low Quantity'

            frozen = frappe.get_value('Item',d['item_code'],'disabled')
            if frozen:
                status = 'Frozen Item'	


            if filters.get("currency"):
                default_currency = d['bal_val_cur']
                selected_currency = filters.currency
                exchange_rate = frappe.get_value('Currency Exchange',{'from_currency':default_currency,'to_currency':selected_currency},['exchange_rate'])
                if filters.get('currency') == default_currency:
                    exchange_rate = 1
                sc_val_cur = frappe.db.get_value('Currency',selected_currency,['name'])
                sc_val = d['bal_val'] * flt(exchange_rate)	

            # if no stock ledger entry found return
            converted_value = {
                'sc_currency': sc_val_cur,
                'sc_value' : sc_val,
                'status': status
            }
            d.update(converted_value)
        frappe.errprint(data)
    return columns,data

def get_columns(filters):
    """return columns"""

    columns = [
        # {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 400},
        # {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data","width": 200},
        {"label": _("Category"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 100},
        # {"label": _("Category"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Data","width": 80},
        {"label": _("Part No."), "fieldname": "supplier_part_no", "fieldtype": "Data", "width": 100},
        # {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 300},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 200},
        {"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Data", "width": 100, "convertible": "qty"},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]

    if filters.get('show_stock_ageing_data'):
        columns += [{'label': _('Average Age'), 'fieldname': 'average_age', 'width': 100},
        {'label': _('Earliest Age'), 'fieldname': 'earliest_age', 'width': 100},
        {'label': _('Latest Age'), 'fieldname': 'latest_age', 'width': 100}]

    if filters.get('show_variant_attributes'):
        columns += [{'label': att_name, 'fieldname': att_name, 'width': 100} for att_name in get_variants_attributes()]

    return columns

def get_conditions(filters):
    conditions = ""
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if filters.get("to_date"):
        conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
    else:
        frappe.throw(_("'To Date' is required"))

    if filters.get("company"):
        conditions += " and sle.company = '%s'" % filters.get("company")

    if filters.get("warehouse_type") and not filters.get("warehouse"):
        conditions += " and exists (select name from `tabWarehouse` wh \
            where wh.warehouse_type = '%s' and sle.warehouse = wh.name)"%(filters.get("warehouse_type"))

    return conditions

def get_stock_ledger_entries(filters, items):
    item_conditions_sql = ''
    if items:
        item_conditions_sql = ' and sle.item_code in ({})'\
            .format(', '.join([frappe.db.escape(i, percent=False) for i in items]))

    conditions = get_conditions(filters)
    if filters.warehouse:
        conditions += 'and '
        count = len(filters.warehouse)
        for warehouse in filters.warehouse:
            count -= 1
            parent_wh = frappe.db.exists('Warehouse',{'is_group':1,'name': warehouse})
            if parent_wh:
                child_wh = []
                child_whs = frappe.get_all('Warehouse',{'parent_warehouse':parent_wh},['name'])
                for c in child_whs:
                    child_wh.append(c.name)
                conditions += "sle.warehouse in {0}".format(tuple(child_wh))
            if not parent_wh:
                conditions += "sle.warehouse = '%s'" %(warehouse)
            if count:
                conditions += " or "		
            

    query = """select
            sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
            sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
            sle.item_code as name, sle.voucher_no
        from
            `tabStock Ledger Entry` sle force index (posting_sort_index)
        where sle.docstatus < 2 %s %s
        order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty""" % (item_conditions_sql, conditions)	

    return frappe.db.sql(query, as_dict=1)

def get_item_warehouse_map(filters, sle):
    iwb_map = {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    for d in sle:
        key = (d.company, d.item_code, d.warehouse)
        if key not in iwb_map:
            iwb_map[key] = frappe._dict({
                "opening_qty": 0.0, "opening_val": 0.0,
                "in_qty": 0.0, "in_val": 0.0,
                "out_qty": 0.0, "out_val": 0.0,
                "bal_qty": 0.0, "bal_val": 0.0,
                "val_rate": 0., "sc_val":0.0,
                "sc_val_cur":frappe.db.get_value('Company',d.company,['default_currency']),
            })

        qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

        if d.voucher_type == "Stock Reconciliation":
            qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
        else:
            qty_diff = flt(d.actual_qty)

        value_diff = flt(d.stock_value_difference)

        if d.posting_date < from_date:
            qty_dict.opening_qty += qty_diff
            qty_dict.opening_val += value_diff

        elif d.posting_date >= from_date and d.posting_date <= to_date:
            if qty_diff > 0:
                qty_dict.in_qty += qty_diff
                qty_dict.in_val += value_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
                qty_dict.out_val += abs(value_diff)

        qty_dict.val_rate = d.valuation_rate
        qty_dict.bal_qty += qty_diff
        qty_dict.bal_val += value_diff

    iwb_map = filter_items_with_no_transactions(iwb_map)
    return iwb_map

def filter_items_with_no_transactions(iwb_map):
    for (company, item, warehouse) in sorted(iwb_map):
        qty_dict = iwb_map[(company, item, warehouse)]

        no_transactions = True
        float_precision = cint(frappe.db.get_default("float_precision")) or 3
        for key, val in iteritems(qty_dict):
            val = flt(val, float_precision)
            qty_dict[key] = val
            if key != "val_rate" and val:
                no_transactions = False

        if no_transactions:
            iwb_map.pop((company, item, warehouse))

    return iwb_map

def get_items(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append("item.name=%(item_code)s")
    else:
        if filters.get("brand"):
            conditions.append("item.brand=%(brand)s")
        if filters.get("item_group"):
            conditions.append(get_item_group_condition(filters.get("item_group")))

    items = []
    if conditions:
        items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
            .format(" and ".join(conditions)), filters)
    return items

def get_item_details(items, sle, filters):
    item_details = {}
    if not items:
        items = list(set([d.item_code for d in sle]))

    if not items:
        return item_details

    cf_field = cf_join = ""
    if filters.get("include_uom"):
        cf_field = ", ucd.conversion_factor"
        cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s" \
            % frappe.db.escape(filters.get("include_uom"))

    res = frappe.db.sql("""
        select
            item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom %s
        from
            `tabItem` item
            %s
        where
            item.name in (%s)
    """ % (cf_field, cf_join, ','.join(['%s'] *len(items))), items, as_dict=1)

    for item in res:
        item_details.setdefault(item.name, item)

    if filters.get('show_variant_attributes', 0) == 1:
        variant_values = get_variant_values_for(list(item_details))
        item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

    return item_details

def get_item_reorder_details(items):
    item_reorder_details = frappe._dict()

    if items:
        item_reorder_details = frappe.db.sql("""
            select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
            from `tabItem Reorder`
            where parent in ({0})
        """.format(', '.join([frappe.db.escape(i, percent=False) for i in items])), as_dict=1)

    return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

def validate_filters(filters):
    if not (filters.get("item_code") or filters.get("warehouse")):
        sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
        if sle_count > 500000:
            frappe.throw(_("Please set filter based on Item or Warehouse due to a large amount of entries."))

def get_variants_attributes():
    '''Return all item variant attributes.'''
    return [i.name for i in frappe.get_all('Item Attribute')]

def get_variant_values_for(items):
    '''Returns variant values for items.'''
    attribute_map = {}
    for attr in frappe.db.sql('''select parent, attribute, attribute_value
        from `tabItem Variant Attribute` where parent in (%s)
        ''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
            attribute_map.setdefault(attr['parent'], {})
            attribute_map[attr['parent']].update({attr['attribute']: attr['attribute_value']})

    return attribute_map

def get_parent_details(item, filters):
    conditions = get_conditions(filters)
    result = frappe.db.sql('''select sum(sle.actual_qty) as bal_qty from `tabStock Ledger Entry` sle where sle.item_code = %(item)s {condition}'''.format(condition=conditions), {'item': item}, as_dict=1)
    return result[0] if result else frappe._dict({'bal_qty': 0.0})