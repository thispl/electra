// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
let search_docs=["Quotation", "Sales Invoice", "Sales Order", "Material Request", "Purchase Order", "Purchase Invoice", "Item"]
frappe.ui.form.LinkSelector.prototype.make = function() {
	// console.log("---------make------")
		var me = this;
		this.start = 0;
		let fields = [
				
				// {
				// 	fieldtype: "HTML", fieldname: "results"
				// },
				// {
				// 	fieldtype: "Button", fieldname: "more", label: __("More"), click: () => {
				// 		me.start += 20;
				// 		me.search();
				// 	}
				// }
			]

		// if(this.doctype in search_docs){
		if(jQuery.inArray(this.doctype, search_docs) !== -1){
			fields.push({
					fieldtype: "Data", fieldname: "txt", label: __("Beginning with"),
					description: __("You can use wildcard %"),hidden:1
				})
			// fields.push({
			// 		fieldtype: "Column Break", fieldname: "col_1"})
			fields.push({
					fieldtype: "Data", fieldname: "name", label: __("Name")})
			fields.push({
					fieldtype: "Column Break", fieldname: "col_2"})
			fields.push({
					fieldtype: "Data", fieldname: "description", label: __("Description")})
			fields.push({
					fieldtype: "Section Break", fieldname: "sec_1"})
		}
		else{
			fields.push({
					fieldtype: "Data", fieldname: "txt", label: __("Beginning with"),
					description: __("You can use wildcard %"),hidden:0
				})
		}
		fields.push({
					fieldtype: "HTML", fieldname: "results"
				})
			fields.push({
					fieldtype: "Button", fieldname: "more", label: __("More"), click: () => {
						me.start += 20;
						me.search();
					}
				})

		this.dialog = new frappe.ui.Dialog({
			title: __("Select {0}", [(this.doctype == '[Select]') ? __("value") : __(this.doctype)]),
			fields: fields,
			primary_action_label: __("Search"),
			primary_action: function () {
				me.start = 0;
				me.search();
			}
		});

	
		if(jQuery.inArray(this.doctype, search_docs) !== -1){
			console.log("---------e.which-----------")
			if (this.name)
				this.dialog.fields_dict.name.set_input(this.name);
			if (this.description)
				this.dialog.fields_dict.description.set_input(this.description);
			this.dialog.get_input("name").on("keydown", function (e) {
				console.log(e.which)
				// if (e.which === 13) {
					me.start = 0;
					me.search();
				// }
			});
			this.dialog.get_input("description").on("keydown", function (e) {
				console.log(e.which)
				// if (e.which === 13) {
					me.start = 0;
					me.search();
				// }
			});
		}else{
			if (this.txt)
				this.dialog.fields_dict.txt.set_input(this.txt);
			this.dialog.get_input("txt").on("keypress", function (e) {
			if (e.which === 13) {
				me.start = 0;
				me.search();
			}
		});
		}
		
		this.dialog.show();
		this.search();
}

