# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file
from frappe.utils.file_manager import get_file
from datetime import date, timedelta, datetime
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
import re
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
from six import BytesIO, string_types
from frappe.utils import (
    flt,
    cint,
    cstr,
    get_html_format,
    get_url_to_form,
    gzip_decompress,
    format_duration,
)

class ProductSearch(Document):
	@frappe.whitelist()
	def get_data(self):
		aa = self.item_code
		item = frappe.get_value('Item',{'item_code':self.item_code},'item_code')
		rate = frappe.get_value('Item',{'item_code':self.item_code},'valuation_rate')
		group = frappe.get_value('Item',{'item_code':self.item_code},'item_group')
		des = frappe.get_value('Item',{'item_code':self.item_code},'description')
		price = frappe.get_value('Item Price',{'item_code':self.item_code,'price_list':'Cost'},'price_list_rate')
		c_s_p = frappe.get_value('Item Price',{'item_code':self.item_code,'price_list':'Standard Selling'},'price_list_rate') or 0
		spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
		where `tabItem`.item_code = '%s' """%(self.item_code),as_dict=True)[0]
		csp = 'Current Selling Price'
		cpp = 'Current Purchase Price'
		cost = 'COST'
		pso = 'Pending Sales order'
		po ='Total Purchase Order'
		ppo = 'Pending Purchase order'
		cspp_rate = 0
		cppp_rate = 0
		psoc = 0
		del_total = 0
		ppoc = 0
		ppoc_total = 0
		cspp_query = frappe.db.sql("""select `tabSales Order Item`.rate as rate, `tabSales Order`.creation from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' order by `tabSales Order`.creation """ % (item), as_dict=True)
		if cspp_query:
			cspp = cspp_query[-1]
			cspp_rate = cspp['rate']

		cppp_query = frappe.db.sql("""select `tabPurchase Order Item`.rate as rate, `tabPurchase Order`.creation  from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' order by `tabPurchase Order`.creation """ % (item), as_dict=True)
		if cppp_query:
			cppp = cppp_query[-1]
			cppp_rate = cppp['rate']


		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
        left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
        where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']		

		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		ppoc_total = new_po['qty'] - new_po['d_qty']	


		a = frappe.db.sql("""select `tabPurchase Receipt Item`.purchase_order as name from `tabPurchase Receipt`
			left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
			where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		b = frappe.db.sql("""select `tabPurchase Receipt`.name as name from `tabPurchase Receipt`
			left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
			where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		data = ''
		stocks_query = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
			where item_code = '%s' """%(item),as_dict=True)
		if stocks_query:
			stocks = stocks_query
		data += '<table class="table table-bordered" style="width:50%"><tr><th style="padding:1px;border: 1px solid black;background-color:#fe3f0c;" colspan=4><center>PRODUCT SEARCH</center></th></tr>'
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>Item Code</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(item)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Name</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(frappe.db.get_value('Item',item,'item_name'))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Group</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(group)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(pso,del_total)
		if ppoc_total != 0.0:
			data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total)
		else:
			data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total) 
		if ppoc_total > 0 :
			ppoc_date_query = frappe.db.sql("""select `tabPurchase Order Item`.schedule_date  as date from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' """ % (item), as_dict=True)[0]
			if ppoc_date_query:
				po_date = ppoc_date_query['date']
			
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(csp,(c_s_p))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></td></tr>'
		i = 0
		cou = 0
		tot = 'Total'
		uom = 'Nos'
		for stock in stocks_query:
			if int(stock.actual_qty) >= 0:
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house == stock.warehouse:        
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')
					i += 1
					cou += stock.actual_qty

		for stock in stocks_query:
			if int(stock.actual_qty) >= 0:
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house != stock.warehouse:        
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')
					i += 1
					cou += stock.actual_qty
		data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td></tr>'%(tot,int(cou),uom)
		data += '</table>'
		# if i > 0:
		return data

	@frappe.whitelist()
	def get_pod(self):
		print("HI")
		
		item = frappe.get_value('Item',{'item_code':self.item_code},'item_code')
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """ % (item), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
			
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		    left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		    where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
			
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if ppoc_total == 0.0 :
			frappe.msgprint("No Pending Purchase Receipt")
			data = ''
		else:
			data = ''
			data += '<table class="table table-bordered" style="width:50%"><tr><th style="padding:1px;border: 1px solid black;background-color:#fe3f0c;" colspan=3><center>Pending PO Details</center></th></tr>'
			data += '<tr><td style="padding:1px;width:33%;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: center"><b>Purchase Order</b></td><td style="padding:1px;width:33%;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: center"><b>Expected Date of Arrival</b></td><td style="padding:1px;width:33%;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: center"><b>Pending Qty</b></td></tr>'
			sa = frappe.db.sql(""" select parent,qty,schedule_date,received_qty,rate from `tabPurchase Order Item` where `tabPurchase Order Item`.item_code = '%s' """ %(item),as_dict=True)
			for i in sa:
				if i.qty == i.received_qty:
					pass
				else:
					sb = frappe.get_doc("Purchase Order", i.parent)
					if sb.docstatus == 1 and sb.status!= "Closed":
						pending_qty = i.qty - i.received_qty
						data += '<tr><td style="border: 1px solid black;text-align: center"><b>%s</b></td><td style="border: 1px solid black;text-align: center"><b>%s</b></td><td style="border: 1px solid black;text-align: center"><b>%s</b></td></tr>' %(i.parent,format_date(i.schedule_date),pending_qty)

			print(data)
			data += '</table>'
		return data

	@frappe.whitelist()
	def get_data_perm(self):
		aa = self.item_code
		item = frappe.get_value('Item',{'item_code':self.item_code},'item_code')
		rate = frappe.get_value('Item',{'item_code':self.item_code},'valuation_rate')
		group = frappe.get_value('Item',{'item_code':self.item_code},'item_group')
		des = frappe.get_value('Item',{'item_code':self.item_code},'description')
		price = frappe.get_value('Item Price',{'item_code':self.item_code,'price_list':'Cost'},'price_list_rate')
		c_s_p = frappe.get_value('Item Price',{'item_code':self.item_code,'price_list':'Standard Selling'},'price_list_rate') or 0
		spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
		where `tabItem`.item_code = '%s' """%(self.item_code),as_dict=True)[0]
		csp = 'Current Selling Price'
		cpp = 'Current Purchase Price'
		cost = 'COST'
		pso = 'Pending Sales order'
		po ='Total Purchase Order'
		ppo = 'Pending Purchase order'
		cspp_rate = 0
		cppp_rate = 0
		del_total = 0
		psoc = 0
		ppoc = 0
		ppoc_total = 0
		cspp_query = frappe.db.sql("""select `tabSales Order Item`.rate as rate, `tabSales Order`.creation from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' order by `tabSales Order`.creation """ % (item), as_dict=True)
		if cspp_query:
				cspp = cspp_query[-1]
				cspp_rate = cspp['rate']

		cppp_query = frappe.db.sql("""select `tabPurchase Order Item`.rate as rate, `tabPurchase Order`.creation  from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' order by `tabPurchase Order`.creation """ % (item), as_dict=True)
		if cppp_query:
				cppp = cppp_query[-1]
				cppp_rate = cppp['rate']

		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
        left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
        where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']		
				
		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		ppoc_total = new_po['qty'] - new_po['d_qty']	



		a = frappe.db.sql("""select `tabPurchase Receipt Item`.purchase_order as name from `tabPurchase Receipt`
				left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
				where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"

		b = frappe.db.sql("""select `tabPurchase Receipt`.name as name from `tabPurchase Receipt`
				left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
				where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		
		data = ''
		stocks_query = frappe.db.sql("""select actual_qty,warehouse,valuation_rate,stock_uom,stock_value from tabBin
				where item_code = '%s' """%(item),as_dict=True)
		if stocks_query:
				stocks = stocks_query
		data += '<table class="table table-bordered" style="width:50%"><tr><th style="padding:1px;border: 1px solid black;background-color:#fe3f0c;" colspan=5><center>PRODUCT SEARCH</center></th></tr>'
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>Item Code</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(item)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Name</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(frappe.db.get_value('Item',item,'item_name'))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Group</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(group)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(pso,del_total)
		if ppoc_total != 0.0:
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total)
		else:
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total) 
		if ppoc_total > 0 :
				ppoc_date_query = frappe.db.sql("""select `tabPurchase Order Item`.schedule_date  as date from `tabPurchase Order`
				left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
				where `tabPurchase Order Item`.item_code = '%s' """ % (item), as_dict=True)[0]
				if ppoc_date_query:
					po_date = ppoc_date_query['date']
			
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(csp,(c_s_p))
		
		
		if not frappe.session.user == "anoop@marazeemqatar.com":
			data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>COST</b></center></td></tr>'
		
		if frappe.session.user == "anoop@marazeemqatar.com":
		
			if frappe.session.user == "anoop@marazeemqatar.com" and group == "Eyenor" or group == "NVS" or group == "Secnor":
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>COST</b></center></td></tr>'
			else:
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></td></tr>'
			
		
		
		
		i = 0
		cou = 0
		tot = 'Total'
		uom = 'Nos'
		for stock in stocks_query:
			if stock.actual_qty >= 0:       
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house == stock.warehouse:                        
						
					if not frappe.session.user == "anoop@marazeemqatar.com":
						data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
					
					if frappe.session.user == "anoop@marazeemqatar.com":
					
						if frappe.session.user == "anoop@marazeemqatar.com" and group == "Eyenor" or group == "NVS" or group == "Secnor":
							data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
						else:
							data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 2 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')			
					
					
					
					
					
					i += 1
					cou += stock.actual_qty  

		for stock in stocks_query:
			if stock.actual_qty >= 0:       
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house != stock.warehouse:                        
						
					if not frappe.session.user == "anoop@marazeemqatar.com":
						data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
					
					if frappe.session.user == "anoop@marazeemqatar.com":

						if frappe.session.user == "anoop@marazeemqatar.com" and group == "Eyenor" or group == "NVS" or group == "Secnor":
							data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
						
						else:
							data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 2 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')
					                     
					
					
					
					
					i += 1
					cou += stock.actual_qty  
		
		
		if not frappe.session.user == "anoop@marazeemqatar.com":
			data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>-</b></center></td></tr>'%(tot,int(cou),uom)
		
		if frappe.session.user == "anoop@marazeemqatar.com":

			if frappe.session.user == "anoop@marazeemqatar.com" and group == "Eyenor" or group == "NVS" or group == "Secnor":
				data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>-</b></center></td></tr>'%(tot,int(cou),uom)
			
			else:
				data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td></tr>'%(tot,int(cou),uom)
		
		
		
		
		data += '</table>'
		# if i > 0:
		return data




