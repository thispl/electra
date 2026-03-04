frappe.listview_settings['Stock Confirmation'] = {
    onload:function(listview){
            listview.filter_area.clear()
            listview.filter_area.add([[listview.doctype, "workflow_state", '=', "Pending for Confirmation"]]);
            listview.refresh();     
        }
    }