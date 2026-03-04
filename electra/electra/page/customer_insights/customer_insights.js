frappe.pages['customer-insights'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Customer Insights',
        single_column: true
    });

	$(`<style>
        .dt-cell__content {
            text-align: left !important;
        }</style>
    `).appendTo(page.main);	

    // Filters
    let filters = {
        customer: [],
        customer_group: '',
        date_range: 'Last Week',
		selected_date_range: [frappe.datetime.month_start(), frappe.datetime.now_date()]
    };

    this.page = page;

    // Create filter form on page
    this.form = new frappe.ui.FieldGroup({
        fields: [
            {
                fieldtype: 'MultiSelectList',
                label: 'Customers',
                fieldname: 'customer',
                options: "Customer",
                get_data: function (txt) {
                    return frappe.db.get_link_options("Customer", txt);
                },
                onchange: function() {
                    filters.customer = this.values;
                    fetch_customer_insights();
                }
            },
            {
                fieldtype: 'Column Break',
            },
            {
                fieldtype: 'Link',
                label: 'Customer Group',
                fieldname: 'customer_group',
                options: 'Customer Group',
                onchange: function() {
                    filters.customer_group = this.value;
                    fetch_customer_insights();
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
                    fetch_customer_insights();
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
                    fetch_customer_insights();
                }
			}
        ],
        body: this.page.body,
    });
    this.form.make();

    // Create a table container
    let table_container = $("<div class='customer-insights-table mt-3'></div>").appendTo(page.main);

    // Initialize DataTable
    let data_table = new frappe.DataTable(table_container[0], {
        columns: [
            { name: "Customer", width: 300, fieldtype: "Data", editable: false },
            { name: "Sales Order", width: 250, fieldtype: "Data", editable: false },
            { name: "Delivery Note", width: 250, fieldtype: "Data", editable: false },
            { name: "Sales Invoice", width: 250, fieldtype: "Data", editable: false },
            { name: "Payment Request", width: 250, fieldtype: "Data", editable: false },
            { name: "Payment Entry", width: 250, fieldtype: "Data", editable: false }
        ],
        data: [],
		cellHeight: 200,
        inlineFilters: false,
        noDataMessage: "No records found",
    });

    function fetch_customer_insights() {
		// Fetching Customer Insights Data Based On Filter Changes
        frappe.call({
            method: 'insightly.insightly.page.customer_insights.customer_insights.get_customer_insights',
            args: { filters },
			freeze: true,
			freeze_message: 'Fetching customer insights...',
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
			`Name: ${row.customer_name || ''}<br>Phone: ${row.mobile_no || ''}<br>Email ID: ${row.email_id || ''}`,

			// Update Sales Order Details
			row.sales_order
				? `Total Records: ${row.sales_order.total_records || 0}<br>
				Total Order Qty: ${row.sales_order.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.sales_order.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.sales_order.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-customer="${row.customer_code}" 
					data-doctype="Sales Order" 
					data-details='${JSON.stringify({ 
						total_records: row.sales_order.total_records, 
						total_qty: row.sales_order.total_qty 
					})}'>
					Details
				</button>`
				: ``,

			// Update Delivery Note Details
			row.delivery_note 
				? `Total Records: ${row.delivery_note.total_records || 0}<br>
				Total Delivered Qty: ${row.delivery_note.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.delivery_note.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.delivery_note.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-customer="${row.customer_code}" 
					data-doctype="Delivery Note" 
					data-details='${JSON.stringify({ 
						total_records: row.delivery_note.total_records, 
						total_qty: row.delivery_note.total_qty
					})}'>
					Details
				</button>`
				: ``,

			// Update Sales Invoice Details
			row.sales_invoice 
				? `Total Records: ${row.sales_invoice.total_records || 0}<br>
				Total Qty: ${row.sales_invoice.total_qty || 0} Qty<br>
				Total Taxable Amount: ₹${row.sales_invoice.total_taxable_amount || '0.00'}<br>
				Total Amount: ₹${row.sales_invoice.total_amount || '0.00'}<br>
				Total Paid Amount: ₹${row.sales_invoice.paid_amount || '0.00'}<br>
				Total Pending Amount: ₹${row.sales_invoice.pending_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-customer="${row.customer_code}" 
					data-doctype="Sales Invoice" 
					data-details='${JSON.stringify({ 
						total_records: row.sales_invoice.total_records, 
						total_qty: row.sales_invoice.total_qty
					})}'>
					Details
				</button>`
				: ``,

			// Update Payment Request Details
			row.payment_request 
				? `Total Records: ${row.payment_request.total_records || 0}<br>
				Total Amount: ₹${row.payment_request.total_amount || '0.00'}<br><br>
				<button class="btn btn-secondary details-btn" 
					data-customer="${row.customer_code}" 
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
					data-customer="${row.customer_code}" 
					data-doctype="Payment Entry" 
					data-details='${JSON.stringify({ 
						total_records: row.payment_entry.total_records
					})}'>
					Details
				</button>`
				: ``
		]);

		data_table.refresh(table_data);

		// Add Click Event To Details Button To Open Customer Insights Doctype Wise Details
		$(".customer-insights-table").off("click", ".details-btn").on("click", ".details-btn", function () {
			let customer_code = $(this).data("customer");
			let doctype_name = $(this).data("doctype");
			let details = $(this).data("details");
			open_customer_details(customer_code, doctype_name, details);
		});
	}	

	function open_customer_details(customer_code, doctype_name, details) {
		frappe.call({
			method: 'insightly.insightly.page.customer_insights.customer_insights.get_customer_details',
			args: {
				"customer_code": customer_code,
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

    fetch_customer_insights();
};
