frappe.pages['delivery-note-wip-accounting'].on_page_load = function (wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Delivery Note WIP - Accounting Entries'),
		single_column: true,
	});

	$(wrapper).find('.layout-main-section').css('padding', '0');

	let $content = $(wrapper).find('.layout-main-section');

	page.set_primary_action(__('Print / Save as PDF'), function () {
		window.print();
	}, 'fa fa-print');

	$.get('/assets/electra/delivery_note_wip_accounting.html', function (html) {
		let $html = $(html);

		let styles = '';
		$html.filter('style').each(function () {
			styles += '<style>' + $(this).html() + '</style>';
		});

		let bodyContent = '';
		$html.each(function () {
			if (this.tagName === 'STYLE' || this.tagName === 'HEAD' || this.tagName === 'HTML') return;
			bodyContent += $(this).prop('outerHTML') || '';
		});

		if (!bodyContent) {
			bodyContent = $html.find('body').html() || $html.html();
		}

		$content.html(styles + '<div class="dnwip-manual-wrapper">' + bodyContent + '</div>');

		$content.find('body').css({ margin: 0, padding: 0, background: 'transparent' });
		$content.find('.container, .page').css({ 'max-width': '100%', 'box-shadow': 'none', 'padding': '20px' });
		$content.find('.cover').css({ 'border-radius': '0' });
	}).fail(function () {
		$content.html('<div class="alert alert-danger" style="margin:20px;">Could not load the manual. Please ensure the file exists at <code>/assets/electra/delivery_note_wip_accounting.html</code>. Run <code>bench build</code> if needed.</div>');
	});
};
