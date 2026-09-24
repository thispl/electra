# Norden API Cloudflare Whitelist — Issue & Resolution

## Issue

The Product Search doctype in Electra calls the Norden ERP API to fetch item cost and availability. These calls are failing with:

```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Root Cause

The Norden ERP server (`erp.nordencommunication.com`) is behind **Cloudflare bot protection**. All server-side API requests from the Electra server are being blocked with a **403 Forbidden** response containing a Cloudflare JavaScript challenge page (HTML) instead of JSON data. When `json.loads()` tries to parse this HTML, it throws the `JSONDecodeError`.

### Affected Functions

- `electra.utils.get_norden_item()` — `@/electra/electra/utils.py:1401`
- `electra.utils.get_norden_item_without_cost()` — `@/electra/electra/utils.py:1421`

### API Endpoints Blocked

- `https://erp.nordencommunication.com/api/method/norden.custom.get_electra_details`
- `https://erp.nordencommunication.com/api/method/norden.custom.get_electra_details_without_cost`

## Electra Server Details

| Detail | Value |
|--------|-------|
| Server IP | `13.234.40.9` |
| API Token | `token 2f66b0971d5ff52:f6937d9b5d01850` |
| Cloudflare Ray ID (sample) | `a231ee1bdf299905` |

## Response Headers (Proof of Cloudflare Block)

```
HTTP/2 403
cf-mitigated: challenge
server: cloudflare
content-type: text/html; charset=UTF-8
```

The `cf-mitigated: challenge` header confirms Cloudflare is actively blocking the request.

## Code Fix Applied (Prevents Crash)

Error handling has been added to both `get_norden_item` and `get_norden_item_without_cost` in `electra/utils.py`:

- Added `timeout=30` to prevent indefinite hangs
- Added status code + response text check before `json.loads()`
- Added try/except to catch all exceptions, log via `frappe.log_error`, and return `[]`
- Product Search form will no longer crash — only Norden sections will be empty

## Steps for Norden Team to Whitelist Electra Server

### Option 1 — IP Access Rule (Recommended, Simplest)

1. Log in to **Cloudflare Dashboard** → select domain `nordencommunication.com`
2. Go to **Security** → **WAF** → **Tools**
3. Under **IP Access Rules**, enter: `13.234.40.9`
4. Select action: **Allow**
5. Click **Add**

### Option 2 — WAF Custom Rule with Super Bot Fight Mode Skip

1. Go to **Security** → **WAF** → **Custom rules**
2. Click **Create rule**
3. Set:
   - **Rule name:** `ERP Allow`
   - **Field:** `IP Source Address`
   - **Operator:** `equals`
   - **Value:** `13.234.40.9`
   - **Action:** `Skip`
   - Check **All Super Bot Fight Mode Rules** and all other security features
4. Set rule order to **First**
5. Click **Deploy**

> **Important:** The rule must be **Deployed**, not just saved. Verify it shows a green "Deployed" badge.

### Option 3 — Disable Super Bot Fight Mode Directly

If WAF custom rules don't work (Super Bot Fight Mode may run independently):

1. Go to **Security** → **Bots** → **Super Bot Fight Mode**
2. Turn **OFF** Super Bot Fight Mode entirely, OR
3. Set all bot categories to **Allow**

### Option 4 — Bypass Rule for API Paths

1. Go to **Security** → **WAF** → **Custom rules**
2. Click **Create rule**
3. Set:
   - **Rule name:** `Bypass Norden API`
   - **Field:** `URI Path`
   - **Operator:** `starts with`
   - **Value:** `/api/method/norden.custom.`
   - **Action:** `Skip` → check all security features
4. Click **Deploy**

## Verification

After the Norden team applies any of the above, verify by running:

```bash
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "Content-Type: application/json" \
  -H "Authorization: token 2f66b0971d5ff52:f6937d9b5d01850" \
  "https://erp.nordencommunication.com/api/method/norden.custom.get_electra_details?item=test"
```

- **Success:** Response will be JSON with HTTP 200
- **Still blocked:** Response will be HTML with `Just a moment...` title and HTTP 403

## Troubleshooting

If the rule is configured but still not working:

1. **Check if rule is deployed** — In Cloudflare, saved ≠ deployed. Look for a "Deploy" button or green "Deployed" badge.
2. **Check Security Events** — Go to Security → Events, search for the Ray ID from the blocked request to see which rule (if any) is being evaluated.
3. **Super Bot Fight Mode override** — On some Cloudflare plans, Super Bot Fight Mode cannot be overridden by WAF custom rules. Try disabling it directly (Option 3).
4. **IP mismatch** — Verify the Electra server's outgoing IP hasn't changed: `curl -s ifconfig.me`
5. **Cloudflare propagation** — Rules may take a few minutes to propagate. Wait and retry.
