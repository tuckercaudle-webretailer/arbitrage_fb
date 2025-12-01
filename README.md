# Arbitrage Bot - Facebook Marketplace Stub Version

This prototype expands the earlier arbitrage Flask app with **simulated** Facebook Marketplace integration.
It is intentionally sandboxed: no real purchases or postings happen. Use this to test workflow locally.

## What's included
- `app.py` : Flask app with routes for simulated fetches, approvals, and FB listing stubs.
- `templates/` : simple HTML interfaces.
- `data.db` : created at first run (SQLite).

## How to run
1. Python 3.11+
2. `pip install flask`
3. `python app.py`
4. Open http://127.0.0.1:5000/

## Facebook Marketplace production integration (IMPORTANT)
* Meta provides partner APIs for Marketplace (Marketplace Partner Item API, Content Library API, Marketplace Approval API, etc.)
* **Access usually requires an approved Meta partner account and specific permissions.** You will need to:
  1. Create a Meta developer app in https://developers.facebook.com
  2. Request/obtain the required permissions (Marketplace partner access, Graph API scopes)
  3. Use OAuth access tokens and call the Graph API endpoints to fetch/create listings.
* Official docs and starting points:
  - Marketplace Partner Item API / Seller API: https://developers.facebook.com/docs/marketplace/partnerships/itemAPI/
  - Content Library & Marketplace preview APIs: https://developers.facebook.com/docs/content-library-and-api/content-library-api/guides/fb-marketplace/
  - Marketplace Approval API: https://developers.facebook.com/docs/commerce-platform/platforms/distribution/MPApprovalAPI/
  - Graph API: https://developers.facebook.com/docs/graph-api/

Please read Meta's developer policies before integrating: https://developers.facebook.com/devpolicy/

## Security & Legal
- Do not automate real purchases without human review.
- Follow marketplace terms; avoid scraping/automation that violates policies.
- Use sandbox/test modes and never store raw payment card data.

## Next steps I can do for you right now (pick one)
- Replace the FB stubs with real Graph API calls (I will need you to provide developer app IDs & OAuth tokens, or follow the README to create them).
- Add OAuth flow and example Graph API calls (sandbox) to `app.py` so you can test fetch and listing creation once tokens are available.
- Make a full zip with real integration instructions & sample environment variables.

