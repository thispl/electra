frappe.pages['leave-dashboard'].on_page_load = function (wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Leave Dashboard'),
		single_column: true,
	});

	// State
	let state = {
		filters: {},
		wrapper: wrapper,
		page: page,
		workflow_state_field: 'workflow_state',
		color_map: {
			'Draft': '#f39c12',
			'Pending': '#e74c3c',
			'HR': '#3498db',
			'HR Coordinator': '#3498db',
			'HR Department': '#3498db',
			'General Manager': '#2ecc71',
			'Pending for General Manager': '#2ecc71',
			'CEO': '#f59e0b',
			'Pending for CEO Approval': '#f59e0b',
			'CM': '#c0392b',
			'Pending for CM Approval': '#c0392b',
			'Contract Manager': '#c0392b',
			'Pending for Contract Manager': '#c0392b',
			'Approved': '#27ae60',
			'Rejected': '#e74c3c',
			'Cancelled': '#95a5a6',
		},
	};

	// Build the page layout
	build_page_layout(page, wrapper, state);

	// Create filter bar (async, then fetch data)
	create_filter_bar(page, state);
};

function build_page_layout(page, wrapper, state) {
	const $main = $(page.main);
	$main.html(`
		<div class="leave-dashboard-container">
			<div class="ld-refresh-bar">
				<button class="btn btn-default btn-sm ld-refresh-btn" id="ld-refresh">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<polyline points="23 4 23 10 17 10"></polyline>
						<polyline points="1 20 1 14 7 14"></polyline>
						<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
					</svg>
					${__('Refresh')}
				</button>
			</div>

			<!-- Leave Balance Summary Section -->
			<div class="ld-section-header">
				<h3>${__('Leave Balance Summary')}</h3>
			</div>
			<div class="ld-balance-grid" id="ld-balance-grid">
				<div class="ld-skeleton-card"></div>
				<div class="ld-skeleton-card"></div>
				<div class="ld-skeleton-card"></div>
			</div>

			<!-- Workflow State Cards Section -->
			<div class="ld-section-header">
				<h3>${__('Leave Applications')}</h3>
			</div>
			<div class="ld-card-grid" id="ld-card-grid">
				<div class="ld-skeleton-card"></div>
				<div class="ld-skeleton-card"></div>
				<div class="ld-skeleton-card"></div>
				<div class="ld-skeleton-card"></div>
			</div>
			<div class="ld-no-records" id="ld-no-records" style="display:none;">
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
					<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
					<line x1="16" y1="2" x2="8" y2="10"></line>
					<line x1="8" y1="2" x2="16" y2="10"></line>
				</svg>
				<p>${__('No Records Found')}</p>
			</div>
		</div>
	`);

	// Refresh button
	$main.find('#ld-refresh').on('click', () => {
		fetch_data(state);
	});
}

function create_filter_bar(page, state) {
	const filter_fields = [
		{
			fieldtype: 'Link',
			label: __('Company'),
			fieldname: 'company',
			options: 'Company',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Link',
			label: __('Branch'),
			fieldname: 'branch',
			options: 'Branch',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Column Break',
		},
		{
			fieldtype: 'Link',
			label: __('Department'),
			fieldname: 'department',
			options: 'Department',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Link',
			label: __('Employee'),
			fieldname: 'employee',
			options: 'Employee',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Column Break',
		},
		{
			fieldtype: 'Link',
			label: __('Leave Type'),
			fieldname: 'leave_type',
			options: 'Leave Type',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Date',
			label: __('From Date'),
			fieldname: 'from_date',
			onchange: () => on_filter_change(state),
		},
		{
			fieldtype: 'Column Break',
		},
		{
			fieldtype: 'Date',
			label: __('To Date'),
			fieldname: 'to_date',
			onchange: () => on_filter_change(state),
		},
	];

	state.filter_group = new frappe.ui.FieldGroup({
		fields: filter_fields,
		body: page.body,
	});
	state.filter_group.make();

	// Insert filter bar before the dashboard container
	const $filter_wrapper = $('<div class="ld-filter-bar"></div>');
	$filter_wrapper.append(state.filter_group.wrapper);

	const $container = $(page.main).find('.leave-dashboard-container');
	$container.prepend($filter_wrapper);

	// Now fetch data
	fetch_data(state);
}

