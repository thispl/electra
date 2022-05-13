// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sponsor Company', {
	refresh: function(frm) {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(showPosition);
		  } else { 
			x.innerHTML = "Geolocation is not supported by this browser.";
		  }
		
		
		function showPosition(position) {
			position.coords.latitude
			frm.set_value("latitude",position.coords.latitude)
			frm.set_value("longitude",position.coords.longitude)
		}
	}
});
