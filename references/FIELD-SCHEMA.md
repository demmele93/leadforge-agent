# LeadForge field schema

The lead database (`leads/queue.jsonl`) is ONE ROW PER CONTACT. Contacts belonging to the
same business share `business_id` and `business` name. The dashboard groups them.

## Per-contact fields
- business_id     : stable slug for the business (e.g. "acme-roofing")
- business        : display name of the business
- role            : "main" | "owner" | "gm" | "marketing" | "ops" | etc. ("main" = primary)
- first           : contact first+last name (blank if unknown, never guessed)
- title           : contact job title
- email           : verified business/role email (blank if none published)
- phone           : business main phone (verified)
- cell            : personal mobile ONLY if explicitly published (blank otherwise)
- sources         : [array of URLs that substantiate name/phone/email/cell]
- confidence      : "high" | "med" | ""  ("" = unverified/blank)
- vertical        : industry vertical
- town, state     : location
- pain            : detected pain signal (outage, new opening, expansion, complaint)
- stage           : s0..s4
- touch           : number of outreach touches sent
- next_touch_date : ISO date
- status          : s1/s2/s3/s4 + flags
- score           : hotness score 0-100 (super_hot >= 85)
- notes           : free text

## Stage model (RESEARCH-CONTRACT.md)
- s0 signal      : business shows a trigger (complaint / new opening / expansion)
- s1 business_id : named business + location confirmed
- s2 contact     : verified phone and/or email captured (no guesses)
- s3 qualify     : confirmed decision-maker fit
- s4 hot         : verified contact + active pain -> outreach-ready (paid plans only)

## Business grouping (dashboard)
- Main row = business, showing `main` contact (general website contact) as primary.
- Dropdown per business lists all contacts (even if only one) for vertical outreach.
- Blank names render as "—" (never a guessed value).