function on_filter_change(state) {
	// Collect filter values
	const values = state.filter_group.get_values();
	state.filters = {};

	for (const key in values) {
		if (values[key]) {
			state.filters[key] = values[key];
		}
	}

	fetch_data(state);
}

function fetch_data(state) {
	show_skeleton();

	frappe.call({
		method: 'electra.electra.page.leave_dashboard.leave_dashboard.get_leave_dashboard_data',
		args: {
			filters: JSON.stringify(state.filters || {}),
		},
		callback: (r) => {
			if (r.exc) {
				console.error('Leave Dashboard error:', r.exc);
				return;
			}
			const data = r.message;
			state.workflow_state_field = data.workflow_state_field || 'workflow_state';

			render_balance_cards(data.leave_balances || [], state);
			render_workflow_cards(data.workflow_cards || [], state);
		},
		error: (err) => {
			console.error('Fetch error:', err);
		},
	});
}

function show_skeleton() {
	const $cardGrid = $('#ld-card-grid');
	const $balanceGrid = $('#ld-balance-grid');
	if ($cardGrid.length) {
		$cardGrid.html(Array(4).fill('<div class="ld-skeleton-card"></div>').join(''));
	}
	if ($balanceGrid.length) {
		$balanceGrid.html(Array(3).fill('<div class="ld-skeleton-card"></div>').join(''));
	}
	$('#ld-no-records').hide();
}

function render_balance_cards(balances, state) {
	const $grid = $('#ld-balance-grid');

	if (!balances.length) {
		$grid.html(`<div class="ld-no-balances">${__('No leave balance data available')}</div>`);
		return;
	}

	$grid.html(balances.map(b => `
		<div class="ld-balance-card">
			<div class="ld-balance-header">
				<span class="ld-balance-icon">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
						<line x1="16" y1="2" x2="8" y2="10"></line>
						<line x1="8" y1="2" x2="16" y2="10"></line>
					</svg>
				</span>
				<span class="ld-balance-title">${escape_html(b.leave_type)}</span>
			</div>
			<div class="ld-balance-stats">
				<div class="ld-stat">
					<span class="ld-stat-label">${__('Allocated')}</span>
					<span class="ld-stat-value ld-stat-allocated">${b.allocated}</span>
				</div>
				<div class="ld-stat">
					<span class="ld-stat-label">${__('Consumed')}</span>
					<span class="ld-stat-value ld-stat-consumed">${b.consumed}</span>
				</div>
				<div class="ld-stat">
					<span class="ld-stat-label">${__('Available')}</span>
					<span class="ld-stat-value ld-stat-available">${b.available}</span>
				</div>
			</div>
			<div class="ld-balance-bar">
				<div class="ld-balance-bar-fill" style="width: ${b.allocated > 0 ? (b.consumed / b.allocated * 100) : 0}%"></div>
			</div>
		</div>
	`).join(''));

	// Click handler for balance cards - route to Employee Leave Balance Summary
	$grid.find('.ld-balance-card').on('click', function () {
		const leave_type = $(this).attr('data-leave-type');
		open_leave_balance_report(leave_type, state);
	});
}

