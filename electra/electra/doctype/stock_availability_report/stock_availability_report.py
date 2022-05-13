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

class StockAvailabilityReport(Document):
      @frappe.whitelist()
      def get_data(self):
            item = frappe.get_value('Item',{'item_code':self.item_code},'item_code')
            rate = frappe.get_value('Item',{'item_code':self.item_code},'valuation_rate')
            group = frappe.get_value('Item',{'item_code':self.item_code},'item_group')
            price = frappe.get_value('Item Price',{'item_code':self.item_code},'price_list_rate')
            spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
            where `tabItem`.item_code = '%s' """%(self.item_code),as_dict=True)[0]
            data = ''
            stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
                  where item_code = '%s' """%(item),as_dict=True)
            data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;background-color:#6B8E23;" colspan=6><center>Stock Availability</center></th></tr>'
            data += '<tr><td style="padding:1px;border: 1px solid black;color:white;background-color:#6B8E23;"><b>Item Code</b></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><b>Item Name</b></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><b>Item Group</b></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><b>Item Price</b></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><b>Supplier Part No</b></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><b>cos</b></td></tr>'
            data += '<tr><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td></tr>'%(item,frappe.db.get_value('Item',item,'item_name'),group,price,spn["supplier_part_no",rate or ''])
            data += '<tr><td colspan = 3 style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><center><b>QTY</b></center></td><td style="padding:1px;border: 1px solid black;background-color:#6B8E23;color:white;"><center><b>UOM</b></center></td></tr>'
            i = 0
            for stock in stocks:
                  if stock.actual_qty > 0:
                        data += '<tr><td colspan = 3 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black">%s</td></tr>'%(stock.warehouse,stock.actual_qty,stock.stock_uom)
                        i += 1
            data += '</table>'
            if i > 0:
                  return data
            # data = """<table class='table table-bordered=1'>
            #       <tr>
            #       <td style="background-color:#6B8E23; padding:2px; color:white;border: 1px solid black; font-size:15px;">
            #             <center><b>S.No</b></center>
            #       <td style="background-color:#6B8E23; padding:2px;color:white; border: 1px solid black; font-size:15px;">
            #             <center><b>Item Code</b></center>
            #       <td style="background-color:#6B8E23; padding:2px; color:white;border: 1px solid black; font-size:15px;">
            #             <center><b>Item Name</b></center>
            #       <td style="background-color:#6B8E23; padding:2px;color:white; border: 1px solid black; font-size:15px;">
            #             <center><b>Category</b></center>
            #       <td style="background-color:#6B8E23;color:white; padding:2px; border: 1px solid black; font-size:15px;">
            #             <center><b>Description</b></center>
            #       <td style="background-color:#6B8E23; padding:2px; color:white;border: 1px solid black; font-size:15px;">
            #             <center><b>Supplier Part No</b></center>
            #       <td style="background-color:#6B8E23; padding:2px; color:white;border: 1px solid black; font-size:15px;">
            #             <center><b>Unit</b></center>
            #             <td style="background-color:#6B8E23; padding:2px;color:white; border: 1px solid black; font-size:15px;">
            #             <center><b>Warehouse</b></center>
            #       <td style="background-color:#6B8E23; padding:2px;color:white; border: 1px solid black; font-size:15px;">
            #             <center><b>Stock Available </b></center>
            #       </tr>"""
            # # item = frappe.get_all("Item",{'name':self.item_code},['*'])
            # s = 1
            # for i in item:
            # spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
            # where `tabItem`.item_code = '%s' """%(i.item_code),as_dict=True)[0]
            # stocks = frappe.db.sql("""select actual_qty,warehouse from tabBin where item_code = '%s' """%(i.name),as_dict=True)[0] or 0
            #       data += """
            #       <tr>
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><center><b>%s</b><center></td>
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td> 
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td>
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td> 
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td> 
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td>  
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td>
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><b>%s</b></td>
            #             <td style="padding:1px; border: 1px solid black; font-size:10px;"><center><b>%s</b><center></td>
            #       </tr>
            #       </tr>
            #       """ % (s,i.name,i.item_name,i.item_group,i.description,spn["supplier_part_no"],i.stock_uom,stocks["warehouse"],stocks["actual_qty"])
            #       s += 1
            