frappe.ui.form.LinkSelector.prototype.search = function() {
	// console.log("-------search------------")
	var name_data = null
	var description_data = null
	if(jQuery.inArray(this.doctype, search_docs) !== -1){
		var args = {
			txt: '',
			// txt: this.dialog.fields_dict.txt.get_value(),
			// filters:{"name": this.dialog.fields_dict.name.get_value(),"description": this.dialog.fields_dict.description.get_value()},
			// name: this.dialog.fields_dict.name.get_value(),
			// description: this.dialog.fields_dict.description.get_value(),
			searchfield: "name",
			start: this.start
		};
		name_data = this.dialog.fields_dict.name.get_value()
		description_data = this.dialog.fields_dict.description.get_value()
			// console.log("args----")
			// console.log(args.filters)
		if(name_data && !description_data){
			args.filters={"name": ["like","%"+name_data+"%"]}
			args.filters["name"] = ["like","%"+name_data+"%"]
		}
		if(description_data && !name_data){
			args.filters={"description": ["like","%"+description_data+"%"]}
			args.filters["description"] = ["like","%"+description_data+"%"]
		}
		if(name_data && description_data){
			args.filters={"name": ["like","%"+name_data+"%"], "description": ["like","%"+description_data+"%"]}
			args.filters["name"] = ["like","%"+name_data+"%"]
			args.filters["description"] = ["like","%"+description_data+"%"]
		}
		
		// console.log(args.filters)
	}else{
		var args = {
			txt: this.dialog.fields_dict.txt.get_value(),
			// txt:'',
			searchfield: "name",
			start: this.start
		};
	}
// 		console.log("args---0-")
// console.log(args)
		var me = this;

		if (this.target.set_custom_query) {
			this.target.set_custom_query(args);
		}
// 	console.log("args--1--")
// console.log(args)
		// load custom query from grid
		if (this.target.is_grid && this.target.fieldinfo[this.fieldname]
			&& this.target.fieldinfo[this.fieldname].get_query) {
			$.extend(args,
				this.target.fieldinfo[this.fieldname].get_query(cur_frm.doc));
		}
// 		console.log("args-2---")
// console.log(args)
		frappe.link_searchs(this.doctype, args, name_data, description_data, function (r) {
			// console.log(r)
			var parent = me.dialog.fields_dict.results.$wrapper;
			if (args.start === 0) {
				parent.empty();
			}

			if (r.values.length) {
				$.each(r.values, function (i, v) {
					var row = $(repl('<div class="row link-select-row">\
						<div class="col-xs-4">\
							<b><a href="#">%(name)s</a></b></div>\
						<div class="col-xs-8">\
							<span class="text-muted">%(values)s</span></div>\
						</div>', {
							name: v[0],
							values: v.splice(1).join(", ")
						})).appendTo(parent);

					row.find("a")
						.attr('data-value', v[0])
						.click(function () {
							var value = $(this).attr("data-value");
							var $link = this;
							if (me.target.is_grid) {
								// set in grid
								me.set_in_grid(value);
							} else {
								if (me.target.doctype)
									me.target.parse_validate_and_set_in_model(value);
								else {
									me.target.set_input(value);
									me.target.$input.trigger("change");
								}
								me.dialog.hide();
							}
							return false;
						})
				})
			} else {
				$('<p><br><span class="text-muted">' + __("No Results") + '</span>'
					+ (frappe.model.can_create(me.doctype) ?
						('<br><br><a class="new-doc btn btn-default btn-sm">'
							+ __('Create a new {0}', [__(me.doctype)]) + "</a>") : '')
					+ '</p>').appendTo(parent).find(".new-doc").click(function () {
						frappe.new_doc(me.doctype);
					});
			}

			if (r.values.length < 20) {
				var more_btn = me.dialog.fields_dict.more.$wrapper;
				more_btn.hide();
			}

		}, this.dialog.get_primary_btn());
	}

frappe.ui.form.LinkSelector.prototype.set_in_grid = function(value) {
	console.log("--setingrid--")
	var me = this, updated = false;
		var d = null;
		if (this.qty_fieldname) {
			frappe.prompt({
				fieldname: "qty", fieldtype: "Float", label: "Qty",
				"default": 1, reqd: 1
			}, function (data) {
				console.log(data)
				$.each(me.target.frm.doc[me.target.df.fieldname] || [], function (i, d) {
					if (d[me.fieldname] === value) {
						frappe.model.set_value(d.doctype, d.name, me.qty_fieldname, data.qty);
						frappe.show_alert(__("Added {0} ({1})", [value, d[me.qty_fieldname]]));
						updated = true;
						return false;
					}
				});
				if (!updated) {
					frappe.run_serially([
						() => {
							d = me.target.add_new_row();
						},
						() => frappe.timeout(0.1),
						() => frappe.model.set_value(d.doctype, d.name, me.fieldname, value),
						() => frappe.timeout(0.5),
						() => frappe.model.set_value(d.doctype, d.name, me.qty_fieldname, data.qty),
						() => frappe.show_alert(__("Added {0} ({1})", [value, data.qty]))
					]);
				}
			}, __("Set Quantity"), __("Set"));
		} else if (me.dynamic_link_field) {
			var d = me.target.add_new_row();
			frappe.model.set_value(d.doctype, d.name, me.dynamic_link_field, me.dynamic_link_reference);
			frappe.model.set_value(d.doctype, d.name, me.fieldname, value);
			frappe.show_alert(__("{0} {1} added", [me.dynamic_link_reference, value]));
		} else {
			var d = me.target.add_new_row();
			frappe.model.set_value(d.doctype, d.name, me.fieldname, value);
			frappe.show_alert(__("{0} added", [value]));
		}
}




