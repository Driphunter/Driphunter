"""
DRIP HUNTER v3 - Backend Flask
Sneakers + Streetwear + Luxe + Vintage
"""

from flask import Flask, jsonify, request, send_from_directory
import requests, time, random, threading
from datetime import datetime

app = Flask(__name__, static_folder="static")

# ─── SEARCHES PAR CATÉGORIE ─────────────────────────────────
# Format: keyword, prix_max, fourchette_revente (min,max), liquidite_jours
SEARCHES = {
    "sneakers": [
        {"keyword": "Nike Air Force 1",    "prix_max": 45,  "rev_min": 70,  "rev_max": 95,  "liq": 3},
        {"keyword": "Jordan 1",            "prix_max": 70,  "rev_min": 120, "rev_max": 160, "liq": 2},
        {"keyword": "Jordan 4",            "prix_max": 80,  "rev_min": 140, "rev_max": 185, "liq": 2},
        {"keyword": "Nike Dunk Low",       "prix_max": 55,  "rev_min": 95,  "rev_max": 130, "liq": 3},
        {"keyword": "Adidas Yeezy 350",    "prix_max": 90,  "rev_min": 160, "rev_max": 220, "liq": 3},
        {"keyword": "New Balance 550",     "prix_max": 40,  "rev_min": 70,  "rev_max": 95,  "liq": 4},
        {"keyword": "New Balance 2002r",   "prix_max": 50,  "rev_min": 85,  "rev_max": 115, "liq": 4},
        {"keyword": "Asics Gel Lyte III",  "prix_max": 35,  "rev_min": 65,  "rev_max": 90,  "liq": 5},
        {"keyword": "Nike Air Max 90",     "prix_max": 40,  "rev_min": 70,  "rev_max": 95,  "liq": 5},
        {"keyword": "Salomon XT-6",        "prix_max": 60,  "rev_min": 110, "rev_max": 150, "liq": 3},
    ],
    "streetwear": [
        {"keyword": "Stone Island",        "prix_max": 60,  "rev_min": 110, "rev_max": 150, "liq": 3},
        {"keyword": "Arc'teryx",           "prix_max": 90,  "rev_min": 160, "rev_max": 210, "liq": 2},
        {"keyword": "Carhartt WIP",        "prix_max": 30,  "rev_min": 55,  "rev_max": 80,  "liq": 4},
        {"keyword": "Palace skateboards",  "prix_max": 40,  "rev_min": 75,  "rev_max": 110, "liq": 3},
        {"keyword": "Supreme",             "prix_max": 80,  "rev_min": 150, "rev_max": 220, "liq": 2},
        {"keyword": "Stussy",              "prix_max": 30,  "rev_min": 55,  "rev_max": 80,  "liq": 5},
        {"keyword": "Represent clothing",  "prix_max": 55,  "rev_min": 100, "rev_max": 140, "liq": 4},
        {"keyword": "Aime Leon Dore",      "prix_max": 55,  "rev_min": 100, "rev_max": 145, "liq": 4},
        {"keyword": "Kith hoodie",         "prix_max": 50,  "rev_min": 90,  "rev_max": 130, "liq": 4},
        {"keyword": "Comme des Garcons",   "prix_max": 50,  "rev_min": 95,  "rev_max": 135, "liq": 4},
    ],
    "luxe": [
        {"keyword": "Moncler",             "prix_max": 150, "rev_min": 280, "rev_max": 380, "liq": 4},
        {"keyword": "Balenciaga sneakers", "prix_max": 120, "rev_min": 220, "rev_max": 310, "liq": 4},
        {"keyword": "Louis Vuitton ceinture","prix_max":120,"rev_min": 200, "rev_max": 280, "liq": 5},
        {"keyword": "Gucci",               "prix_max": 130, "rev_min": 230, "rev_max": 320, "liq": 5},
        {"keyword": "Prada",               "prix_max": 130, "rev_min": 240, "rev_max": 330, "liq": 5},
        {"keyword": "Burberry",            "prix_max": 100, "rev_min": 180, "rev_max": 250, "liq": 5},
        {"keyword": "Bottega Veneta",      "prix_max": 140, "rev_min": 260, "rev_max": 360, "liq": 5},
        {"keyword": "Dior sneakers",       "prix_max": 160, "rev_min": 290, "rev_max": 400, "liq": 5},
        {"keyword": "Ami Paris",           "prix_max": 70,  "rev_min": 120, "rev_max": 170, "liq": 4},
        {"keyword": "Jacquemus",           "prix_max": 60,  "rev_min": 110, "rev_max": 155, "liq": 4},
    ],
    "vintage": [
        {"keyword": "Levi's 501 vintage",  "prix_max": 20,  "rev_min": 45,  "rev_max": 70,  "liq": 5},
        {"keyword": "Bomber vintage",      "prix_max": 25,  "rev_min": 55,  "rev_max": 85,  "liq": 6},
        {"keyword": "Nike vintage 90s",    "prix_max": 30,  "rev_min": 65,  "rev_max": 100, "liq": 5},
        {"keyword": "Adidas vintage",      "prix_max": 25,  "rev_min": 55,  "rev_max": 85,  "liq": 6},
        {"keyword": "Polo Ralph Lauren vintage","prix_max":20,"rev_min":45, "rev_max": 75,  "liq": 6},
        {"keyword": "Lacoste vintage",     "prix_max": 20,  "rev_min": 45,  "rev_max": 70,  "liq": 6},
        {"keyword": "Carhartt vintage",    "prix_max": 25,  "rev_min": 55,  "rev_max": 85,  "liq": 5},
        {"keyword": "Wrangler vintage",    "prix_max": 15,  "rev_min": 35,  "rev_max": 60,  "liq": 7},
        {"keyword": "Champion vintage",    "prix_max": 18,  "rev_min": 40,  "rev_max": 65,  "liq": 6},
        {"keyword": "Tommy Hilfiger vintage","prix_max":20, "rev_min": 45,  "rev_max": 75,  "liq": 6},
    ],
}

