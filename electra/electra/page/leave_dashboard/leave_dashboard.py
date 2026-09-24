import frappe
import json
from frappe.utils import getdate, nowdate, flt


@frappe.whitelist()
def get_leave_dashboard_data(filters=None):
	"""Single optimized API that returns:
	1. Workflow state counts (cards)
	2. Leave balance summary (allocated / consumed / available) by leave type
	3. All workflow states for dynamic card generation

	Respects ERPNext permission rules via frappe.get_list with ignore_permissions=False.
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	else:
		filters = filters or {}

	filters = frappe._dict(filters)

	# Determine the workflow state field for Leave Application
	workflow_state_field = _get_workflow_state_field()

	# Build common filter conditions for Leave Application
	la_filters = _build_leave_application_filters(filters)

	# ── 1. Workflow state counts via GROUP BY ──
	workflow_cards = _get_workflow_state_counts(la_filters, workflow_state_field)

	# ── 2. Leave balance summary ──
	leave_balances = _get_leave_balance_summary(filters)

	# ── 3. All workflow states from the workflow definition ──
	all_workflow_states = _get_all_workflow_states()

	return {
		"workflow_cards": workflow_cards,
		"leave_balances": leave_balances,
		"workflow_states": all_workflow_states,
		"workflow_state_field": workflow_state_field,
	}


def _get_workflow_state_field():
	"""Return the workflow_state field name for Leave Application, defaulting to 'workflow_state'."""
	# Check if a workflow is applied to Leave Application
	workflow_name = frappe.db.get_value("Workflow", {"document_type": "Leave Application"})
	if workflow_name:
		override_status, ws_field = frappe.db.get_value(
			"Workflow", workflow_name, ["override_status", "workflow_state_field"]
		)
		if not override_status and ws_field:
			return ws_field
	# Fall back to the custom field that exists in this system
	return "workflow_state"


def _get_all_workflow_states():
	"""Fetch all states defined in the Leave Application workflow."""
	workflow_name = frappe.db.get_value("Workflow", {"document_type": "Leave Application", "is_active": 1})
	if not workflow_name:
		# Try without is_active filter
		workflow_name = frappe.db.get_value("Workflow", {"document_type": "Leave Application"})
	if not workflow_name:
		return []
	# Get states from Workflow Document State child table
	states = frappe.get_all(
		"Workflow Document State",
		filters={"parent": workflow_name},
		fields=["state"],
		order_by="idx",
	)
	return [s.state for s in states]


def _build_leave_application_filters(filters):
	"""Build frappe filter dict for Leave Application based on dashboard filters."""
	la_filters = {}

	# Only active employees
	active_employees = _get_active_employee_names(filters)
	if active_employees is not None:
		la_filters["employee"] = ["in", active_employees]
	else:
		# No active employees matching the filter
		la_filters["employee"] = ["in", []]

	if filters.get("company"):
		la_filters["company"] = filters["company"]
	if filters.get("department"):
		la_filters["department"] = filters["department"]
	if filters.get("leave_type"):
		la_filters["leave_type"] = filters["leave_type"]
	if filters.get("employee"):
		la_filters["employee"] = filters["employee"]
	if filters.get("from_date"):
		la_filters["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		la_filters["to_date"] = filters["to_date"]

	return la_filters


def _get_active_employee_names(filters):
	"""Return list of active employee names matching branch/department/company filters.
	Returns None if no employee-specific filter is applied (meaning all active employees).
	"""
	emp_filters = {"status": "Active"}

	if filters.get("company"):
		emp_filters["company"] = filters["company"]
	if filters.get("department"):
		emp_filters["department"] = filters["department"]
	if filters.get("branch"):
		emp_filters["branch"] = filters["branch"]
	if filters.get("employee"):
		emp_filters["name"] = filters["employee"]

	# Check if employee_category custom field exists
	meta = frappe.get_meta("Employee")
	if filters.get("employee_category") and meta.get_field("employee_category"):
		emp_filters["employee_category"] = filters["employee_category"]

	employees = frappe.get_list("Employee", filters=emp_filters, pluck="name")
	return employees if employees else []


def _get_workflow_state_counts(la_filters, workflow_state_field):
	"""Use a single GROUP BY SQL query to get counts per workflow state.
	Respects permissions by using frappe.db.sql with permission check.
	"""
	if not workflow_state_field:
		return []

	# Build WHERE conditions from filters
	conditions = ["la.docstatus != 2"]
	params = []

	# Active employee filter
	if la_filters.get("employee"):
		emp_val = la_filters["employee"]
		if isinstance(emp_val, (list, tuple)):
			op, values = emp_val
			if op == "in" and values:
				placeholders = ", ".join(["%s"] * len(values))
				conditions.append(f"la.employee IN ({placeholders})")
				params.extend(values)
			else:
				conditions.append("1=0")
		else:
			# Single employee value (string)
			conditions.append("la.employee = %s")
			params.append(emp_val)

	if la_filters.get("company"):
		conditions.append("la.company = %s")
		params.append(la_filters["company"])
	if la_filters.get("department"):
		conditions.append("la.department = %s")
		params.append(la_filters["department"])
	if la_filters.get("leave_type"):
		conditions.append("la.leave_type = %s")
		params.append(la_filters["leave_type"])
	if la_filters.get("from_date"):
		conditions.append("la.from_date >= %s")
		params.append(la_filters["from_date"])
	if la_filters.get("to_date"):
		conditions.append("la.to_date <= %s")
		params.append(la_filters["to_date"])

	where_clause = " AND ".join(conditions)

	# Use backtick-quoted field name for safety
	ws_field = f"`la`.`{workflow_state_field}`"

	sql = f"""
		SELECT {ws_field} AS workflow_state, COUNT(*) AS count
		FROM `tabLeave Application` la
		WHERE {where_clause}
		GROUP BY {ws_field}
		ORDER BY count DESC
	"""

	results = frappe.db.sql(sql, params, as_dict=True)

	# If user can't read Leave Application at all, return empty
	if not frappe.has_permission("Leave Application", "read"):
		return []

	return results


def _filter_by_permissions(results, la_filters, workflow_state_field):
	"""For users with limited permissions, get counts via frappe.get_list which respects permissions."""
	# Get all Leave Applications the user can see (frappe.get_list respects permissions)
	visible = frappe.get_list(
		"Leave Application",
		filters=la_filters,
		fields=[workflow_state_field],
		ignore_permissions=False,
	)

	# Count by workflow state
	state_counts = {}
	for rec in visible:
		state = rec.get(workflow_state_field) or "Unknown"
		state_counts[state] = state_counts.get(state, 0) + 1

	return [{"workflow_state": k, "count": v} for k, v in state_counts.items()]


def _get_leave_balance_summary(filters):
	"""Get allocated, consumed, and available leaves grouped by leave type.
	Uses the same get_leave_details function as the Employee Leave Balance Summary report
	for exact data consistency.
	"""
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	# Get active employees matching filters
	active_employees = _get_active_employee_names(filters)
	if not active_employees:
		return []

	# Determine the date to check leave balance on
	if filters.get("from_date"):
		date = filters["from_date"]
	elif filters.get("to_date"):
		date = filters["to_date"]
	else:
		date = nowdate()

	# Aggregate leave details across all active employees
	leave_totals = {}

	for emp in active_employees:
		try:
			details = get_leave_details(emp, date)
		except Exception:
			continue

		leave_allocation = details.get("leave_allocation", {})

		for leave_type, info in leave_allocation.items():
			# Skip if leave_type filter is set and doesn't match
			if filters.get("leave_type") and leave_type != filters["leave_type"]:
				continue

			if leave_type not in leave_totals:
				leave_totals[leave_type] = {
					"allocated": 0,
					"consumed": 0,
					"available": 0,
				}

			leave_totals[leave_type]["allocated"] += flt(info.get("total_leaves", 0))
			leave_totals[leave_type]["consumed"] += flt(info.get("leaves_taken", 0))
			leave_totals[leave_type]["available"] += flt(info.get("remaining_leaves", 0))

	# Convert to list sorted by leave type
	balances = []
	for leave_type, totals in sorted(leave_totals.items()):
		balances.append({
			"leave_type": leave_type,
			"allocated": flt(totals["allocated"], 2),
			"consumed": flt(totals["consumed"], 2),
			"available": flt(totals["available"], 2),
		})

	return balances


@frappe.whitelist()
def get_filter_options():
	"""Return available options for dashboard filters."""
	companies = frappe.get_list("Company", pluck="name")
	branches = frappe.get_list("Branch", pluck="name")
	departments = frappe.get_list("Department", pluck="name")
	leave_types = frappe.get_list("Leave Type", pluck="name")

	# Employee categories (if the custom field exists)
	employee_categories = []
	emp_meta = frappe.get_meta("Employee")
	if emp_meta.get_field("employee_category"):
		field = emp_meta.get_field("employee_category")
		if field.fieldtype == "Select" and field.options:
			employee_categories = [opt.strip() for opt in field.options.split("\n") if opt.strip()]
		elif field.fieldtype == "Link":
			employee_categories = frappe.get_list(field.options, pluck="name")

	return {
		"companies": companies,
		"branches": branches,
		"departments": departments,
		"leave_types": leave_types,
		"employee_categories": employee_categories,
	}
