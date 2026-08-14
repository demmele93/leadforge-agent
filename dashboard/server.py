#!/usr/bin/env python3
"""
LeadForge dashboard server. Brand-themed from config/config.json.
Businesses are the main rows; clicking a row opens a dropdown of that business's contacts.
Reads leads/queue.jsonl.
"""
import json, os, http.server, urllib.parse, datetime
from functools import partial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "leads", "queue.jsonl")
CONFIG = os.path.join(ROOT, "config", "config.json")
DASH = os.path.join(ROOT, "dashboard")

DEFAULT_BRAND = {"name": "LeadForge", "color_primary": "#1f6feb", "color_accent": "#0b3d91", "logo_url": ""}


def brand():
    if os.path.exists(CONFIG):
        try:
            c = json.load(open(CONFIG))
            return {**DEFAULT_BRAND, **c.get("brand", {})}
        except Exception:
            pass
    return DEFAULT_BRAND


def load_leads():
    out = []
    if os.path.exists(LEADS):
        with open(LEADS) as f:
            for line in f:
                line = line.strip()
                if line:
                    try: out.append(json.loads(line))
                    except: pass
    return out


def business_view():
    """Group contacts by business for the dashboard."""
    leads = load_leads()
    biz = {}
    for l in leads:
        bid = l.get("business_id") or l.get("business", "")
        biz.setdefault(bid, []).append(l)
    rows = []
    for bid, rows_l in biz.items():
        main = next((r for r in rows_l if r.get("role") == "main"), rows_l[0])
        contacts = []
        for r in rows_l:
            contacts.append({
                "role": r.get("role", ""), "name": r.get("first", "") or "—",
                "title": r.get("title", ""), "phone": r.get("phone", "") or "—",
                "cell": r.get("cell", "") or "—", "email": r.get("email", "") or "—",
                "conf": r.get("confidence", "") or "",
            })
        rows.append({
            "id": bid, "business": main.get("business", ""), "vertical": main.get("vertical", ""),
            "town": main.get("town", ""), "state": main.get("state", ""),
            "main": contacts[0], "contacts": contacts,
            "pain": main.get("pain", "") or "—", "stage": main.get("stage", "s1"),
            "score": main.get("score", 0), "source": main.get("source", ""),
        })
    return rows


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DASH, **kw)

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/leads":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "brand": brand(), "leads": business_view(),
                "generated": datetime.datetime.now().isoformat(),
            }).encode())
            return
        return super().do_GET()


def main():
    port = int(os.environ.get("PORT", "8787"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Dashboard: http://127.0.0.1:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
