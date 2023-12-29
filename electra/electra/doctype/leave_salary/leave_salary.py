# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import formatdate

class LeaveSalary(Document):
	pass
@frappe.whitelist()
def leave_salary_calculation(total_earnings,salary,gratuity,amount,leave_salary):
    lss= frappe.db.get_value('Employee',employee)
    sal = int(salary) + int(leave_salary) + int(amount) + int(gratuity)
    return sal
@frappe.whitelist()
def ticket_amount(ticket):
	at = frappe.db.get_value("Employee", {"employee_number": ticket},["air_ticket_allowance_"])
	frappe.errprint("HI")
		
	return at
		

@frappe.whitelist()
def leave_salary(leave_salary,join_date,emp_name,company,department,designation):
	salary = ''
	lea = frappe.get_all("Leave Salary",{'employee_number':leave_salary},['name'])
	if lea:
		salary = "<table style='width:100%'>"
		salary += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b>EMPLOYEE DETAILS</b></td></tr>"
		salary += "<tr style ='background-color:white;color:black'><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 10 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>" %("Employee ID",leave_salary,"Date of Joining",formatdate(join_date))
		salary += "<tr style ='background-color:white;color:black'><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 10 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>" %("Employee Name",emp_name,"Company",company)
		salary += "<tr style ='background-color:white;color:black'><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:left;border:1px solid black'><b>%s</b></td><td colspan = 10 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>" %("Department",department,"Designation",designation)
		salary += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b>VACATION DETAILS</b></td></tr>"
		salary += "<tr style ='background-color:white;color:black'><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 2 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 2 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>" %("S NO","Type","Service Start Date","Service End Date","Days","Vacation Start Date","Vacation End Date","Vacation Days","Extra Days","Rejoining Date")
		a = 0
		for i in lea:
			# frappe.errprint(i.name)
			a += 1
			his = frappe.db.get_value("Leave Salary",{'name':i.name},["type","joining_or_last_rejoining_date","date_of_service","leave_salary_days","vacation_start_date","vacation_end_date","vacation_days","extra_days","rejoining_date"]) 
			salary += "<tr style ='background-color:white;color:black'><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 2 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 2 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 1 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 3 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>" %(a,his[0] or "-",formatdate(his[1]) or "-",formatdate(his[2]) or "-",his[3] or "-",formatdate(his[4]) or "-",formatdate(his[5]) or "-",his[6] or "-",his[7] or "-",formatdate(his[8]) or "-")
		salary += "</table>"
	return salary



@frappe.whitelist()
def service_days(leave_salary_days,grade):
	frappe.errprint("HI")
	service = ''
	if grade == "STAFF":
		if int(leave_salary_days) >= 335:
			frappe.errprint("S E")
			service = "<table style='width:100%'>"
			service += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b>Eligible</b></td></tr>"
			service += "</table>"
		else:
			frappe.errprint("S NE")
			service = "<table style='width:100%'>"
			service += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b> Not Eligible</b></td></tr>"
			service += "</table>"
	elif grade == "NON STAFF" :
		if int(leave_salary_days) >= 365:
			frappe.errprint("W E")
			service = "<table style='width:100%'>"
			service += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b>Eligible</b></td></tr>"
			service += "</table>"
		else:
			frappe.errprint("W NE")
			service = "<table style='width:100%'>"
			service += "<tr width = 100%><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:orange'><b> Not Eligible</b></td></tr>"
			service += "</table>"

	return service

# @frappe.whitelist()
# def service_date(employee,type):
# 	if type == "Leave Salary Encashment"
# 	sd = frappe.db.get_value("Leave Salary", {"employee_number": employee},["date_of_service"])
# 	frappe.errprint("HI")
		
# 	return sd

# @frappe.whitelist()
# def rejoin_date(employee_number):
# 	rejoin = frappe.db.sql("""select rejoining_date from `tabLeave Salary` where employee_number = '%s' """ %(employee_number),as_dict=True)[0] or "-"
	
	# rejoining = frappe.get_value("Leave Salary",{'employee_number':employee_number},['rejoining_date'])[0]

	# frappe.errprint(rejoin)
	
	return rejoin




	
	