CONDITION_LABELS = {
    6: "Neuf (étiquette)", 1: "Neuf",
    2: "Très bon état", 3: "Bon état", 4: "Satisfaisant",
}

SOLD_MESSAGES = [
    "Vendu 😔", "Trop tard...", "Déjà parti 💨",
    "Quelqu'un a été plus rapide", "C'était une pépite 💎",
    "Deal expiré", "Plus disponible",
]

BASE_URL = "https://www.vinted.fr"
API_URL  = f"{BASE_URL}/api/v2"
HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": BASE_URL + "/",
}

session = requests.Session()
session.headers.update(HEADERS)

# Cache des statuts vendus
sold_cache = {}

def get_token():
    try:
        session.get(BASE_URL, timeout=10)
    except:
        pass

def liquidity_info(jours):
    if jours <= 2:  return {"label": "Ultra rapide", "level": 5, "color": "green"}
    if jours <= 4:  return {"label": "Rapide",       "level": 4, "color": "lime"}
    if jours <= 6:  return {"label": "Normal",       "level": 3, "color": "yellow"}
    if jours <= 10: return {"label": "Lent",         "level": 2, "color": "orange"}
    return              {"label": "Très lent",       "level": 1, "color": "red"}

def check_item_sold(item_id):
    """Vérifie si une annonce est encore disponible sur Vinted."""
    if item_id in sold_cache:
        return sold_cache[item_id]
    try:
        r = session.get(f"{API_URL}/items/{item_id}", timeout=8)
        if r.status_code == 404:
            sold_cache[item_id] = True
            return True
        data = r.json()
        item = data.get("item", {})
        is_sold = item.get("is_closed", False) or item.get("status", "") in ["sold", "reserved"]
        sold_cache[item_id] = is_sold
        return is_sold
    except:
        return False

