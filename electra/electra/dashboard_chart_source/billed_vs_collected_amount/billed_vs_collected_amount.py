import frappe
from frappe import _
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get_result
from frappe.utils import getdate
from frappe.utils.dashboard import cache_source
from frappe.utils.dateutils import get_period

@frappe.whitelist()
@cache_source
def get_data(
    chart_name=None,
    chart=None,
    no_cache=None,
    filters=None,
    from_date=None,
    to_date=None,
    timespan=None,
    time_interval=None,
    heatmap_year=None,
) -> dict[str, list]:
    if filters:
        filters = frappe.parse_json(filters)

    total = get_records("grand_total", filters.get("company"))
    # frappe.errprint(total)

    # return {
    # "labels": [get_period(r[0], filters.get("time_interval")) for r in dose2],
    # "datasets": [   
    # {"name": _("Dose2 Count"), "values": [r[1] for r in dose2]},
    # ],
    # }

def get_records(
    company: str ,grand_total: str
) -> tuple[tuple[str]]:
    filters = [
        ["Sales Invoice", "company", "=", company],
    ]

    data = frappe.db.sql(
    """select sum(grand_total) as grand_total from `tabSales Invoice` where company = '%s' group by company"""%(filters.get("company"))
    )
    # frappe.errprint(data)
    return data