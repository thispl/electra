frappe.listview_settings['Material Transfer Inter Company'] = {
	onload: function(frm) {
		if (!frappe.route_options) {
				frappe.call({
					"method" : "frappe.client.get",
					args:{
						doctype: 'User Permission',
						filters: {
							"user": frappe.session.user,
							"allow": "Company"
						},
						fields: ['for_value']
					},
					callback:function(r){
						console.log(r.message.for_value)
						frappe.route_options = {
							"source_company": r.message.for_value
						};
					}
				})
			
		}
	}
}