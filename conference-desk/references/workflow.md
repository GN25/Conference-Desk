# Execution and formats

## Gather and understand

Normal request: `Prepare FOSDEM from <official XML URL> for a platform engineer learning how to operate local AI. Attend Saturday 10:30–18:00, lunch 12:30–13:15. Save to <output>.`

Run with the installed skill's script path:

```sh
python3 scripts/desk.py ingest --source <url-or-local-xml.gz> --out <work>/catalog.json
python3 scripts/desk.py index --catalog <work>/catalog.json
python3 scripts/desk.py read --catalog <work>/catalog.json --tracks 'AI Plumbers' 'Security'
```

`index` prints the complete track inventory and every title with stable ID, track, date, time and room. Use `--tracks` to read complete title indexes for the relevant and adjacent tracks after reviewing the inventory. It is deliberately not a keyword ranker. Consider adjacent tracks and unexpected relevant titles. `read --ids ID ID` reads full abstracts/descriptions and source links; `read --tracks` reads every session in those tracks. Paginate shell output if needed, preserving coverage. For non-XML material, use the host's normal browsing/document tools and write the same catalog shape; explain incomplete coverage rather than pretending the export was complete. Do not execute downloaded code.

Read the actual programme evidence. Relevance scores 1–5 mean marginal through essential **for this attendee**, not intrinsic talk quality. For every plausible choice, write a specific why, two useful questions and a preparation note tied to an exact short excerpt of its abstract/description. Phrase questions as questions, not promised content. A talk title is not evidence for performance or a product claim. Do not fabricate speaker details or imply recordings/slides were watched. Keep a review note describing which tracks were inspected and why other areas were excluded.

## Brief JSON

```json
{
  "goal": "Understand practical local inference operations",
  "display_timezone": "Europe/Madrid",
  "days": [{"date":"2026-01-31","start":"10:30","end":"18:00"}],
  "breaks": [{"date":"2026-01-31","start":"12:30","end":"13:15","label":"Lunch"}],
  "transition_minutes": 15,
  "same_room_minutes": 0,
  "max_sessions_per_day": 6,
  "minimum_score": 3,
  "must_attend": [],
  "assumptions": "Historical programme replay. Walking allowance is a preference, not a measured route."
}
```

Brief dates/times use the **conference timezone**, even when display_timezone differs. Daily windows and breaks are hard constraints. For meetings add a break with its label. Must-attend contains catalog IDs, not fuzzy titles. If mandatory sessions conflict or do not fit, report the exact problem and seek a choice; never silently drop one. The planner considers scores of at least `minimum_score` (default 3) and maximizes their sum under the count cap and room-change rules. A named must-attend overrides the relevance threshold, but never a time constraint. It is not a model of actual walking routes, accessibility, queues or seat availability.

## Decisions JSON

```json
{
  "catalog_sha256": "value from catalog",
  "review": "Reviewed the full track inventory and title indexes plus relevant abstracts; explain exclusions here.",
  "decisions": [{
    "id": "stable catalog ID",
    "score": 5,
    "why": "Specific relationship to the attendee goal.",
    "evidence": "Exact short substring from this session's abstract or description",
    "questions": ["Specific question?", "Another useful question?"],
    "preparation": "What to review or capture for this session."
  }]
}
```

Do not write generic notes just to satisfy the schema. The script verifies the excerpt but cannot prove your interpretation is sound. Include enough relevant alternatives to make actual tradeoffs. Lower scores or exclude tangential sessions instead of filling every minute.

## Produce and check

```sh
python3 scripts/desk.py build --catalog <work>/catalog.json --brief <work>/brief.json --decisions <work>/decisions.json --out <output>
python3 scripts/desk.py verify --out <output>
```

Inspect `plan.json`, `agenda.md` and `index.html`. Check that the chosen sessions form a sensible narrative, questions are specific, breaks and room transitions fit, and every skipped high-value session has a useful explanation. The pack lists all rated alternatives, including out-of-window and blocked ones. These are **alternatives**, not all drop-in replacements: consult the shown constraints before swapping. Open the HTML using available local browser tools, check desktop and narrow layouts where possible, and fix clipping or unreadable content. The default folder is the authorized destination. Optional calendar import is a separate user action; importing the same ICS twice can create duplicates depending on the calendar client.

`verify` checks file hashes, the ICS entries against chosen IDs/times, and re-solves the plan from its archived inputs. Also do the semantic review; a hash check does not evaluate talk quality. Report remaining manual work: review subjective choices, check the live official programme before attending, import the ICS if desired, and attend. Use UTC ICS timestamps to preserve exact instants across calendar timezones. UID stays stable for a given conference/session; refresh files are not a live subscription and omit cancelled entries rather than sending cancellation messages.

## Refresh and input schema

```sh
python3 scripts/desk.py changes --before old/catalog.json --after new/catalog.json
```

The change report distinguishes added/removed IDs and changed scheduling/content. Old decisions deliberately fail against a new catalog hash. Re-evaluate changed notes and new sessions, then set the new hash. Never merely change the hash to bypass review.

Catalog JSON contains `conference` (title, timezone, base_url, id), `source` (url, sha256, fetched_at), `catalog_sha256` and `events`. Each event has `id`, `title`, `start` (ISO with offset), `end`, `room`, `track`, `url`, `speakers` (list), `abstract`, `description`, and `links` (list of label/url objects). `catalog_sha256` is SHA256 of canonical JSON excluding that field. Normalization must retain the source facts exactly; missing offset/timezone or duplicate IDs are errors. `ingest` currently handles the XML dialect used by the bundled FOSDEM examples. Other exporters may need an adapter; do not claim universal support.
