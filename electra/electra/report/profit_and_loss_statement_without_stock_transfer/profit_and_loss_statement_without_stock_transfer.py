# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import flt

from electra.electra.report.profit_and_loss_statement_without_stock_transfer.financial_statements import (
    get_columns,
    get_data,
    get_filtered_list_for_consolidated_report,
    get_period_list,
)

def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )
    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )
    
    exclude_account = "Sales - Stock Transfer"

    income = [
        row for row in income
        if not row.get("account_name", "").startswith(exclude_account)
    ]

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    net_profit_loss = get_net_profit_loss(
        income, expense, period_list, filters.company, filters.presentation_currency
    )

    data = []
    data.extend(format_data(income) or [])
    data.extend(format_data(expense) or [])
    if net_profit_loss:
        data.append(format_data([net_profit_loss])[0])

    columns = get_columns(
        filters.periodicity, period_list, filters.accumulated_values, filters.company
    )

    chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

    currency = filters.presentation_currency or frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )
    report_summary = get_report_summary(
        period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
    )

    return columns, data, None, chart, report_summary

def format_data(data):
    """Format data to ensure all numerical values are displayed with 2 decimal places."""
    for row in data:
        for key in row:
            if isinstance(row[key], (int, float)):
                row[key] = flt(row[key], 2)
    return data

def get_report_summary(
    period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
    net_income, net_expense, net_profit = 0.0, 0.0, 0.0

    # from consolidated financial statement
    if filters.get("accumulated_in_group_company"):
        period_list = get_filtered_list_for_consolidated_report(filters, period_list)

    for period in period_list:
        key = period if consolidated else period.key
        if income:
            net_income += flt(income[-2].get(key), 2)
        if expense:
            net_expense += flt(expense[-2].get(key), 2)
        if net_profit_loss:
            net_profit += flt(net_profit_loss.get(key), 2)

    if len(period_list) == 1 and periodicity == "Yearly":
        profit_label = _("Profit This Year")
        income_label = _("Total Income This Year")
        expense_label = _("Total Expense This Year")
    else:
        profit_label = _("Net Profit")
        income_label = _("Total Income")
        expense_label = _("Total Expense")

    return [
        {"value": f"{flt(net_income, 2):.2f}", "label": income_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "-"},
        {"value": f"{flt(net_expense, 2):.2f}", "label": expense_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "=", "color": "blue"},
        {
            "value": f"{flt(net_profit, 2):.2f}",
            "indicator": "Green" if net_profit > 0 else "Red",
            "label": profit_label,
            "datatype": "Currency",
            "currency": currency,
        },
    ]

def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
    total = 0
    net_profit_loss = {
        "account_name": "'" + _("Profit for the year") + "'",
        "account": "'" + _("Profit for the year") + "'",
        "warn_if_negative": True,
        "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
    }

    has_value = False

    for period in period_list:
        key = period if consolidated else period.key
        total_income = flt(income[-2][key], 2) if income else 0
        total_expense = flt(expense[-2][key], 2) if expense else 0

        net_profit_loss[key] = flt(total_income - total_expense, 2)

        if net_profit_loss[key]:
            has_value = True

        total += flt(net_profit_loss[key], 2)
        net_profit_loss["total"] = total

    if has_value:
        return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
    labels = [d.get("label") for d in columns[2:]]

    income_data, expense_data, net_profit = [], [], []

    for p in columns[2:]:
        if income:
            income_data.append(flt(income[-2].get(p.get("fieldname")), 2))
        if expense:
            expense_data.append(flt(expense[-2].get(p.get("fieldname")), 2))
        if net_profit_loss:
            net_profit.append(flt(net_profit_loss.get(p.get("fieldname")), 2))

    datasets = []
    if income_data:
        datasets.append({"name": _("Income"), "values": income_data})
    if expense_data:
        datasets.append({"name": _("Expense"), "values": expense_data})
    if net_profit:
        datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

    chart = {"data": {"labels": labels, "datasets": datasets}}

    if not filters.accumulated_values:
        chart["type"] = "bar"
    else:
        chart["type"] = "line"

    chart["fieldtype"] = "Currency"

    return chart
