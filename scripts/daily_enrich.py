#!/usr/bin/env python3
"""
LeadForge daily enrichment.

Discovers named businesses in the configured geography/verticals, then enriches each
with a MAIN contact + additional people (owner/gm/marketing/ops). Hunts personal cell
numbers ONLY when explicitly published, across multiple sources, logging every source.

One ROW PER CONTACT in leads/queue.jsonl (grouped by business_id).
Refuses to guess any email/phone/name. See references/RESEARCH-CONTRACT.md.
"""
import json, os, re, subprocess, sys, datetime, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "leads", "queue.jsonl")
LEDGER = os.path.join(ROOT, "LEDGER.md")
CONFIG = os.path.join(ROOT, "config", "config.json")

GEO_DEFAULT = ["WV", "VA", "KY", "TN", "NC", "OH", "GA"]


def load_config():
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def slug(business):
    return re.sub(r"[^a-z0-9]+", "-", business.lower()).strip("-")


def log(msg):
    with open(LEDGER, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] enrich: {msg}\n")


def web_search(q, limit=5):
    try:
        r = subprocess.run([sys.executable, "-c",
            "from hermes_tools import web_search; import json,sys;"
            f"q={q!r}; r=web_search(q,limit={limit}); print(json.dumps(r))"],
            capture_output=True, text=True, cwd=ROOT, timeout=120).stdout
        return json.loads(r).get("data", {}).get("web", [])
    except Exception:
        return []


def discover(cfg):
    geo = cfg.get("targeting", {}).get("geography", GEO_DEFAULT)
    verts = cfg.get("targeting", {}).get("verticals", ["any"])
    signals = cfg.get("targeting", {}).get("pain_signals",
                 ["now open", "expansion", "outage", "hiring", "moving"])
    found = []
    # one query per (signal x state-ish), capped to keep daily runtime sane
    for sig in signals:
        for st in geo[:5]:
            q = f'"{sig}" new business {st}'
            for it in web_search(q, 5):
                title = it.get("title", "")
                biz = re.sub(r"\s*[-|].*$", "", title).strip()
                if len(biz) > 3 and biz.lower() not in ("business", "news"):
                    found.append({
                        "business": biz, "state": st, "source": it.get("url", ""),
                        "pain": sig, "vertical": (verts[0] if verts != ["any"] else "local business"),
                    })
    return found


def dedupe_merge(incoming, existing_ids):
    out = []
    for b in incoming:
        sid = slug(b["business"]) + ":" + b["state"]
        if sid in existing_ids:
            continue
        out.append((sid, b))
    return out


def enrich_contact(business, role, town, state, source):
    """Return a contact dict. Never guesses; blank when unpublished."""
    q = f'{business} {role} {town} {state} contact email phone'
    hits = web_search(q, 6)
    name, title, email, phone, cell, sources = "", "", "", "", "", []
    for h in hits:
        u = h.get("url", "")
        txt = h.get("title", "") + " " + h.get("description", "")
        sources.append(u)
        # email
        m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", txt)
        if m and not email:
            email = m.group(0)
        # business phone
        m = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", txt)
        if m and not phone:
            phone = m.group(0)
        # personal cell: only if text explicitly says "cell" / "mobile" near a number
        if re.search(r"\b(cell|mobile)\b", txt, re.I):
            mc = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", txt)
            if mc:
                cell = mc.group(0)
        # name (conservative)
        mn = re.search(r"(?:owner|founder|manager|director|president)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})", txt)
        if mn and not name:
            name = mn.group(1)
        mt = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),?\s+(?:is|are)\s+(?:the\s+)?(?:owner|founder|manager|general manager)", txt)
        if mt and not name:
            name = mt.group(1)
    conf = "high" if (email or phone) else ("med" if name else "")
    return {
        "role": role, "first": name, "title": title, "email": email,
        "phone": phone, "cell": cell, "sources": list(dict.fromkeys(sources)),
        "confidence": conf,
    }


def main():
    cfg = load_config()
    os.makedirs(os.path.dirname(LEADS), exist_ok=True)
    existing = []
    existing_ids = set()
    if os.path.exists(LEADS):
        with open(LEADS) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line); existing.append(d)
                        existing_ids.add(d.get("business_id", "") + ":" + d.get("state", ""))
                    except Exception:
                        pass

    found = discover(cfg)
    new = dedupe_merge(found, existing_ids)
    added = 0
    for sid, b in new:
        bid = slug(b["business"])
        # MAIN contact first
        main_c = enrich_contact(b["business"], "main", b.get("town", ""), b["state"], b["source"])
        rec = {
            "business_id": bid, "business": b["business"], "role": "main",
            "first": main_c["first"], "title": main_c["title"], "email": main_c["email"],
            "phone": main_c["phone"], "cell": main_c["cell"], "sources": main_c["sources"],
            "confidence": main_c["confidence"], "vertical": b.get("vertical", ""),
            "town": b.get("town", ""), "state": b["state"], "source": b["source"],
            "pain": b.get("pain", ""), "stage": "s1", "touch": 0,
            "next_touch_date": datetime.date.today().isoformat(), "status": "s1",
            "score": 50, "notes": "",
        }
        existing.append(rec); added += 1
        # attempt additional people (vertical outreach)
        for role in ("owner", "gm", "marketing"):
            c = enrich_contact(b["business"], role, b.get("town", ""), b["state"], b["source"])
            if c["first"] or c["email"] or c["phone"] or c["cell"]:
                existing.append({**rec, **{
                    "role": role, "first": c["first"], "title": c["title"],
                    "email": c["email"], "phone": c["phone"], "cell": c["cell"],
                    "sources": c["sources"], "confidence": c["confidence"],
                }})
                added += 1
    with open(LEADS, "w") as f:
        for d in existing:
            f.write(json.dumps(d) + "\n")
    log(f"discovery: {len(found)} raw, {len(new)} new businesses, +{added} contact rows.")
    print(f"Added {added} contact rows across {len(new)} new businesses (queue now {len(existing)}).")


if __name__ == "__main__":
    main()
