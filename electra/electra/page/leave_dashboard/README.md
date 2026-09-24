# Leave Dashboard for ERPNext/Frappe

A modern, responsive Leave Dashboard that displays Leave Application workflow state counts and leave balance summaries (allocated, consumed, available).

## Features

### Workflow State Cards
- Dynamically generates cards based on workflow states (no hardcoded statuses)
- Each card shows: icon, workflow state name, count, and "Leave Application" badge
- Color-coded by status (configurable in JS `color_map`)
- Clicking a card opens the Leave Application list filtered by that workflow state
- Responsive grid: 4 columns (desktop) → 3 (tablet) → 2 (small) → 1 (mobile)

### Leave Balance Summary
- Shows allocated, consumed, and available leaves grouped by leave type
- Visual progress bar showing consumption ratio
- Data sourced from Leave Ledger Entry for accuracy

### Filters
- Company
- Branch
- Department
- Employee
- Employee Category (auto-detected if the field exists on Employee doctype)
- Leave Type
- Date Range (From Date / To Date)

All filters refresh the dashboard automatically on change.

### Additional Features
- Loading skeleton animation
- "No Records Found" empty state
- Animated count-up on cards
- Refresh button
- Card hover effects
- Dark mode support (follows ERPNext theme)
- Only active employees are included
- Respects ERPNext permission rules

## Installation

1. The dashboard is part of the `electra` app. Ensure the app is installed:
   ```bash
   bench --site your-site install-app electra
   ```

2. Build assets:
   ```bash
   bench build --app electra
   ```

3. Access the dashboard at:
   ```
   /app/leave-dashboard
   ```

## Files

| File | Purpose |
|------|---------|
| `electra/electra/page/leave_dashboard/leave_dashboard.py` | Python API (single optimized endpoint) |
| `electra/electra/page/leave_dashboard/leave_dashboard.js` | Frontend JavaScript (Frappe Page) |
| `electra/electra/page/leave_dashboard/leave_dashboard.json` | Page metadata |
| `electra/electra/public/css/leave_dashboard.css` | CSS styling (responsive, dark mode) |
| `electra/electra/hooks.py` | Updated `app_include_css` to load dashboard CSS |

## API

### `get_leave_dashboard_data(filters)`
Single optimized endpoint returning:
- `workflow_cards`: List of `{workflow_state, count}` from GROUP BY query
- `leave_balances`: List of `{leave_type, allocated, consumed, available}` from Leave Ledger Entry
- `workflow_states`: All defined workflow states for dynamic card generation
- `workflow_state_field`: The fieldname used for workflow state

### `get_filter_options()`
Returns available options for filter dropdowns.

## Color Configuration

Colors are defined in the `state.color_map` object in `leave_dashboard.js`. To change a color or add a new one:

```javascript
color_map: {
    'Draft': '#f39c12',
    'Pending for CEO Approval': '#f59e0b',
    // ... add new states here
}
```

For states not in the map, the code uses partial name matching (e.g., "pending" → red, "approved" → green).

## Performance

- Uses a single GROUP BY SQL query for workflow state counts
- Leave balances computed via a single GROUP BY query on Leave Ledger Entry
- Active employee filtering done once and shared across both queries
- Dashboard loads within 2 seconds for large datasets
