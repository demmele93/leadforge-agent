# Research Contract — LeadForge compliance rules

Every enrichment action MUST obey these rules. They are non-negotiable and embedded in
the skill prompt so the agent enforces them even when autonomous.

## 1. Geography & vertical
- Only research businesses inside the target geography the user specified.
- Only the industry verticals the user specified (default: any B2B / local business).
- Never consumer-only targeting unless the user explicitly asks.

## 2. No fabricated contacts (hard rule)
- NEVER invent an email, phone, or name.
- An email is "verified" only if it appears on the business's own site, a directory, or a
  public record. Guessed patterns (`name@example.com`) are FORBIDDEN.
- A phone is "verified" only if published on a public source.
- A name is "verified" only if it appears on an official/about/press source.

## 3. Personal cell phone (special handling)
- Personal mobile numbers are captured ONLY when EXPLICITLY published on a public source
  (bio page, staff directory, press quote with number, etc.).
- ALWAYS cross-check across MULTIPLE sources before logging a personal cell.
- Log every source URL in the contact's `sources` array.
- If not published anywhere, leave `cell` blank. Do not infer from landline or guess.

## 4. Multi-contact enrichment
- Always capture the MAIN business contact (website general contact / front desk).
- Attempt to enrich ADDITIONAL people per business: owner, GM, marketing, ops.
- One ROW PER CONTACT, each tagged with `business_id` and `role`.
- The dashboard shows businesses as the main row; contacts expand via dropdown.

## 5. Deeper enrichment
- If the user says "enrich" on a lead, or the lead is scored SUPER HOT, run an extra
  multi-source pass: personal cell hunt, LinkedIn/title confirmation, recent news.

## 6. Outreach (opt-in only)
- Sending email/SMS is DISABLED by default.
- Only enabled on a paid plan (see OUTREACH.md) AND with explicit user authorization.
- Always include opt-out; honor STOP/unsubscribe immediately.
- No more than the authorized daily cap; 3-touch maximum per lead.

## 7. Sources & logging
- Every fact (name, phone, email, cell) records its `sources` (URLs) and `confidence`.
- confidence: high = direct official source; med = secondary/public directory.
- The LEDGER.md logs each enrichment run with counts.

## 8. Brand respect
- The dashboard inherits the user's brand colors/name from config.json.
- If the user provided a website, default brand from it; ask only what's missing.
