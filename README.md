# Night-Out Curator

A localhost browser application for planning Phoenix/Tempe outings with a
tool-using LangGraph workflow. The current hybrid prototype and original Phase-0
baseline are both included; their commands and data modes are different.

## Prerequisites

- Python **3.13**, the tested runtime, with `pip` and virtual environment support.
- A modern browser such as Chrome, Edge or Firefox.
- Internet access for live venue discovery, hosted models, fonts, icons and map tiles.
- For real planning: credentials and model access for a supported LLM provider.
  The current tested setup is **Claude Haiku 4.5 on AWS Bedrock**.
- For reliable live discovery: a **Geoapify API key**. Public OpenStreetMap/Overpass
  is attempted without one, but service availability is not guaranteed.

No database, Node.js frontend build, or cloud deployment is required for the UI.
Credentials stay in the Python server, not in the browser.

## Quick Start: Localhost UI

Run from the repository root. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-milestone2.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` in your editor using the configuration below. **Do not overwrite an
existing populated `.env`.** It is ignored by Git; never commit it, put keys in
screenshots, or paste credentials into chat.

For Bedrock Haiku with one Bedrock API key and live venue discovery:

```dotenv
LLM_PROVIDER=bedrock_converse
LLM_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0
AWS_REGION=us-east-2
AWS_BEARER_TOKEN_BEDROCK=YOUR_BEDROCK_API_KEY
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
GEOAPIFY_KEY=YOUR_GEOAPIFY_API_KEY
```

`us-east-2` is the region verified in this workspace. Use the region matching your
credentials and model access; a region mismatch can appear as an invalid-key error.
The example file's `us-east-1` setting is only a default, not a requirement.

If AWS issued an **access-key pair**, leave `AWS_BEARER_TOKEN_BEDROCK` blank and
fill `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` instead. Temporary credentials
also require `AWS_SESSION_TOKEN`. Bedrock credentials are not an Anthropic API key.
Single quotes, double quotes, and unquoted values are supported by `python-dotenv`;
copy the exact credential without line breaks or a `Bearer ` prefix.

Get a venue-discovery key from [Geoapify MyProjects](https://myprojects.geoapify.com/).
Its free plan has usage quotas; check your account's current allowance. Requests
originate from the Python server, so key restrictions must permit server-side access.

Check configuration without invoking the model, then optionally send one small
real request to verify Bedrock authentication and structured output:

```powershell
.\.venv\Scripts\python.exe scripts/check_bedrock.py
.\.venv\Scripts\python.exe scripts/check_bedrock.py --invoke
```

The check reports key presence rather than values. `--invoke` and Real LLM runs can
incur AWS charges; confirm credit eligibility, expiry, model access and quotas.
Credits do not remove rate limits or guarantee zero out-of-pocket cost.

Start the UI:

```powershell
.\.venv\Scripts\python.exe run_ui.py --port 8765
```

Open **http://127.0.0.1:8765**. Keep the terminal running while using the browser;
stop the server with **Ctrl+C**. If that port is occupied, use `--port 8766` and
open http://127.0.0.1:8766. The server binds only to `127.0.0.1`; no public hosting
or deployment is needed. Restart it after changing `.env`. Existing process
environment variables take precedence over values loaded from `.env`.

These commands use the virtual environment directly, so PowerShell activation
is unnecessary. With an already-configured interpreter, use `python` instead of
`.\.venv\Scripts\python.exe`. Install `requirements-milestone2.txt` for the current
UI; `requirements.txt` preserves older baseline pins and should use a separate
environment if reproducing those exact versions.

On macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-milestone2.txt
test -f .env || cp .env.example .env
# Edit .env before starting the UI.
.venv/bin/python run_ui.py --port 8765
```

### Browser Test

The **Live provider** selector now supports Google Maps and Geoapify. A configured
`GOOGLE_MAPS_API_KEY` selects Google by default after server restart. Your existing
Maps demo key can be used for its supported test APIs; keep it separate from Gemini.
Select an outing date so Google hours are evaluated at the requested local time.
Google-source plans use Google walking routes; weather remains a bundled sample.

Google price ranges and tiers are guidance, not exact meal quotes. A plan can be
**provisional** when the upper guidance range fits the cap but exact cost is unverified;
its exact-budget check remains false. Vegetarian indicators never establish vegan
suitability. Dietary requests with insufficient menu evidence remain unresolved.
Google results use Google Maps attribution and links, not the OpenStreetMap panel.
Raw Google Places JSON export is disabled; CLI Google output is restricted to metrics
and check outcomes. No user photos or reviews are requested with the demo key.

1. Set the request and form constraints. Budget is a **maximum per person**:
  use $20/person for a $40 total budget for two people. Changing only the text
  does not automatically replace party size, stop count or every other form value.
