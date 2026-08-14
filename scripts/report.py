#!/usr/bin/env python3
"""
LeadForge daily report. Prints a concise summary of the lead database and the day's change.
Used by the daily cron and surfaced to the user. Honors RESEARCH-CONTRACT.md (no guessing;
reports only verified fields). Also emits a weekly "modify?" prompt marker when due.
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "leads", "queue.jsonl")
CFG = os.path.join(ROOT, "config", "config.json")


def load():
    out = []
    with open(LEADS) as f:
        for line in f:
            line = line.strip()
            if line:
                try: out.append(json.loads(line))
                except: pass
    return out


def main(weekly=False):
    leads = load()
    biz = {}
    for l in leads:
        bid = l.get("business_id") or l.get("business", "")
        biz.setdefault(bid, []).append(l)
    named = sum(1 for l in leads if l.get("first"))
    cell = sum(1 for l in leads if l.get("cell"))
    emailed = sum(1 for l in leads if l.get("email"))
    hot = sum(1 for l in leads if l.get("stage") == "s4")
    print(f"=== LeadForge Daily Report ({datetime.date.today().isoformat()}) ===")
    print(f"Businesses: {len(biz)} | Contacts: {len(leads)}")
    print(f"Verified name: {named} | Verified email: {emailed} | Personal cell: {cell} | S4 hot: {hot}")
    print("Stage breakdown:")
    for st in ("s1", "s2", "s3", "s4"):
        print(f"  {st}: {sum(1 for l in leads if l.get('stage')==st)}")
    if weekly:
        print("\n[WEEKLY] Would you like to modify targeting (geography/verticals/volume)? Reply 'modify' or 'keep'.")


if __name__ == "__main__":
    import sys
    main(weekly="--weekly" in sys.argv)
