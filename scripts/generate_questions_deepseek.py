"""Generate synthetic user questions for many disasters with the DeepSeek API.

Code decides the mix (disaster, phase, scenario, lengths); the model only writes messages.
Resumable: re-running counts existing rows per disaster/phase and generates only the missing ones.
Needs DEEPSEEK_API_KEY in .env.

    uv run python scripts/generate_questions_deepseek.py --prompt multi_v3 --per-disaster 10 \
        --out data/synthetic/multi_pilot/pilot_v3.jsonl            # pilot
    uv run python scripts/generate_questions_deepseek.py --prompt multi_v3 --max-usd 3   # full run
"""

import argparse
import json
import math
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from dotenv import load_dotenv

from labels import ALLOWED

URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
PRICE = (0.28, 0.42)  # USD per 1M tokens (input, output). Estimate: check your DeepSeek dashboard.
LENGTHS = {"2-6 words": 0.35, "7-15 words": 0.45, "16-30 words": 0.20}
PHASES = ["during", "before", "during", "after"]  # 50% during, 25% before, 25% after
WATER_DISASTERS = {"tsunami", "hurricane", "sinkhole or dam failure"}  # "can't swim" only makes sense here

# (quota, before, during, after, where). "where" only lists places that make sense for the disaster.
_TABLE = {
    "earthquake": (400, "they live in a quake zone and want to prepare",
                   "the ground is shaking right now, or it just stopped and aftershocks may come",
                   "the shaking is over: damage, gas, fire, blocked exits, aftershocks, no power or water",
                   ["house", "apartment", "car", "workplace", "school", "walking outside", "public place"]),
    "wildfire": (400, "a fire is burning in the region, smoke is in the air or an evacuation warning is out",
                 "fire or heavy smoke is close, or they are leaving or trapped",
                 "the fire has passed: unsafe air, ash, damaged home, hot spots, returning home",
                 ["house", "apartment", "car", "campsite", "workplace", "school", "walking outside"]),
    "extreme heat": (400, "a heat wave or heat dome is forecast and they are preparing",
                     "it is dangerously hot right now and someone may be getting sick",
                     "the worst heat is over but people may still be unwell, or the power or water is out",
                     ["house", "apartment", "car", "workplace", "school", "walking outside", "campsite"]),
    "winter storm": (400, "a blizzard or deep-freeze warning is out and they are preparing",
                     "a blizzard or extreme cold is happening now: whiteout, drifting snow, frostbite or hypothermia risk",
                     "the storm has passed but roads are blocked, pipes froze, heat is out or someone is cold-injured",
                     ["house", "apartment", "car", "workplace", "school", "walking outside"]),
    "tornado": (400, "a tornado watch or warning is out and they are choosing where to go",
                "a tornado is close or hitting right now",
                "the tornado has passed: damaged building, gas, power lines, injuries, debris",
                ["house", "apartment", "basement", "car", "workplace", "school", "walking outside", "public place"]),
    "hurricane": (400, "a hurricane is forecast and they decide whether to evacuate or how to prepare",
                  "the hurricane is hitting: high wind, storm surge, rising water, flying debris, the eye passing",
                  "the hurricane has passed: flooding, downed lines, no power, damaged home, unsafe water",
                  ["house", "apartment", "basement", "car", "rooftop", "workplace", "school", "in the water"]),
    "power outage": (400, "a long outage is forecast or has just started and they want to prepare",
                     "the power has been out for hours or days: food, heating or cooling, medical devices, generators, candles",
                     "power is coming back or just returned: spoiled food, surges, damaged appliances, still cold or hot",
                     ["house", "apartment", "basement", "car", "workplace", "public place"]),
    "landslide": (400, "heavy rain or a slope looks unstable and they wonder whether to leave",
                  "earth, mud or debris is moving or has just hit near them",
                  "the slide has stopped: blocked roads, broken utilities, more slides possible, injured people, returning home",
                  ["house", "apartment", "car", "workplace", "school", "walking outside", "campsite"]),
    "tsunami": (400, "they live on the coast and want to know the warning signs and the evacuation plan",
                "a tsunami warning is out, the sea is pulling back or a wave is arriving",
                "the waves have passed: flooded streets, debris, more waves possible, when to go back",
                ["house", "apartment", "car", "workplace", "school", "walking outside", "public place", "rooftop", "in the water"]),
    "ice storm": (200, "freezing rain is forecast and they are preparing",
                  "freezing rain is coating everything: ice on lines and trees, slippery roads, branches falling",
                  "the ice has stopped: downed lines, fallen trees, no power for days, icy roads and walkways",
                  ["house", "apartment", "car", "workplace", "school", "walking outside"]),
    "thunderstorm": (200, "a severe thunderstorm warning is out (lightning, hail, high wind) and they are deciding what to do",
                     "lightning, hail or damaging wind is happening right now",
                     "the storm has passed: fallen trees, downed lines, hail damage, flooded roads",
                     ["house", "apartment", "car", "campsite", "workplace", "school", "walking outside", "public place"]),
    "drought": (200, "a long dry spell or water restrictions are coming and they want to prepare",
                "water is very short now: dry taps, restrictions, wells running dry, livestock or garden, heat",
                "the drought is easing or the water is back: cloudy or unsafe water, wells to recheck, fire risk",
                ["house", "apartment", "workplace", "school", "campsite"]),
    "volcano": (200, "a volcano nearby is showing activity and an alert level has been raised",
                "an eruption is happening: ashfall, a dark plume, a loud boom, lahar or gas risk",
                "the eruption has calmed: ash on roofs and cars, unsafe air, closed roads, cleanup",
                ["house", "apartment", "car", "workplace", "school", "walking outside", "campsite"]),
    "avalanche": (200, "avalanche danger is high in the mountains and they are planning a trip or travelling through",
                  "an avalanche has just happened or they are caught in or crossing a risky slope",
                  "the avalanche is over: someone is buried, a rescue is needed, they are stranded or cold",
                  ["car", "campsite", "walking outside", "house"]),
    "sinkhole or dam failure": (200, "cracks, new holes or a dam warning appear and they worry about their area",
                                "ground is collapsing or a dam is breaking and a surge of water is coming right now",
                                "the collapse or surge is over: damage, undermined ground, unsafe building, returning home",
                                ["house", "apartment", "basement", "car", "workplace", "school", "walking outside", "in the water"]),
    "house fire": (150, "they want to prevent a fire, plan an escape route or check smoke alarms",
                   "there is fire or smoke in their home right now and they need to get out",
                   "the fire is out: smoke damage, is the structure safe, where to stay, what is safe to touch or eat",
                   ["house", "apartment", "basement", "workplace", "school"]),
    "gas leak or carbon monoxide": (150, "they want to prevent gas leaks or CO problems, buy detectors or check appliances",
                                    "they smell gas, a CO alarm is sounding or people feel dizzy or sick right now",
                                    "the gas or CO source was stopped: when to go back in, lingering symptoms, airing out, what to check",
                                    ["house", "apartment", "basement", "car", "workplace", "school"]),
    "chemical spill": (150, "they live near a plant, rail line or highway and want to prepare for a hazmat release",
                       "a chemical spill, tanker crash or toxic cloud is close and they smell fumes or see a plume",
                       "the release is over: contaminated clothes or skin, when to go home, cleaning, symptoms",
                       ["house", "apartment", "car", "workplace", "school", "walking outside", "public place"]),
    "radiological incident": (150, "they want to know how to prepare for a nuclear plant accident or radiation release",
                              "a radiation or nuclear emergency has been announced and they must shelter or leave now",
                              "the immediate danger has passed: decontamination, food and water safety, when to leave shelter",
                              ["house", "apartment", "basement", "car", "workplace", "school", "public place"]),
    "contaminated water": (150, "a boil-water or do-not-drink notice is possible and they want to prepare supplies",
                           "a boil-water, do-not-drink or do-not-use notice is in force and they need safe water now",
                           "the notice was lifted or the water is clearing: flushing taps, cleaning, symptoms, baby formula",
                           ["house", "apartment", "workplace", "school", "campsite"]),
    "pandemic": (150, "a new outbreak is spreading nearby and they want to prepare supplies and plans",
                 "an outbreak is in their area: someone at home is sick, isolation, masks, exposure, who to call",
                 "the outbreak is easing: recovery, lingering symptoms, when to return to work or school",
                 ["house", "apartment", "workplace", "school", "public place"]),
    "lost or stranded": (150, "they plan a hike, drive or winter trip and want to know what to pack and what to tell people",
                         "they are lost in the wilderness or stuck in a car in snow or on a remote road right now",
                         "they were found or reached shelter but are cold, hurt, dehydrated or still far from help",
                         ["car", "campsite", "walking outside"]),
}
DISASTERS = {n: dict(zip(("before", "during", "after", "where"), v[1:])) for n, v in _TABLE.items()}
TIER_COUNTS = {n: v[0] for n, v in _TABLE.items()}


