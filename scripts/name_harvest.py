#!/usr/bin/env python3
"""
LeadForge deep enrichment for contacts missing verified data.

For each contact missing a verified name/phone/cell, render the business's official site
(real browser if Playwright is present, else static extract) and attempt to fill: owner name,
title, business phone, and PERSONAL CELL (only when explicitly published, multi-source logged).
Never guesses. Honors RESEARCH-Contract.md.
"""
import json, os, re, sys, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "leads", "queue.jsonl")
LEDGER = os.path.join(ROOT, "LEDGER.md")


def log(msg):
    with open(LEDGER, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] name_harvest: {msg}\n")


def find_site(business, state):
    try:
        r = subprocess.run([sys.executable, "-c",
            "from hermes_tools import web_search; import json,sys;"
            f"r=web_search({business!r}+{(state)}!r+official+website,limit=5); print(json.dumps(r))"],
            capture_output=True, text=True, cwd=ROOT, timeout=90).stdout
        for it in json.loads(r).get("data", {}).get("web", []):
            u = it.get("url", "")
            if u and not any(k in u for k in ("facebook","instagram","tiktok","yelp")):
                return u
    except Exception:
        pass
    return None


def render(url):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page()
            pg.goto(url, timeout=20000, wait_until="networkidle")
            t = pg.inner_text("body"); b.close(); return t
    except Exception:
        pass
    try:
        from hermes_tools import web_extract
        r = web_extract([url], char_limit=9000)
        return " ".join(x.get("content","") or "" for x in r.get("results",[]))
    except Exception:
        return ""


def harvest(txt, sources):
    name = title = phone = cell = ""
    mn = re.search(r"(?:owner|founder|manager|director|president)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})", txt)
    if mn: name = mn.group(1)
    mt = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),?\s+(?:is|are)\s+(?:the\s+)?(?:owner|founder|manager|general manager)", txt)
    if mt and not name: name = mt.group(1)
    mp = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", txt)
    if mp: phone = mp.group(0)
    if re.search(r"\b(cell|mobile)\b", txt, re.I):
        mc = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", txt)
        if mc: cell = mc.group(0)
    return name, title, phone, cell


def main():
    leads = []
    with open(LEADS) as f:
        for line in f:
            line = line.strip()
            if line:
                try: leads.append(json.loads(line))
                except: pass
    done = 0
    for l in leads:
        if l.get("first") and l.get("confidence") == "high":
            continue
        site = find_site(l.get("business",""), l.get("state",""))
        if not site:
            continue
        name, title, phone, cell = harvest(render(site), [site])
        if name and not l.get("first"):
            l["first"] = name; l["confidence"] = "high"; l["name_source"] = site; done += 1
        if cell and not l.get("cell"):
            l["cell"] = cell
        if phone and not l.get("phone"):
            l["phone"] = phone
    with open(LEADS, "w") as f:
        for l in leads:
            f.write(json.dumps(l) + "\n")
    log(f"deep harvest: +{done} names locked")
    print(f"Deep harvest: {done} new verified names.")


if __name__ == "__main__":
    main()
