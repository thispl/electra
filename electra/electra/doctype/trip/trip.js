

frappe.ui.form.on('Trip', {
    refresh: function (frm) {
        if (frm.doc.docstatus < 1) {
            let button_label = 'Start Timer';

            $.each(frm.doc.destination || [], function (i, row) {
                if (row.from_time && (frappe.datetime.get_datetime_as_string() >= row.from_time)) {
                    button_label = 'Resume Timer';
                }
            });

            frm.add_custom_button(__(button_label), function () {
                let dialog = new frappe.ui.Dialog({
                    title: __("Timer"),
                    fields: [
                        { "fieldtype": "Select", "label": __("Point Type"), "fieldname": "point_type", "options": ["Pickup", "Halt", "Drop"] },
                        { "fieldtype": "Float", "label": __("Expected Hrs"), "fieldname": "expected_hours" },
                        { "fieldtype": "Section Break" },
                        { "fieldtype": "HTML", "fieldname": "timer_html" }
                    ]
                });

                dialog.get_field("timer_html").$wrapper.append(get_timer_html());

                let $btn_start = dialog.$wrapper.find(".playpause .btn-start");
                let $btn_complete = dialog.$wrapper.find(".playpause .btn-complete");

                $btn_start.click(function (e) {
                    let args = dialog.get_values();
                    if (!args) return;

                    let row = findChildRow(frm.doc.destination, args.point_type);

                    if (row) {
                        row.from_time = frappe.datetime.get_datetime_as_string();
                        frm.set_value('destination', frm.doc.destination);  // Set value in the field
                        frm.refresh_field("destination");
                        $btn_start.hide();
                        $btn_complete.show();
                    } else {
                        frappe.msgprint('No existing row found for the selected Point Type.');
                    }
                });

                $btn_complete.click(function () {
                    let args = dialog.get_values();
                    if (!args) return;

                    let row = findChildRow(frm.doc.destination, args.point_type);

                    if (row && !row.to_time) {
                        row.to_time = frappe.datetime.get_datetime_as_string();
                        frm.set_value('destination', frm.doc.destination);  // Set value in the field
                        frm.refresh_field("destination");
                        dialog.hide();
                        // frm.page.btn_primary.html('Start Timer');
                    } else {
                        frappe.msgprint('No existing row found for the selected Point Type or To Time already set.');
                    }
                });

                dialog.show();
            }).addClass("btn-primary");
        }
    }
});

function get_timer_html() {
    return `
        <div class="stopwatch">
            <span class="hours">00</span>
            <span class="colon">:</span>
            <span class="minutes">00</span>
            <span class="colon">:</span>
            <span class="seconds">00</span>
        </div>
        <div class="playpause text-center">
            <button class="btn btn-primary btn-start">${__("Start")}</button>
            <button class="btn btn-primary btn-complete">${__("Complete")}</button>
        </div>
    `;
}

function findChildRow(destination, point_type) {
    for (let i = 0; i < destination.length; i++) {
        let row = destination[i];
        if (row.point === point_type) {
            return row;
        }
    }
    return null;
}