2. Select dinner cuisine, time, dietary requirements and 1-4 ordered stops.
  Common cuisine names can be inferred from the request; the selector takes precedence.
3. Choose **Live listings**, an area/radius and a result limit. Click **Browse places**
  to inspect venues and sources without LLM calls.
4. Choose **Real LLM** and click **Plan evening**. Watch streamed stage progress;
  inspect Itinerary, Places, Activity and JSON, or download the displayed result.
5. For deterministic no-LLM testing, choose **Mock** and **Fixture catalog**.

The initial saved result, if present, may use old fixture data and is explicitly
labeled. A high budget is a ceiling, not a premium-dining preference; explicitly
request upscale dining when desired. Missing price, hours or dietary evidence can
produce an **unresolved** plan. The browser has a three-minute response timeout;
the graph checks a cooperative two-minute deadline between stages, not a hard
interruption of an in-flight provider request.

### Optional Keys and Current Limits

For a small Google Maps demo-key versus Geoapify comparison, add a separate key
to the ignored `.env` (this is not Gemini's `GOOGLE_API_KEY`):

```dotenv
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_DEMO_KEY
```

Then run the same Indian-restaurant requirement through both adapters:

```powershell
python scripts/compare_places.py --area tempe --cuisine indian --radius-m 5000 --limit 10 --party-size 2 --budget-pp 40
```

Use `--budget-pp 20` if $40 is the total budget for two people. This preliminary
comparison makes one search per provider, no LLM calls, and saves only timing and
field-coverage metrics to `artifacts/provider_comparison.json`, not raw Google
Places records. It does not switch the browser's provider or generate a plan.
Google uses text search plus an in-radius filter; Geoapify uses category search,
so rankings and counts are not directly a measure of accuracy. Missing credentials
stop the script before API requests. Demo-key quotas and field availability apply;
prices and vegetarian indicators do not establish an exact bill or vegan suitability.

Only one LLM provider is required. Other supported choices use `OPENAI_API_KEY`
with `LLM_PROVIDER=openai`, `ANTHROPIC_API_KEY` with `anthropic`, or `GOOGLE_API_KEY`
with `google_genai`. Set `LLM_MODEL` to a model currently accessible to your account.
Ollama requires a running local service and downloaded model rather than a hosted key.

`TRANSITLAND_KEY` is optional for the legacy transit tool's live mode; it is not
required for browsing venues or Haiku planning. Verified Valley Metro light-rail
and Tempe Orbit journey planning are not implemented in the browser yet.
Open-Meteo needs no key, but browser weather currently uses a bundled sample.
Walking uses straight-line estimates, not verified walking routes. Current
availability, party capacity, weekday-specific schedules, reservations and payments
are not verified. Live listings are bounded provider results, not an exhaustive
or independently verified business directory.

## Milestone 2 hybrid prototype

### Browser interface

Venue data is now selectable independently of the LLM. Live listings queries
Geoapify when `GEOAPIFY_KEY` is configured, otherwise public OpenStreetMap/Overpass.
Choose Tempe, Downtown Phoenix or the Phoenix/Tempe metro, a 2-30 km radius,
and up to 120 returned venues. Browse places makes no LLM calls and displays
names, addresses, listed hours, source links and retrieval time. Provider coverage
and limits mean this is not an exhaustive list of every business.
Live failures never silently select fixtures. Public endpoints can be unavailable;
configure a Geoapify key in the ignored `.env` and restart the UI server to use it.
Mock planning requires Fixture catalog. Live planning selects up to eight venues
for website enrichment; missing facts remain unknown and may prevent a valid plan.
Use `--live-discovery` with the CLI for the same source mode.

```bash
python run_ui.py --port 8765
```

Open http://127.0.0.1:8765 to edit the request, budget, party size, time,
atmosphere, walking limit and 1-4 ordered stops. Choose Real LLM to use the
configured server-side model, or Mock for a deterministic no-cost integration run.
The initial view displays the saved Bedrock run when available, explicitly labeled
as saved. New results expose itinerary, venue map, constraint checks, node activity
and downloadable JSON. Fixture mode uses offline annotations; live mode retrieves
provider listings and selected website evidence. Walking connections remain estimated;
the UI does not verify current availability or group capacity.

The server binds only to localhost, validates inputs, accepts one run at a time,
rejects foreign browser origins, and never serves `.env` or includes keys in its
configuration endpoint. Icons, fonts, Leaflet and OpenStreetMap tiles need internet
access. Test the UI boundary with `python -m unittest eval.test_ui -v`.

### AWS Bedrock Haiku

The local `.env` is ignored by Git. Set `LLM_PROVIDER=bedrock_converse`,
`LLM_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0`, and `AWS_REGION` to
your enabled region (`us-east-2` is verified here; the template defaults to `us-east-1`). Fill either
`AWS_BEARER_TOKEN_BEDROCK` for a Bedrock API key, or `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` for AWS IAM credentials. Temporary credentials also
require `AWS_SESSION_TOKEN`. Do not put credentials in chat or commit them.

```bash
python scripts/check_bedrock.py
python scripts/check_bedrock.py --invoke
python run_multi_agent.py --scenario examples/test1.json --max-attempts 2 --output artifacts/bedrock_flow.json
```

The first command only checks presence; `--invoke` sends one small request.
The graph then makes multiple real LLM calls for enrichment and planning.
Confirm credit eligibility and model access before invoking; credits do not
remove rate limits or guarantee that usage cannot incur charges. Venue data
remains offline unless explicitly enabled; a real LLM is independent of data mode.

The Phase-0 code below remains unchanged. The new prototype is a LangGraph workflow
with Discovery, Enrichment, Weather, Planner, Transit, and deterministic Critic nodes.
Only enrichment and planning invoke an LLM; specialist tool nodes are not independent
LLM agents. The critic can reject a proposal and request a bounded re-plan.

```bash
pip install -r requirements-milestone2.txt
python -m unittest eval.test_itinerary eval.test_multi_agent -v
python run_multi_agent.py --mock --scenario examples/test1.json
python -m eval.evaluate_multi --mock --repeats 3
python scripts/draft_milestone2.py
```

`--mock` performs deterministic integration tests, NOT LLM benchmarking. Without
`--mock`, configure an LLM provider as described below. `--live-web` fetches approved
bundled venue URLs; `--live-discovery` also permits HTTPS public websites linked by
the selected provider. Redirects are blocked; destinations are checked for private IPs,
responses are size-bounded, and requests have timeouts.
The prototype's `web_search` is only an official-URL lookup in the bundled catalog,
not a general search-engine integration. Offline page text is synthetic annotated
fixture content correlated with evaluation labels; it is not an independently captured
website dataset or evidence of current venue availability.

Scenario constraints may include `stop_types`, such as `["dinner", "dessert", "bar"]`.
The current prototype supports 1-4 explicitly requested stops. Legacy scenarios default
to dinner plus one after-stop. Each stop is scheduled using `stop_interval_hours`
(default 2); actual visit duration, weekday-specific opening times, reservations,
party capacity, and tax/tip are not yet modeled. All stops must satisfy a vegan request.
The pilot uses straight-line walking checks; unverified transit samples or estimates
cannot satisfy the verifier's transit constraint.

Results and node traces are saved in `artifacts/`. The pilot compares the graph with
two deterministic policies in mock mode, or greedy and single-call references in LLM
mode. The actual Phase-0 ReAct comparison remains a separate run. The two pilot datasets
are small authored scenario collections sharing one venue catalog, not public benchmarks.
No personal history is stored; evidence caching is in-memory and scoped to a runner.
Follow-up stakeholder approval, paired real-model evaluations, independent venue annotations,
human ratings, broader transit coverage, and alternative itineraries remain pending.

A tool-using AI agent that plans a two-stop night out (dinner, then one spot after) in the
Tempe / greater Phoenix area from a request in plain English. It respects real rules: budget per
person, dietary needs (vegan), open hours, and walkability.

This repo is the Phase-0 runnable baseline for a CSE 598 (Agentic AI) capstone. It is kept minimal
on purpose (one tool-using agent), so the full multi-agent project can measurably improve over it
(see [Roadmap](#roadmap)).

> Cost and keys: every data source is free and needs no credit card. The only paid part is the LLM,
> and even that has free, no-card options (Gemini Flash free tier, or local Ollama).

## What it does (the agent loop)

```
request -> Agent
             |- search_venues  (Geoapify / bundled)         candidate dinner + after-spots
             |- walk_route      (Geoapify / haversine)       is the hop walkable?
             |- transit         (Valley Metro / Transitland) or one short transit hop?
             |- weather         (Open-Meteo)                 patio vs indoor, conditions
           -> recommends a 2-stop plan -> objective constraint check (score)
```

## APIs used (all free, no credit card)

| Capability | Source | Free? | Card? |
|---|---|---|---|
| Venue discovery + dietary filter + walking routes | [Geoapify](https://www.geoapify.com/) | yes, 3,000/day | none |
| Public transit (bus/rail/streetcar) | [Valley Metro GTFS](https://www.phoenixopendata.com/) + [Transitland](https://www.transit.land/) | yes | none |
| Weather | [Open-Meteo](https://open-meteo.com/) | yes | none |
| LLM (default) | OpenAI | paid | yes |
| LLM (free option) | Google Gemini Flash free tier, or Ollama (local) | yes | none |

The baseline runs fully offline using bundled real Tempe data in `data/`, so no data-API keys are
needed to reproduce it. You only need one LLM provider. The `--live` flag switches the tools to the
real APIs.

### Scope: why Phoenix (for now)
The project is scoped to greater Phoenix because the free, no-card transit data (Valley Metro GTFS)
is regional. The venue and weather sources (Geoapify, Open-Meteo) are global, so the approach can
extend to any city by dropping in that city's GTFS feed, or by using Google Directions/Routes
transit (which covers any city but needs a billing account / credit card).

## Legacy Baseline Setup

For the current browser UI, use the Quick Start above. This section describes
the original Phase-0 baseline; its fixed two-stop prompt, older model examples
and dependency pins should not be confused with the current prototype.

```powershell
python -m venv .venv-baseline
.\.venv-baseline\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set exactly one LLM provider in `.env`:

| Provider | `.env` settings | Notes |
|---|---|---|
| OpenAI (default) | `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`, `OPENAI_API_KEY=...` | paid, best quality |
| Anthropic | `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-3-5-haiku-latest`, `ANTHROPIC_API_KEY=...` | paid |
| Gemini Flash | `LLM_PROVIDER=google_genai`, `LLM_MODEL=gemini-2.0-flash`, `GOOGLE_API_KEY=...` | free tier, no card ([get key](https://aistudio.google.com/apikey)) |
| Ollama (local) | `LLM_PROVIDER=ollama`, `LLM_MODEL=llama3.1` | free, no card; run `ollama pull llama3.1` first |

Provider selection lives in [`src/llm.py`](src/llm.py) via LangChain's `init_chat_model`, so adding
another supported provider is just an env change.

Data-source keys are only needed for `--live`: set `GEOAPIFY_KEY` and `TRANSITLAND_KEY` (both free,
no card).

## Run

```bash
# Offline (bundled data, recommended for reproducing, no data keys needed):
python run_baseline.py --scenario examples/test1.json

# Live (calls the real free APIs, needs GEOAPIFY_KEY + TRANSITLAND_KEY):
python run_baseline.py --scenario examples/test1.json --live
```

- Input: a scenario JSON in `examples/` (request text + the hard rules). Two are provided:
  `examples/test1.json` and `examples/test2.json`.
- Output: printed to the console and saved to `examples/output_<name>.txt`.

## Evaluation

```bash
python eval/evaluate_batch.py     # runs all scenarios in eval/scenarios.json and prints scores
```

The scorer (`eval/evaluate.py`) checks each plan against ground-truth venue data and reports a 0 to 1
constraint-satisfaction score over budget, vegan, open-at-time, and walkable. This is the objective
metric the full system is meant to improve.

## Test case and expected output

Input (`examples/test1.json`): "Plan a night out for 4 near ASU Tempe Friday ~7pm, ~$40/person,
chill and walkable, one of us is vegan. Dinner + one spot after."

Expected: the agent finds a vegan-friendly, walkable, in-budget plan (for example
Pita Jungle then The Gelato Spot) and prints a constraint check. A valid plan scores 1.0. The exact
saved output is in `examples/output_test1.txt` (and `examples/output_test2.txt` for the second test).

## Regenerate the bundled data (optional)

```bash
TRANSITLAND_KEY=... python scripts/cache_samples.py   # refresh the weather + transit samples
```

## Known limitations

- The offline data in `data/` is a small curated snapshot of Tempe venues, not the whole city.
- `--live` needs the free `GEOAPIFY_KEY` and `TRANSITLAND_KEY` to be set.
- LLM output is not deterministic, so the exact plan can vary between runs.
- The free structured data has no price and lists opening hours only about 20% of the time, so the
  baseline estimates budget and mood rather than verifying them. Recovering these is a Phase-2
  feature (reading venue websites).
- Tested with Python 3.13 and the pinned versions in `requirements.txt`.

## Roadmap (how the full project beats this baseline)

| | Baseline (this repo) | Full project (Phases 2-4) |
|---|---|---|
| Agents | one ReAct agent | multi-agent (Discovery, Enrichment, Transit, Weather, Critic) on LangGraph |
| Price / hours / mood | not in free data, estimated | web-fetch enrichment reads each venue's own page |
| Verification | none | a Critic verifies the plan and asks for a re-plan |
| Metric | lower constraint-satisfaction | higher constraint-satisfaction |

## Attribution
Venue data (c) OpenStreetMap contributors / Geoapify (ODbL). Transit data (c) Valley Metro
(City of Phoenix Open Data) via Transitland. Weather by Open-Meteo. Keys are read from environment
variables and are never committed.