function render_workflow_cards(cards, state) {
	const $grid = $('#ld-card-grid');
	const $noRecords = $('#ld-no-records');

	// Filter out Cancelled and Rejected states
	const filtered_cards = cards.filter(card => {
		const state_lower = (card.workflow_state || '').toLowerCase();
		return !state_lower.includes('cancelled') && !state_lower.includes('rejected');
	});

	if (!filtered_cards.length) {
		$grid.empty();
		$noRecords.show();
		return;
	}

	$noRecords.hide();

	$grid.html(filtered_cards.map(card => {
		const color = get_color_for_state(card.workflow_state, state);
		const count = card.count || 0;

		return `
			<div class="ld-card" style="--card-color: ${color};" data-workflow-state="${escape_attr(card.workflow_state)}">
				<div class="ld-card-top">
					<div class="ld-card-icon" style="background: ${color}20; color: ${color};">
						<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
							<line x1="16" y1="2" x2="8" y2="10"></line>
							<line x1="8" y1="2" x2="16" y2="10"></line>
						</svg>
					</div>
					<div class="ld-card-title">${escape_html(card.workflow_state)}</div>
					<div class="ld-card-arrow">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<polyline points="9 18 15 12 9 6"></polyline>
						</svg>
					</div>
				</div>
				<div class="ld-card-count" data-target="${count}">0</div>
				<div class="ld-card-badge">
					<span class="ld-badge">Leave Application</span>
				</div>
			</div>
		`;
	}).join(''));

	// Animate counts
	$grid.find('.ld-card-count').each(function () {
		animate_count(this, parseInt($(this).attr('data-target'), 10));
	});

	// Click handler for workflow cards
	$grid.find('.ld-card').on('click', function () {
		const ws = $(this).attr('data-workflow-state');
		open_leave_application_list(ws, state);
	});
}

function get_color_for_state(state_name, state) {
	// Direct match
	if (state.color_map[state_name]) {
		return state.color_map[state_name];
	}
	// Partial match
	const lower = state_name.toLowerCase();
	if (lower.includes('draft')) return state.color_map['Draft'];
	if (lower.includes('ceo')) return state.color_map['CEO'];
	if (lower.includes('cm') || lower.includes('contract manager')) return state.color_map['CM'];
	if (lower.includes('hr')) return state.color_map['HR'];
	if (lower.includes('general manager')) return state.color_map['General Manager'];
	if (lower.includes('pending')) return state.color_map['Pending'];
	if (lower.includes('approved')) return state.color_map['Approved'];
	if (lower.includes('rejected')) return state.color_map['Rejected'];
	if (lower.includes('cancelled')) return state.color_map['Cancelled'];
	if (lower.includes('site manager') || lower.includes('project manager')) return '#8e44ad';
	// Default: generate a color from the string
	return '#7f8c8d';
}

function open_leave_application_list(workflow_state, state) {
	const ws_field = state.workflow_state_field || 'workflow_state';
	const filters = {};
	filters[ws_field] = workflow_state;

	// Also apply dashboard filters to the list view
	if (state.filters) {
		if (state.filters.company) filters['company'] = state.filters.company;
		if (state.filters.department) filters['department'] = state.filters.department;
		if (state.filters.leave_type) filters['leave_type'] = state.filters.leave_type;
		if (state.filters.employee) filters['employee'] = state.filters.employee;
		if (state.filters.from_date) filters['from_date'] = ['>=', state.filters.from_date];
		if (state.filters.to_date) filters['to_date'] = ['<=', state.filters.to_date];
	}

	frappe.set_route('List', 'Leave Application', filters);
}

function animate_count(el, target) {
	const duration = 800;
	const start = performance.now();
	const start_val = 0;

	function tick(now) {
		const elapsed = now - start;
		const progress = Math.min(elapsed / duration, 1);
		const eased = 1 - Math.pow(1 - progress, 3);
		const current = Math.round(start_val + (target - start_val) * eased);
		el.textContent = current;
		if (progress < 1) {
			requestAnimationFrame(tick);
		} else {
			el.textContent = target;
		}
	}

	requestAnimationFrame(tick);
}

function escape_html(str) {
	const div = document.createElement('div');
	div.textContent = str || '';
	return div.innerHTML;
}

function escape_attr(str) {
	return (str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