// frappe.ui.form.LinkSelector = Class.extend({
// 	init: function (opts) {
// 		/* help: Options: doctype, get_query, target */
// 		$.extend(this, opts);

// 		var me = this;
// 		if (this.doctype != "[Select]") {
// 			frappe.model.with_doctype(this.doctype, function (r) {
// 				me.make();
// 			});
// 		} else {
// 			this.make();
// 		}
// 	},
// 	make: function () {
// 		var me = this;

// 		this.start = 0;
// 		this.dialog = new frappe.ui.Dialog({
// 			title: __("Select {0}", [(this.doctype == '[Select]') ? __("value") : __(this.doctype)]),
// 			fields: [
// 				{
// 					fieldtype: "Data", fieldname: "txt", label: __("Beginning with"),
// 					description: __("You can use wildcard %"),
// 				},
// 				{
// 					fieldtype: "HTML", fieldname: "results"
// 				},
// 				{
// 					fieldtype: "Button", fieldname: "more", label: __("More"), click: () => {
// 						me.start += 20;
// 						me.search();
// 					}
// 				}
// 			],
// 			primary_action_label: __("Search"),
// 			primary_action: function () {
// 				me.start = 0;
// 				me.search();
// 			}
// 		});

// 		if (this.txt)
// 			this.dialog.fields_dict.txt.set_input(this.txt);

// 		this.dialog.get_input("txt").on("keypress", function (e) {
// 			if (e.which === 13) {
// 				me.start = 0;
// 				me.search();
// 			}
// 		});
// 		this.dialog.show();
// 		this.search();
// 	},
// 	search: function () {
// 		var args = {
// 			txt: this.dialog.fields_dict.txt.get_value(),
// 			searchfield: "name",
// 			start: this.start
// 		};
// 		var me = this;

// 		if (this.target.set_custom_query) {
// 			this.target.set_custom_query(args);
// 		}

// 		// load custom query from grid
// 		if (this.target.is_grid && this.target.fieldinfo[this.fieldname]
// 			&& this.target.fieldinfo[this.fieldname].get_query) {
// 			$.extend(args,
// 				this.target.fieldinfo[this.fieldname].get_query(cur_frm.doc));
// 		}

// 		frappe.link_search(this.doctype, args, function (r) {
// 			var parent = me.dialog.fields_dict.results.$wrapper;
// 			if (args.start === 0) {
// 				parent.empty();
// 			}

// 			if (r.values.length) {
// 				$.each(r.values, function (i, v) {
// 					var row = $(repl('<div class="row link-select-row">\
// 						<div class="col-xs-4">\
// 							<b><a href="#">%(name)s</a></b></div>\
// 						<div class="col-xs-8">\
// 							<span class="text-muted">%(values)s</span></div>\
// 						</div>', {
// 							name: v[0],
// 							values: v.splice(1).join(", ")
// 						})).appendTo(parent);

// 					row.find("a")
// 						.attr('data-value', v[0])
// 						.click(function () {
// 							var value = $(this).attr("data-value");
// 							var $link = this;
// 							if (me.target.is_grid) {
// 								// set in grid
// 								me.set_in_grid(value);
// 							} else {
// 								if (me.target.doctype)
// 									me.target.parse_validate_and_set_in_model(value);
// 								else {
// 									me.target.set_input(value);
// 									me.target.$input.trigger("change");
// 								}
// 								me.dialog.hide();
// 							}
// 							return false;
// 						})
// 				})
// 			} else {
// 				$('<p><br><span class="text-muted">' + __("No Results") + '</span>'
// 					+ (frappe.model.can_create(me.doctype) ?
// 						('<br><br><a class="new-doc btn btn-default btn-sm">'
// 							+ __('Create a new {0}', [__(me.doctype)]) + "</a>") : '')
// 					+ '</p>').appendTo(parent).find(".new-doc").click(function () {
// 						frappe.new_doc(me.doctype);
// 					});
// 			}

