frappe.pages['supplier-insights'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Supplier Insights',
        single_column: true
    });

	$(`<style>
        .dt-cell__content {
            text-align: left !important;
        }</style>
    `).appendTo(page.main);	

    // Filters
    let filters = {
        supplier: [],
        supplier_group: '',
        date_range: 'Last Week',
		selected_date_range: [frappe.datetime.month_start(), frappe.datetime.now_date()]
    };

    this.page = page;

    // Create filter form on page
    this.form = new frappe.ui.FieldGroup({
        fields: [
            {
                fieldtype: 'MultiSelectList',
                label: 'Supplier',
                fieldname: 'supplier',
                options: "Supplier",
                get_data: function (txt) {
                    return frappe.db.get_link_options("Supplier", txt);
                },
                onchange: function() {
                    filters.supplier = this.values;
                    fetch_supplier_insights();
                }
            },
            {
                fieldtype: 'Column Break',
            },
            {
                fieldtype: 'Link',
                label: 'Supplier Group',
                fieldname: 'supplier_group',
                options: 'Supplier Group',
                onchange: function() {
                    filters.supplier_group = this.value;
                    fetch_supplier_insights();
                }
            },
            {
                fieldtype: 'Column Break',
            },
            {
                fieldtype: 'Select',
                label: 'Date Range',
                fieldname: 'date_range',
				default: 'Last Week',
                options: ['Last Week', 'Last Month', 'Last 3 Months', 'Last Year', 'Select Date Range'],
                onchange: function() {
                    filters.date_range = this.value;
                    fetch_supplier_insights();
                }
            },
			{
                fieldtype: 'Column Break',
            },
			{
				label: 'Select Date Range',
				fieldtype: 'Date Range',
				fieldname: 'selected_date_range',
				depends_on: "eval:doc.date_range == 'Select Date Range'",
				default: [frappe.datetime.month_start(), frappe.datetime.now_date()],
				onchange: function() {
                    filters.selected_date_range = this.value;
                    fetch_supplier_insights();
                }
			}
        ],
        body: this.page.body,
    });
    this.form.make();

    // Create a table container
    let table_container = $("<div class='supplier-insights-table mt-3'></div>").appendTo(page.main);

    // Initialize DataTable
    let data_table = new frappe.DataTable(table_container[0], {
        columns: [
            { name: "Supplier", width: 300, fieldtype: "Data", editable: false },
            { name: "Purchase Order", width: 250, fieldtype: "Data", editable: false },
            { name: "Purchase Receipt", width: 250, fieldtype: "Data", editable: false },
            { name: "Purchase Invoice", width: 250, fieldtype: "Data", editable: false },
            { name: "Payment Request", width: 250, fieldtype: "Data", editable: false },
            { name: "Payment Entry", width: 250, fieldtype: "Data", editable: false }
        ],
        data: [],
		cellHeight: 200,
        inlineFilters: false,
        noDataMessage: "No records found",
    });

    function fetch_supplier_insights() {
		// Fetching Supplier Insights Data Based On Filter Changes
        frappe.call({
            method: 'insightly.insightly.page.supplier_insights.supplier_insights.get_supplier_insights',
            args: { filters },
			freeze: true,
			freeze_message: 'Fetching supplier insights...',
            callback: function(r) {
                if (r.message) {
                    update_table(r.message);
					frappe.dom.unfreeze();
                }
            }
        });
    }

    function update_table(data) {
		// Update Fetched Data To DataTable
		let table_data = data.map(row => [
			`Name: ${row.supplier_name || ''}<br>Phone: ${row.mobile_no || ''}<br>Email ID: ${row.email_id || ''}`,

			// Update Purchase Order Details
			row.purchase_order
				? `Total Records: ${row.purchase_order.total_records || 0}<br>
				Total Order Qty: ${row.purchase_order.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.purchase_order.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.purchase_order.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-supplier="${row.supplier_code}" 
					data-doctype="Purchase Order" 
					data-details='${JSON.stringify({ 
						total_records: row.purchase_order.total_records, 
						total_qty: row.purchase_order.total_qty 
					})}'>
					Details
				</button>`
				: ``,

			// Update Purchase Receipt Details
			row.purchase_receipt 
				? `Total Records: ${row.purchase_receipt.total_records || 0}<br>
				Total Received Qty: ${row.purchase_receipt.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.purchase_receipt.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.purchase_receipt.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-supplier="${row.supplier_code}" 
					data-doctype="Purchase Receipt" 
					data-details='${JSON.stringify({ 
						total_records: row.purchase_receipt.total_records, 
						total_qty: row.purchase_receipt.total_qty
					})}'>
					Details
				</button>`
				: ``,

			// Update Purchase Invoice Details
			row.purchase_invoice 
				? `Total Records: ${row.purchase_invoice.total_records || 0}<br>
				Total Qty: ${row.purchase_invoice.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.purchase_invoice.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.purchase_invoice.total_amount || '0.00'}<br>
				Total Paid Amount: ₹${row.purchase_invoice.paid_amount || '0.00'}<br>
				Total Pending Amount: ₹${row.purchase_invoice.pending_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-supplier="${row.supplier_code}" 
					data-doctype="Purchase Invoice" 
					data-details='${JSON.stringify({ 
						total_records: row.purchase_invoice.total_records, 
						total_qty: row.purchase_invoice.total_qty
					})}'>
					Details
				</button>`
				: ``,

			// Update Payment Request Details
			row.payment_request 
				? `Total Records: ${row.payment_request.total_records || 0}<br>
				Total Amount: ₹${row.payment_request.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-supplier="${row.supplier_code}" 
					data-doctype="Payment Request" 
					data-details='${JSON.stringify({ 
						total_records: row.payment_request.total_records
					})}'>
					Details
				</button>`
				: ``,

			// Update Payment Entry Details
			row.payment_entry 
				? `Total Records: ${row.payment_entry.total_records || 0}<br>
				Total Amount: ₹${row.payment_entry.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-supplier="${row.supplier_code}" 
					data-doctype="Payment Entry" 
					data-details='${JSON.stringify({ 
						total_records: row.payment_entry.total_records
					})}'>
					Details
				</button>`
				: ``
		]);

		data_table.refresh(table_data);

		// Add Click Event To Details Button To Open Supplier Insights Doctype Wise Details
		$(".supplier-insights-table").off("click", ".details-btn").on("click", ".details-btn", function () {
			let supplier_code = $(this).data("supplier");
			let doctype_name = $(this).data("doctype");
			let details = $(this).data("details");
			open_supplier_details(supplier_code, doctype_name, details);
		});
	}	

	function open_supplier_details(supplier_code, doctype_name, details) {
		frappe.call({
			method: 'insightly.insightly.page.supplier_insights.supplier_insights.get_supplier_details',
			args: {
				"supplier_code": supplier_code,
				"doctype": doctype_name,
				"details": details,
				"filters": filters
			 },
			callback: function (r) {
				if (r.message) {
					let details = r.message;

					// Open Dialog Box
					let d = new frappe.ui.Dialog({
						title: `${doctype_name} Details`,
						size: "large",
						fields: [{ fieldtype: "HTML", options: details }],
						primary_action_label: "Close",
						primary_action() { d.hide(); }
					});

					d.show();
					d.$wrapper.find('.modal-dialog').css("max-width", "1000px");
				}
			}
		});
	}

    fetch_supplier_insights();
};
