frappe.pages['cost-estimation-manual'].on_page_load = function (wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Cost Estimation - User Manual & Calculation Reference'),
		single_column: true,
	});

	$(wrapper).find('.layout-main-section').css('padding', '0');

	let $content = $(wrapper).find('.layout-main-section');

	// Add a print button to the page header
	page.set_primary_action(__('Print / Save as PDF'), function () {
		window.print();
	}, 'fa fa-print');

	// Load the HTML content from the public folder
	$.get('/assets/electra/cost_estimation_user_manual.html', function (html) {
		// Extract the body content and styles from the standalone HTML
		let $html = $(html);

		// Extract styles
		let styles = '';
		$html.filter('style').each(function () {
			styles += '<style>' + $(this).html() + '</style>';
		});

		// Extract body content
		let bodyContent = '';
		$html.each(function () {
			if (this.tagName === 'STYLE' || this.tagName === 'HEAD' || this.tagName === 'HTML') return;
			bodyContent += $(this).prop('outerHTML') || '';
		});

		// Also grab elements inside body if the top-level is the full document
		if (!bodyContent) {
			bodyContent = $html.find('body').html() || $html.html();
		}

		// Inject into the page
		$content.html(styles + '<div class="ce-manual-wrapper">' + bodyContent + '</div>');

		// Adjust styles for embedding inside Frappe
		$content.find('body').css({ margin: 0, padding: 0, background: 'transparent' });
		$content.find('.container, .page').css({ 'max-width': '100%', 'box-shadow': 'none', 'padding': '20px' });
		$content.find('.cover').css({ 'border-radius': '0' });

		// Remove href from TOC links to prevent Frappe router interference
		$content.find('.toc a').each(function () {
			$(this).removeAttr('href').css('cursor', 'default');
		});
	}).fail(function () {
		$content.html('<div class="alert alert-danger" style="margin:20px;">Could not load the manual. Please ensure the file exists at <code>/assets/electra/cost_estimation_user_manual.html</code>. Run <code>bench build</code> if needed.</div>');
	});
};