def phase_quotas(total: int) -> dict:
    during, before = total // 2, total // 4
    return {"during": during, "before": before, "after": total - during - before}


def pick_scenario(rng: random.Random, disaster: str, phase: str) -> dict:
    d = DISASTERS[disaster]
    no_swim = phase == "after" or disaster not in WATER_DISASTERS
    people = [p for p in sorted(ALLOWED["who"]) if not (no_swim and p == "someone who can't swim")]
    return {
        "disaster": disaster, "phase": phase,
        "where": rng.choice(d["where"]), "who": rng.choice(people),
        "complication": rng.choice(sorted(ALLOWED["complication"])),
        "state": rng.choice(sorted(ALLOWED["state"])),
    }


def build_prompt(template: str, scenario: dict, n: int, lengths: list[str], k: int) -> str:
    d = DISASTERS[scenario["disaster"]]
    length_lines = "\n".join(f"{j}. {length}" for j, length in enumerate(lengths, 1))
    return template.format(n=n, k=k, lengths=length_lines, phase_before=d["before"],
                           phase_during=d["during"], phase_after=d["after"], **scenario)


def call_api(key: str, prompt: str) -> dict:
    """POST with retry/backoff on 429 and 5xx (and network errors)."""
    for attempt in range(5):
        try:
            r = httpx.post(URL, timeout=120, headers={"Authorization": f"Bearer {key}"},
                           json={"model": MODEL, "temperature": 1.2, "max_tokens": 2000,
                                 "response_format": {"type": "json_object"},
                                 "messages": [{"role": "user", "content": prompt}]})
            if r.status_code == 429 or r.status_code >= 500:
                raise httpx.HTTPStatusError("retryable", request=r.request, response=r)
            r.raise_for_status()
            return r.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            if attempt == 4 or (isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 429):
                raise
            time.sleep(2 ** attempt + random.random())
    raise RuntimeError("unreachable")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="e.g. multi_v3 (data/prompts/question_gen_multi_v3.md)")
    ap.add_argument("--out", default="data/synthetic/multi/questions_multi_v3.jsonl")
    ap.add_argument("--n", type=int, default=5, help="messages per call")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tier-counts", default=None,
                    help="JSON like '{\"earthquake\": 400}' (default: the built-in tiers)")
    ap.add_argument("--per-disaster", type=int, default=None, help="override: same quota for every disaster (pilot)")
    ap.add_argument("--disasters", default=None, help="comma list to restrict to")
    ap.add_argument("--max-usd", type=float, default=3.0, help="hard spending cap")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true", help="print the first prompt and the plan, no API call")
    args = ap.parse_args()
    args.workers = min(args.workers, 5)

    template = Path(f"data/prompts/question_gen_{args.prompt}.md").read_text()
    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    quotas = json.loads(args.tier_counts) if args.tier_counts else dict(TIER_COUNTS)
    if args.disasters:
        quotas = {d: quotas.get(d, TIER_COUNTS[d]) for d in args.disasters.split(",")}
    if args.per_disaster:
        quotas = {d: args.per_disaster for d in quotas}

    have = {}  # (disaster, phase) -> rows already in the file
    if out_file.exists():
        for line in out_file.read_text().splitlines():
            r = json.loads(line)
            have[(r["disaster"], r["phase"])] = have.get((r["disaster"], r["phase"]), 0) + 1

    jobs = []  # one job = one API call; the call index makes the seed (and so the scenario) reproducible
    for disaster, total in quotas.items():
        for phase, want in phase_quotas(total).items():
            done = have.get((disaster, phase), 0)
            for c in range(math.ceil(max(want - done, 0) / args.n)):
                jobs.append((disaster, phase, done // args.n + c))
    # interleave so a stop part-way still leaves every disaster covered
    jobs.sort(key=lambda j: (j[2], j[1], j[0]))
    print(f"{len(jobs)} calls planned, {sum(have.values())} rows already in {out_file}")

    load_dotenv()
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key and not args.dry_run:
        raise SystemExit("DEEPSEEK_API_KEY is not in .env")

    lock = threading.Lock()
    state = {"cost": 0.0, "written": 0, "fails": 0, "stop": False}

    def run(job):
        disaster, phase, idx = job
        if state["stop"]:
            return
        rng = random.Random(f"{args.seed}-{disaster}-{phase}-{idx}")
        scenario = pick_scenario(rng, disaster, phase)
        lengths = rng.choices(list(LENGTHS), weights=list(LENGTHS.values()), k=args.n)
        k = rng.randint(1, args.n)  # only message k gets where / who / complication
        prompt = build_prompt(template, scenario, args.n, lengths, k)
        if args.dry_run:
            print(prompt)
            state["stop"] = True
            return
        try:
            body = call_api(key, prompt)
            msgs = json.loads(body["choices"][0]["message"]["content"])["messages"]
            usage = body["usage"]
            rows = []
            for j, m in enumerate(msgs[:args.n]):
                if m.get("urgency") not in ALLOWED["urgency"] or not str(m.get("question", "")).strip():
                    continue
                row = dict(scenario)
                if j + 1 != k:
                    row.update(where=None, who=None, complication=None)
                rows.append({**row, "urgency": m["urgency"], "question": m["question"].strip(),
                             "target_length": lengths[j], "model": MODEL, "prompt": f"question_gen_{args.prompt}.md"})
        except Exception as e:  # noqa: BLE001 - count any failure toward the stop rule
            with lock:
                state["fails"] += 1
                print(f"FAIL {disaster}/{phase}: {type(e).__name__} {str(e)[:100]}")
                if state["fails"] >= 5:
                    state["stop"] = True
                    print("5 consecutive failures, stopping")
            return
        with lock:
            state["fails"] = 0
            state["cost"] += (usage["prompt_tokens"] * PRICE[0] + usage["completion_tokens"] * PRICE[1]) / 1e6
            with out_file.open("a") as f:
                f.writelines(json.dumps(r) + "\n" for r in rows)
            state["written"] += len(rows)
            if state["cost"] >= args.max_usd:
                state["stop"] = True
                print(f"spending cap ${args.max_usd} reached, stopping")

    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(run, jobs))
    print(f"wrote {state['written']} rows to {out_file}, cost about ${state['cost']:.4f} (estimate), fails={state['fails']}")


if __name__ == "__main__":
    main()
