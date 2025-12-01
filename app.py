from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3, os, uuid
from decimal import Decimal, ROUND_HALF_UP

DB = "data.db"
APP_SECRET = "change-me-in-prod"

app = Flask(__name__)
app.secret_key = APP_SECRET

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE items (
                id TEXT PRIMARY KEY,
                source TEXT,
                title TEXT,
                buy_price REAL,
                shipping REAL,
                fees REAL,
                sku TEXT,
                inspected INTEGER DEFAULT 0,
                approved INTEGER DEFAULT 0,
                status TEXT DEFAULT 'candidate'
            )
        ''')
        c.execute('''
            CREATE TABLE listings (
                id TEXT PRIMARY KEY,
                item_id TEXT,
                platform TEXT,
                list_price REAL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

def db_conn():
    return sqlite3.connect(DB)

def fetch_marketplace_samples():
    samples = [
        {"id": "src1-"+str(uuid.uuid4())[:8], "source":"ExampleMarket", "title":"Used Wireless Headphones - Good", "buy_price":25.0, "shipping":5.0, "fees":2.5},
        {"id": "src1-"+str(uuid.uuid4())[:8], "source":"ExampleMarket", "title":"Vintage Board Game - Complete", "buy_price":18.0, "shipping":8.0, "fees":1.8},
        {"id": "src1-"+str(uuid.uuid4())[:8], "source":"ExampleMarket", "title":"Smartphone Case (lot)", "buy_price":4.0, "shipping":6.0, "fees":1.0},
    ]
    return samples

def compute_profit_estimate(buy_price, shipping, fees, expected_resell_price, est_returns=0.0):
    cost = buy_price + shipping + fees
    profit = expected_resell_price - (cost + est_returns)
    profit = float(Decimal(profit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    roi = None
    if cost > 0:
        roi = float(Decimal((profit / cost) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return profit, roi

def estimate_resell_price(item):
    if "headphone" in item["title"].lower() or "headphones" in item["title"].lower():
        return max(item["buy_price"] * 2.5, 49.99)
    if "board game" in item["title"].lower():
        return max(item["buy_price"] * 3, 39.99)
    return max(item["buy_price"] * 2.0, item["buy_price"] + 15.0)

@app.route("/")
def index():
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, source, title, buy_price, shipping, fees, inspected, approved, status FROM items ORDER BY ROWID DESC")
    items = c.fetchall()
    conn.close()
    items = [dict(zip(["id","source","title","buy_price","shipping","fees","inspected","approved","status"], row)) for row in items]
    enriched = []
    for it in items:
        expected = estimate_resell_price(it)
        profit, roi = compute_profit_estimate(it["buy_price"], it["shipping"], it["fees"], expected)
        it["expected_resell"] = expected
        it["profit"] = profit
        it["roi"] = roi
        enriched.append(it)
    return render_template("index.html", items=enriched)

@app.route("/fetch")
def fetch():
    samples = fetch_marketplace_samples()
    conn = db_conn()
    c = conn.cursor()
    for s in samples:
        c.execute("SELECT 1 FROM items WHERE id = ?", (s["id"],))
        if c.fetchone(): continue
        c.execute("INSERT INTO items (id, source, title, buy_price, shipping, fees, sku) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (s["id"], s["source"], s["title"], s["buy_price"], s["shipping"], s["fees"], s["id"]))
    conn.commit()
    conn.close()
    flash("Fetched sample items (simulated).", "info")
    return redirect(url_for("index"))

@app.route("/inspect/<item_id>", methods=["POST"])
def inspect(item_id):
    conn = db_conn()
    c = conn.cursor()
    c.execute("UPDATE items SET inspected = 1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Item inspected.", "success")
    return redirect(url_for("index"))

@app.route("/approve/<item_id>", methods=["POST"])
def approve(item_id):
    conn = db_conn()
    c = conn.cursor()
    c.execute("UPDATE items SET approved = 1, status = 'purchased' WHERE id = ?", (item_id,))
    c.execute("SELECT buy_price, shipping, fees, title FROM items WHERE id = ?", (item_id,))
    row = c.fetchone()
    buy_price, shipping, fees, title = row
    expected = estimate_resell_price({"title": title, "buy_price": buy_price})
    listing_id = "lst-" + str(uuid.uuid4())[:8]
    c.execute("INSERT INTO listings (id, item_id, platform, list_price, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
              (listing_id, item_id, "ExampleMarketListingDraft", expected))
    conn.commit()
    conn.close()
    flash("Item approved & sandbox-purchased. Listing draft created (simulated).", "success")
    return redirect(url_for("index"))

# ----------------------------
# FACEBOOK MARKETPLACE STUBS
# ----------------------------
# NOTE: Meta/ Facebook Marketplace provides partner APIs but access generally requires
# approval / partnership and uses Graph API endpoints. The routes below are SIMULATED
# placeholders — replace the TODO blocks with real Graph API calls once you have
# an app, access tokens, and the required permissions.
#
# References: See README.md in the project for links to the official docs.
@app.route("/fetch_fb")
def fetch_fb():
    # Simulated fetch from Facebook Marketplace: in production,
    # you'd call the Content Library API or Marketplace Partner Item API
    # with proper OAuth tokens and permissions.
    samples = [
        {"id": "fb-"+str(uuid.uuid4())[:8], "source":"FacebookMarketplace", "title":"FB Used Headphones - Good", "buy_price":28.0, "shipping":0.0, "fees":3.0},
        {"id": "fb-"+str(uuid.uuid4())[:8], "source":"FacebookMarketplace", "title":"FB Vintage Lamp", "buy_price":12.0, "shipping":0.0, "fees":1.2},
    ]
    conn = db_conn()
    c = conn.cursor()
    for s in samples:
        c.execute("SELECT 1 FROM items WHERE id = ?", (s["id"],))
        if c.fetchone(): continue
        c.execute("INSERT INTO items (id, source, title, buy_price, shipping, fees, sku) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (s["id"], s["source"], s["title"], s["buy_price"], s["shipping"], s["fees"], s["id"]))
    conn.commit()
    conn.close()
    flash("Fetched simulated FB Marketplace items (stub).", "info")
    return redirect(url_for("index"))

@app.route("/list_fb/<item_id>", methods=["POST"])
def list_fb(item_id):
    # Simulated create listing on Facebook Marketplace:
    # TODO: Replace this with Graph API POST to create a listing (requires partner access).
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT buy_price, shipping, fees, title FROM items WHERE id = ?", (item_id,))
    row = c.fetchone()
    buy_price, shipping, fees, title = row
    expected = estimate_resell_price({"title": title, "buy_price": buy_price})
    listing_id = "fb-list-" + str(uuid.uuid4())[:8]
    c.execute("INSERT INTO listings (id, item_id, platform, list_price, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
              (listing_id, item_id, "FacebookMarketplaceDraft", expected))
    c.execute("UPDATE items SET status = 'listed' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Created Facebook listing draft (simulated).", "success")
    return redirect(url_for("index"))

@app.route("/listings")
def listings():
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, item_id, platform, list_price, created_at FROM listings ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    listings = [dict(zip(["id","item_id","platform","list_price","created_at"], r)) for r in rows]
    return render_template("listings.html", listings=listings)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
