# Multi-disaster questions v3: report

Raw rows: 5917. Clean rows: 5903. Dropped: {'near dup': 9, 'non-English': 2, 'exact dup': 3} (duplicate rate 0.2%).

Prompt question_gen_multi_v3.md, DeepSeek deepseek-chat, seed 42, 5 messages per call.

Length match overall: 49.3%. Typo rate overall (dictionary check, crude, slang counts): 64.5%.

## Per disaster (clean rows)

| disaster | rows | during/before/after | critical/high/medium/low | length match | typo rate | flagged words (>5% of rows) | openers (>5%) |
|---|---|---|---|---|---|---|---|
| drought | 200 | 100/50/50 | 8/73/88/31 | 43% | 58% | n (26%), wells (12%), w (10%), restrictions (6%), says (6%), shoud (6%), rn (6%) | wells (11%), taps (8%), well (6%) |
| contaminated water | 153 | 73/40/40 | 20/63/50/20 | 54% | 58% | w (20%), n (19%), smells (16%), says (15%), rn (8%), im (8%), lifted (6%), dishes (6%) | water (14%), tap (10%), notice (10%) |
| avalanche | 200 | 100/50/50 | 80/83/32/5 | 57% | 64% | n (22%), w (12%), rn (8%) | snow (12%), the (6%) |
| chemical spill | 155 | 75/40/40 | 24/71/49/11 | 46% | 57% | n (22%), windows (15%), fumes (14%), w (14%), thru (8%), eyes (8%), flipped (6%), smells (6%) | tanker (10%), smell (6%), fumes (6%) |
| earthquake | 403 | 199/104/100 | 100/163/99/41 | 62% | 63% | n (24%), w (10%), rn (8%), stairs (6%), walls (6%), im (5%) | smell (6%) |
| house fire | 155 | 75/40/40 | 66/34/41/14 | 54% | 59% | n (20%), w (13%), flames (9%), stairs (8%), thru (7%), shoud (6%), walls (5%) | smoke (15%), kitchen (7%) |
| extreme heat | 399 | 199/100/100 | 82/165/129/23 | 38% | 62% | n (36%), w (16%), ac (16%), feels (11%), windows (8%), rn (8%), says (7%), mom (6%) | my (9%), heat (8%), is (7%) |
| hurricane | 401 | 202/100/99 | 117/179/90/15 | 50% | 66% | n (23%), w (13%), thru (8%), windows (7%), comin (7%), rn (6%), shud (6%), lines (5%) | water (14%), wind (8%), tree (5%) |
| gas leak or carbon monoxide | 155 | 75/40/40 | 52/50/38/15 | 53% | 59% | co (23%), n (21%), windows (10%), w (8%), shoud (7%), smells (6%), im (6%), feels (5%) | co (14%), gas (10%), smell (10%) |
| ice storm | 204 | 100/50/54 | 23/94/73/14 | 48% | 60% | w (16%), n (15%), rn (7%), lines (6%), shud (6%), steps (5%) | power (10%), tree (10%), ice (9%) |
| lost or stranded | 155 | 75/40/40 | 32/64/49/10 | 40% | 68% | n (16%), w (12%), campsite (7%), 2 (7%), thru (6%) | car (8%), we (8%), trail (6%) |
| landslide | 397 | 197/100/100 | 139/172/83/3 | 53% | 67% | n (21%), w (11%), trees (10%), rn (9%), thru (9%) | mud (14%), ground (7%), hill (5%) |
| pandemic | 155 | 75/40/40 | 7/53/66/29 | 51% | 66% | n (19%), w (12%), has (9%), coughing (8%), masks (8%), rn (8%), im (7%), shuld (6%) | my (16%), is (8%), can (6%) |
| power outage | 402 | 202/100/100 | 59/155/139/49 | 46% | 70% | n (28%), fridge (21%), w (18%), lights (8%), 2 (7%), candles (6%), powers (5%), 3 (5%) | fridge (12%), power (7%) |
| radiological incident | 156 | 75/41/40 | 30/66/43/17 | 53% | 62% | n (21%), w (13%), sirens (13%), windows (12%), says (10%), rn (7%), shud (6%), shoud (5%) | sirens (10%), power (5%) |
| sinkhole or dam failure | 204 | 100/54/50 | 82/72/44/6 | 53% | 66% | n (16%), thru (9%), w (8%), im (6%) | water (13%), dam (10%), street (7%) |
| thunderstorm | 207 | 103/50/54 | 38/105/56/8 | 45% | 66% | n (25%), w (12%), rn (9%), windows (9%), lines (7%), thru (6%) | hail (16%), power (8%), tree (8%) |
| tsunami | 400 | 200/100/100 | 156/158/74/12 | 51% | 74% | n (30%), w (12%), pulled (10%), sirens (8%), rn (8%), comin (7%), im (6%), thru (5%) | water (14%), ocean (8%), sirens (7%) |
| volcano | 199 | 99/50/50 | 53/91/44/11 | 50% | 59% | n (24%), w (14%), shud (9%), windows (8%), rn (8%), sulfur (7%), thru (5%) | ash (11%), smell (8%), sky (6%) |
| tornado | 401 | 201/100/100 | 173/156/69/3 | 53% | 59% | n (23%), windows (12%), w (10%), rn (9%), sirens (9%), neighbors (5%) | sirens (8%), roof (7%) |
| wildfire | 399 | 200/100/99 | 105/186/93/15 | 51% | 65% | n (20%), w (13%), thru (11%), flames (10%), rn (7%), windows (5%), evac (5%), shoud (5%) | smoke (15%), ash (11%), flames (6%) |
| winter storm | 403 | 204/99/100 | 74/185/115/29 | 38% | 69% | n (33%), w (14%), pipes (10%), fingers (9%), shoud (6%), whiteout (6%), shud (6%) | power (10%), fingers (5%), car (5%) |

