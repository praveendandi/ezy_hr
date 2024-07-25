frappe.ui.form.on('Employee', {
    // Trigger when the form is loaded or refreshed
    refresh: function(frm) {
        // Check the status and perform actions based on the status
        if (frm.doc.status === 'Left') {
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'User',
                    name: frm.doc.user_id, // Assuming user_id is the link to the User doctype
                    fieldname: 'enabled',
                    value: 0
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint(__('The employee user ID has been disabled.'));
                    }
                }
            });
        }
    }
});
