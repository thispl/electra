import frappe

def execute(filters=None):
    columns = [
        {"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 200},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120}
    ]
    data = []
    
    # Get the list of sales and cost of goods sold accounts
    sales_accounts = frappe.get_list("Account", filters={"parent_account": "Sales"})
    cogs_accounts = frappe.get_list("Account", filters={"parent_account": "Cost of Goods Sold"})
    sales_account_names = [account.name for account in sales_accounts]
    cogs_account_names = [account.name for account in cogs_accounts]
    
    # Get the total debit and credit amounts for each account
    for account_name in sales_account_names + cogs_account_names:
        account = frappe.get_doc("Account", account_name)
        total_debit = 0
        total_credit = 0
        for entry in account.get("entries"):
            if entry.posting_date >= filters["from_date"] and entry.posting_date <= filters["to_date"]:
                if entry.account in sales_account_names + cogs_account_names:
                    total_debit += entry.debit
                    total_credit += entry.credit
        if total_debit != 0 or total_credit != 0:
            data.append({
                "account": account_name,
                "debit": total_debit,
                "credit": total_credit
            })
    
    # Calculate the gross profit
    gross_profit_debit = 0
    gross_profit_credit = 0
    for row in data:
        if row["account"] in sales_account_names:
            gross_profit_credit += row["credit"]
        elif row["account"] in cogs_account_names:
            gross_profit_debit += row["debit"]
    gross_profit = gross_profit_credit - gross_profit_debit
    
    # Add the gross profit row to the data
    data.append({
        "account": "Gross Profit",
        "debit": gross_profit_debit,
        "credit": gross_profit_credit
    })
    
    # Calculate the net profit
    net_profit_debit = sum([row["debit"] for row in data])
    net_profit_credit = sum([row["credit"] for row in data])
    net_profit = net_profit_credit - net_profit_debit
    
    # Add the net profit row to the data
    data.append({
        "account": "Net Profit",
        "debit": net_profit_debit,
        "credit": net_profit_credit
    })
    
    return columns, data