def score_item(item, s):
    prix = float(item.get("price", 0))
    if prix <= 0:
        return None

    rev_mid = (s["rev_min"] + s["rev_max"]) / 2
    frais_achat   = max(prix * 0.05 + 0.70, 1.50)
    cout          = prix + frais_achat
    frais_revente = max(rev_mid * 0.05 + 0.70, 1.50)
    revenu        = rev_mid - frais_revente
    marge         = revenu - cout
    marge_pct     = (marge / cout * 100) if cout > 0 else 0

    s_marge = 35 if marge_pct>=80 else 28 if marge_pct>=50 else 18 if marge_pct>=30 else 10 if marge_pct>=15 else 0
    cond    = item.get("status_id", 0)
    s_etat  = {6:20, 1:18, 2:14, 3:9, 4:4}.get(cond, 0)
    fav     = item.get("favourite_count", 0)
    s_pop   = 15 if fav>=20 else 12 if fav>=10 else 8 if fav>=5 else 4 if fav>=1 else 0
    ts      = item.get("created_at_ts", 0)
    age_h   = (time.time() - ts) / 3600 if ts else 999
    s_fresh = 15 if age_h<1 else 12 if age_h<6 else 8 if age_h<24 else 4 if age_h<72 else 0
    liq     = liquidity_info(s["liq"])
    s_liq   = {5:15, 4:12, 3:9, 2:5, 1:2}.get(liq["level"], 5)

    photo = ""
    if item.get("photo"):
        photo = item["photo"].get("url","") or item["photo"].get("full_size_url","")

    return {
        "id":           item.get("id"),
        "titre":        item.get("title",""),
        "marque":       item.get("brand_title",""),
        "taille":       item.get("size_title",""),
        "etat":         CONDITION_LABELS.get(cond,"Inconnu"),
        "etat_id":      cond,
        "prix_achat":   round(prix, 2),
        "frais_achat":  round(frais_achat, 2),
        "cout_total":   round(cout, 2),
        "rev_min":      s["rev_min"],
        "rev_max":      s["rev_max"],
        "marge_nette":  round(marge, 2),
        "marge_pct":    round(marge_pct, 1),
        "favoris":      fav,
        "age_heures":   round(age_h, 1),
        "score":        s_marge + s_etat + s_pop + s_fresh + s_liq,
        "liquidite":    liq,
        "url":          f"{BASE_URL}/items/{item.get('id')}",
        "photo":        photo,
        "created_at_ts":ts,
        "is_sold":      False,
        "sold_msg":     "",
        "categorie":    s.get("categorie",""),
        "keyword":      s["keyword"],
    }

def fetch_category(cat_name, cutoff_hours=24):
    searches = SEARCHES.get(cat_name, [])
    deals = []
    cutoff = time.time() - (cutoff_hours * 3600)

    for s in searches:
        s_with_cat = {**s, "categorie": cat_name}
        params = {
            "search_text": s["keyword"],
            "currency": "EUR",
            "price_to": s["prix_max"],
            "order": "newest_first",
            "per_page": 96,
            "page": 1,
        }
        try:
            r = session.get(f"{API_URL}/items", params=params, timeout=15)
            r.raise_for_status()
            items = r.json().get("items", [])
            for item in items:
                ts = item.get("created_at_ts", 0)
                if ts < cutoff:
                    continue
                scored = score_item(item, s_with_cat)
                if scored and scored["marge_nette"] > 0:
                    deals.append(scored)
        except:
            pass
        time.sleep(random.uniform(1.0, 2.2))

    return deals

# ── API: scan par catégorie (top 24h) ──
@app.route("/api/scan/top")
def api_scan_top():
    cat  = request.args.get("cat", "sneakers")
    sort = request.args.get("sort", "score")
    get_token()

    deals = fetch_category(cat, cutoff_hours=24)

    if sort == "score":   deals.sort(key=lambda x: x["score"], reverse=True)
    elif sort == "marge": deals.sort(key=lambda x: x["marge_nette"], reverse=True)
    else:                 deals.sort(key=lambda x: x["created_at_ts"], reverse=True)

    return jsonify({"items": deals, "total": len(deals)})

# ── API: scan récent (dernière heure) ──
@app.route("/api/scan/recent")
def api_scan_recent():
    cat = request.args.get("cat", "sneakers")
    get_token()

    deals = fetch_category(cat, cutoff_hours=1)
    deals.sort(key=lambda x: x["created_at_ts"], reverse=True)
    return jsonify({"items": deals, "total": len(deals)})

# ── API: vérifier si une annonce est vendue ──
@app.route("/api/check_sold/<int:item_id>")
def api_check_sold(item_id):
    is_sold = check_item_sold(item_id)
    msg = random.choice(SOLD_MESSAGES) if is_sold else ""
    return jsonify({"id": item_id, "is_sold": is_sold, "msg": msg})

# ── API: vérifier plusieurs annonces en batch ──
@app.route("/api/check_sold_batch", methods=["POST"])
def api_check_sold_batch():
    ids = request.json.get("ids", [])
    results = {}
    for item_id in ids[:20]:  # max 20 à la fois
        is_sold = check_item_sold(item_id)
        results[str(item_id)] = {
            "is_sold": is_sold,
            "msg": random.choice(SOLD_MESSAGES) if is_sold else ""
        }
        time.sleep(0.3)
    return jsonify(results)

@app.route("/api/categories")
def api_categories():
    return jsonify(list(SEARCHES.keys()))

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    get_token()
    app.run(debug=True, host='0.0.0.0', port=5000)
