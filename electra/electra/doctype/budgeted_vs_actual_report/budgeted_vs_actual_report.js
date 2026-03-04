// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budgeted vs Actual Report", {
	refresh(frm) {
        frm.set_df_property('print', "hidden", 1);
        if (!frm.is_new()) {
            frm.add_custom_button(__('Calculate'), function () {
                frappe.call({
                    method: 'electra.electra.doctype.budgeted_vs_actual_report.budgeted_vs_actual_report.enqueue_create_project',
                    args: {
                        name: frm.doc.project // Pass the project name
                    },
                    freeze: true,
				    freeze_message: __("Calculating ..."),
                    callback: function (r) {
                        if (r.message) {
                            console.log(r.message)
                            frm.set_df_property('print', "hidden", 0);
                        }
                    },
                    
                });
            });
        }

        if (!frm.setup_progress_subscription) {
            frm.setup_progress_subscription = true;

            frappe.realtime.on('project_update_progress', function (data) {
                console.log('Progress Update:', data);

                frm.dashboard.show_progress('Update Progress', data.progress, __(data.description));

                if (data.progress === 100) {
                    frappe.msgprint(__('Project calculation is complete!'));
                }
            });
        }
    },
});