// 			if (r.values.length < 20) {
// 				var more_btn = me.dialog.fields_dict.more.$wrapper;
// 				more_btn.hide();
// 			}

// 		}, this.dialog.get_primary_btn());

// 	},
// 	set_in_grid: function (value) {
// 		var me = this, updated = false;
// 		var d = null;
// 		if (this.qty_fieldname) {
// 			frappe.prompt({
// 				fieldname: "qty", fieldtype: "Float", label: "Qty",
// 				"default": 1, reqd: 1
// 			}, function (data) {
// 				$.each(me.target.frm.doc[me.target.df.fieldname] || [], function (i, d) {
// 					if (d[me.fieldname] === value) {
// 						frappe.model.set_value(d.doctype, d.name, me.qty_fieldname, data.qty);
// 						frappe.show_alert(__("Added {0} ({1})", [value, d[me.qty_fieldname]]));
// 						updated = true;
// 						return false;
// 					}
// 				});
// 				if (!updated) {
// 					frappe.run_serially([
// 						() => {
// 							d = me.target.add_new_row();
// 						},
// 						() => frappe.timeout(0.1),
// 						() => frappe.model.set_value(d.doctype, d.name, me.fieldname, value),
// 						() => frappe.timeout(0.5),
// 						() => frappe.model.set_value(d.doctype, d.name, me.qty_fieldname, data.qty),
// 						() => frappe.show_alert(__("Added {0} ({1})", [value, data.qty]))
// 					]);
// 				}
// 			}, __("Set Quantity"), __("Set"));
// 		} else if (me.dynamic_link_field) {
// 			var d = me.target.add_new_row();
// 			frappe.model.set_value(d.doctype, d.name, me.dynamic_link_field, me.dynamic_link_reference);
// 			frappe.model.set_value(d.doctype, d.name, me.fieldname, value);
// 			frappe.show_alert(__("{0} {1} added", [me.dynamic_link_reference, value]));
// 		} else {
// 			var d = me.target.add_new_row();
// 			frappe.model.set_value(d.doctype, d.name, me.fieldname, value);
// 			frappe.show_alert(__("{0} added", [value]));
// 		}
// 	}
// });

frappe.link_searchs = function (doctype, args, name_data, description_data, callback, btn) {
	
	if (!args) {
		
		// if(doctype in search_docs){
		if(jQuery.inArray(doctype, search_docs) !== -1){
			args = {
				txt: '',
				// filters:{"name": name_data,"description": description_data}
				// name: '',
				// description: ''
			}
			// args.filters={"name": name_data,"description": description_data}
		}else{
			args = {
				txt: ''
			}
		}
		
	}
	if(jQuery.inArray(doctype, search_docs) !== -1){
		if(name_data && !description_data){
			args.filters={"name": ["like","%"+name_data+"%"]}
			args.filters["name"] = ["like","%"+name_data+"%"]
		}
		if(description_data && !name_data){
			args.filters={"description": ["like","%"+description_data+"%"]}
			args.filters["description"]= ["like","%"+description_data+"%"]
		}
		if(name_data && description_data){
			args.filters={"name": ["like","%"+name_data+"%"],"description": ["like","%"+description_data+"%"]}
			args.filters["name"] = ["like","%"+name_data+"%"]
			args.filters["description"]= ["like","%"+description_data+"%"]
		}

		// args.filters=JSON.stringify({"name": name_data,"description": description_data})
	}
	args.doctype = doctype;
	if (!args.searchfield) {
		args.searchfield = 'name';
	}
	// console.log(doctype)
	// console.log(args)
	// console.log(args.filters)
	// console.log(btn)
	frappe.call({
		method: "frappe.desk.search.search_widget",
		type: "GET",
		args: args,
		callback: function (r) {
			console.log(r)
			callback && callback(r);
		},
		btn: btn
	});
}

