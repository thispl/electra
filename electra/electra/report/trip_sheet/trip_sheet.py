# Copyright (c) 2024, Abdulla and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		_("Customer") + ":Link/Customer:200",
		_("Site") + ":Link/Customer:200",
		_("Trip") + ":Link/Trip:200",
		_("QR/ TRIP") + ":Link/Trip:50",
		_("Total") + ":Currency:100",
		_("Driver") + ":Data/:70",
		_("VEH") + ":Link/vehicle:100",
		_("Card") + ":Data/:70",
		_("GAL/LTR/TRIP") + ":Data/:100",

	]
	return columns

def get_data(filters):	
	data = []
	
	# trip_filters = {}
	# # if filters.get("customer"):
	# # 	trip_filters["customer"] = filters.get("customer")
	# if filters.get("vehicle"):
	# 	trip_filters["vehicle_number"] = filters.get("vehicle")


	if filters.get("vehicle_number"):
		trips = frappe.db.get_all("Trip", filters={"vehicle_number":filters.get("vehicle_number")}, fields=["customer", "name", "total", "driver","vehicle_number","location"])
		
		for trip in trips:
			trip_doc = frappe.get_doc("Trip", trip.name)
			for j in trip_doc.get("trip_item",[]):
				row = [
					trip.customer,
					trip.location,
					trip.name,
					j.rate, 
					trip.total,
					trip.driver,
					trip.vehicle_number,
					j.item_code,
					j.uom,
					
				]
				data.append(row)
	else:
		trips = frappe.db.get_all("Trip",["customer", "name", "total", "driver","vehicle_number","location"])
		
		for trip in trips:
			trip_doc = frappe.get_doc("Trip", trip.name)
			for j in trip_doc.get("trip_item",[]):
				row = [
					trip.customer,
					trip.location,
					trip.name,
					j.rate, 
					trip.total,
					trip.driver,
					trip.vehicle_number,
					j.item_code,
					j.uom,
					
				]
				data.append(row)
	return data