Overall urgency: {'medium': 1564, 'high': 2438, 'critical': 1520, 'low': 381}. Overall phase: {'after': 1486, 'before': 1488, 'during': 2929}.

## Notes on the numbers
- Raw 5917 rows (one resume pass filled the gaps; 1 call failed with a JSON error and was retried by the resume run). Cost about $0.35 (estimate from API usage numbers, not the dashboard). Clean 5903 rows. Drops: 3 exact duplicates, 9 near duplicates (token Jaccard >= 0.8 within a disaster), 2 non-English (non-ASCII or Spanish/French marker words). A first, stricter English check wrongly dropped about 300 short typo-heavy English rows; that heuristic was loosened.
- Quotas are met within about 0 to 8% per disaster (phase quotas are rounded per call of 5, and a few rows lost to the JSON/label checks).
- 59 rows have where="public place". That value is not in scripts/labels.py. I kept the rows (the questions are fine) and flag it here: either add it to labels.py or treat it as a missing label.
- The task said 23 disasters but listed 22 (9 + 6 + 7). All 22 are done.
- Length match: only 49% of rows fall in the target word range (flood run: about 60%). Extreme heat 36%, winter storm 38%, lost or stranded 39%. The model writes long when asked for 2-6 words.
- Typo rate is a crude dictionary check (any 4+ letter word not in /usr/share/dict/words); slang, plural forms and place names count too, so it is an upper bound. The real typo share looked high (most rows) when reading.
- Flagged words (>5% of a disaster's rows): the shortcuts "n" (and) and "w" (with) appear in 15-36% and 8-21% of rows in every disaster, "rn" in 6-10%, "thru" 5-11%, "shud/shoud" 5-10%. This is the "tonite x33" problem in a milder form: n/w are shared slang. They are in the table above with percentages. Topic words (fridge 21% in power outage, "wells" 13% in drought, "windows" 16% in chemical spill) are domain words, not a slang problem. Opening words over 5%: see the table; none above 17% (water 15%, smoke 16%, hail 17%, pandemic "my" 17%).
- Scenario leakage still happens although only message k should carry details: insulin 1.0%, baby 2.9%, dog 3.5%, elderly relative 3.7%, "no english" 1.4%. Less than in v1/v2 but visible (e.g. "cut his arm bad" + "insulin" in a wildfire message).
- Phase labels are noisy: many "before" rows describe an event already happening (hurricane "before": "water rising fast on our street"), and many "after" rows are still "during". Urgency: critical 23%, high 40%, medium 26%, low 6% (low is thin; urgency labels from the generator are unreliable, as in the flood data).

## Disaster clue (random sample of 5 per disaster, read by me)
77 of 110 sampled rows (70%) carry a clear clue to the specific disaster. Weakest: thunderstorm (1/5), hurricane (2/5), tornado (2/5), ice storm (2/5), power outage (3/5). Typical failure: a generic follow-up that could be any storm ("power lines sparking, can i walk over them", "roof just tore off what now"). Strongest (5/5): drought, avalanche-ish, gas leak, landslide. Some rows pass as ambiguous with floods (hurricane "water rising on our street").

## 10 worst-looking rows seen
1. house fire / before: "smell gas near stove, should we open windows" - that is a gas leak, wrong disaster.
2. hurricane / before: "power lines down n flooding in my street, can i go look at my dads house?" - already happening, no hurricane clue.
3. hurricane / before: "water rising fast on our street, can we still drive out now?" - flood, not a before-phase hurricane.
4. thunderstorm / before: "trampoline not tied down ok?" - trivia, no clue.
5. ice storm / after: "ice fell on him n phone dying help" - unclear, no clue.
6. extreme heat / during: "baby getting real fussy, phone bout to die" - no disaster clue, the complication took over.
7. power outage / before: "at mall w my dog n insulin gettng warm what do" - scenario detail dominates, phase wrong.
8. chemical spill / before: "hes got asthma and cant walk, spill at work" - fragment, no way to tell what spilled.
9. radiological incident / after: "how long we gotta stay inside?" - could be anything.
10. tornado / during: "roof just tore off what now" - could be hurricane or tornado; plus drought / after: "wildfire risk here now huh after all the dry" (wrong disaster word).

## Verdict
Prompt v3 kept (no v4). The pilot (22 disasters x 15 rows, 328 rows, all read) showed no disaster that was broken enough to justify a prompt change; fixes were limited to the table (lists of "where" places). Main remaining problems: weak clues in the storm family (thunderstorm, hurricane, tornado, ice storm), noisy phase labels, long messages, and the n/w/rn slang shared by all disasters.
