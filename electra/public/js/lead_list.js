frappe.listview_settings['Lead'] = {
	onload: function(listview) {
		if (!frappe.route_options){ //remove this condition if not required
			frappe.route_options = {
				"status": ["=", ""]
			};
		}
	}
};