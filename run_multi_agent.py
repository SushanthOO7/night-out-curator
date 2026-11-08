"""Run the hybrid graph; --mock is explicitly not a real LLM evaluation."""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from dotenv import load_dotenv

load_dotenv()
from multi_agent import MultiAgentRunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="examples/test1.json")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--live-web", action="store_true")
    parser.add_argument("--live-discovery", action="store_true")
    parser.add_argument("--venue-provider", choices=["geoapify", "google"])
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument("--output", default="artifacts/demo.json")
    args = parser.parse_args()
    scenario = json.loads((ROOT / args.scenario).read_text())
    if args.venue_provider:
        scenario["constraints"]["venue_provider"] = args.venue_provider
    result = MultiAgentRunner(args.mock, args.live_web, args.max_attempts, args.live_discovery).run(scenario)
    if result.get("restricted_content"):
        result = {"status": result["status"], "metrics": result["metrics"],
                  "checks": result["report"]["checks"], "note": "Raw Google Maps content omitted from saved output."}
    print(json.dumps(result, indent=2))
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()