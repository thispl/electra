# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import math
from math import floor

class CostEstimation(Document):
	def validate(self):
		master_sow = self.master_scope_of_work
		for msow in master_sow:
			if msow.msow:
				if frappe.db.exists('Master Scope of Work',msow.msow):
					msow_id = frappe.get_doc("Master Scope of Work",msow.msow)
				else:
					msow_id = frappe.new_doc("Master Scope of Work")
				msow_id.master_scope_of_work = msow.msow
				msow_id.desc = msow.msow_desc
				msow_id.save(ignore_permissions=True)

@frappe.whitelist()
def round(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

@frappe.whitelist()
def get_data(tc,ec,cp,gpp,tcc,tec,cpc,gppc,tcp,tpb,dp,dpc,cmp,netp,neta):
	if cmp == "MEP DIVISION - ELECTRA":
		tot = (round(float(tec) , 2)) + round(float(cpc), 2) + round(float(tcc), 2)
		nppc = (round(float(gppc), 2)) - (round(float(dpc), 2))
		tbp = (round(float(tcp), 2)) + (round(float(nppc), 2)) + (round(float(tot), 2)) + (round(float(tpb), 2))
		npp = (round(float(gpp), 2)) - (round(float(dp), 2))
		
		data  = ''
		data = "<table style='width:100%'>"
		data += "<tr><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:#e35310;color:white;font-weight:bold;'>TOTAL COST</td></tr>"
		data += "<tr style ='background-color:#878f99;color:white'><td colspan = 2 style ='text-align:left;text-align:center;border:1px solid black;color:white;font-weight:bold;'>S No</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Title</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Percentage(%)</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Amount(QAR)</td></tr>"
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>A</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Cost of the Project</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tcp), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>B</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Gross Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(gpp), 2),round(float(gppc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>C</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Discount</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(dp), 2),round(float(dpc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>D</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Net Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(npp),2),round(float(nppc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>E</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Business Promotion</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tpb), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black;border-right-color:#878f99;background-color:#878f99'></td><td colspan = 12 style ='text-align:center;border:1px solid black;background-color:#878f99;color:white;font-weight:bold;'>Total Bidding Price(A+D+E)</td><td colspan = 6 style ='color:white;background-color:#878f99;text-align:center;border:1px solid black;color:white;font-weight:bold;'>QAR  %s</td></tr>"%(round(float(tbp), 2))
		data += "</table>"
		
	if cmp != "MEP DIVISION - ELECTRA":
		tot = (round(float(tec) , 2)) + round(float(cpc), 2) + round(float(tcc), 2)
		nppc = (round(float(gppc), 2)) - (round(float(dpc), 2))
		tbp = (round(float(tcp), 2)) + (round(float(nppc), 2)) + (round(float(tot), 2)) + (round(float(tpb), 2))
		eng = (round(float(tcp), 2)) + (round(float(gppc), 2))
		npp = (round(float(gpp), 2)) - (round(float(dp), 2))
		
		data  = ''
		data = "<table style='width:100%'>"
		data += "<tr><td colspan = 20 style ='text-align:center;border:1px solid black;background-color:#e35310;color:white;font-weight:bold;'>TOTAL COST</td></tr>"
		data += "<tr style ='background-color:#878f99;color:white'><td colspan = 2 style ='text-align:left;text-align:center;border:1px solid black;color:white;font-weight:bold;'>S No</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Title</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Percentage(%)</td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black;color:white;font-weight:bold;'>Amount(QAR)</td></tr>"
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>A</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Cost of the Project</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tcp), 2))
		
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>B</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Overhead</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(tc), 2),round(float(tcc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>C</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Engineering Overhead</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(ec),2),round(float(tec), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>D</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Contigency</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(cp),2),round(float(cpc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>E</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Overhead</b>(B+C+D)</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tot),2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>F</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Gross Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(gpp), 2),round(float(gppc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>G</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Discount</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(dp), 2),round(float(dpc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>H</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Net Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s<td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(netp),2),round(float(neta), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>I</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Business Promotion</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tpb), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black;border-right-color:#878f99;background-color:#878f99'><td colspan = 12 style ='color:white;text-align:center;border:1px solid black;background-color:#878f99;color:white;font-weight:bold;'>Total Bidding Price(A+E+H+I)</td><td colspan = 6 style ='color:white;background-color:#878f99;text-align:center;border:1px solid black;color:white;font-weight:bold;'>QAR  %s</td></tr>"%(round(float(eng), 2))
		data += "</table>"
	return data
