# Question generation prompt — v2

Changes from v1:
- Added "in the water" to the Where list (v1 output used it even though it wasn't listed).
- The labels must now come from the fixed lists, using the exact spelling.
- Added an urgency label, because phase alone doesn't show danger (e.g. smelling gas
  "after" a flood is critical).
- Fixed the state labels: the list said "calm and practical" but the JSON said "calm".

## Context

We are building an AI assistant that runs fully offline on a phone, for people in
the US and Canada who are dealing with a flood. There is no internet, so the app is
the only help the person can reach in that moment besides calling 911.

To train and test it, we need realistic messages that real people would type into
the app. Your job is to write those messages. You are NOT writing answers.

## The three phases

Every message belongs to one phase:

1. **before**: the flood is coming or nearby, but the person is not in the water or
   trapped yet. They are deciding what to do. Examples: a warning was issued,
   neighbours are evacuating, water is on the road ahead, the river is rising.
2. **during**: the person is in danger right now. Examples: trapped in a car, a house
   surrounded by water, stranded on a small patch of land, in the water, water
   coming inside.
3. **after**: the flood has peaked and the water is calm or going down. The danger is
   less obvious. Examples: going back home, electricity and gas, walking through
   standing water, animals and snakes, contaminated water, damaged buildings, mould.

## Make them varied

Vary these across the batch. Don't let two messages share the same combination.
Every label must be copied exactly from these lists. Never invent a new label.

- **where**: car, house, apartment, basement, rooftop, small patch of land, in the water,
  campsite, walking outside, workplace, school
- **who**: alone, kids, baby, elderly parent, pet, someone injured,
  someone who can't swim, strangers
- **complication**: none, power out, phone battery low, no car, night time, injury,
  medical condition, doesn't speak English well
- **state**: calm, worried, panicking, shock

## Urgency

Also label how dangerous the situation really is. This is separate from the phase and
separate from how the person feels: a calm person can be in critical danger.

- **critical**: life at risk within minutes (car in moving water, swept away, gas smell)
- **high**: serious danger soon if they make the wrong choice (water entering the house,
  thinking about driving through water)
- **medium**: real risk, but there is time to think (evacuation alert, returning home)
- **low**: planning or general questions (what to pack, cleaning up mould)

## Make them sound real

- People type on a phone, with one hand, under stress. Most messages are short.
- Use typos, missing punctuation, lowercase or ALL CAPS, and slang where it fits.
  Not every message, but a good share of them.
- Some messages contain a wrong belief ("the water's calm so my car can make it").
  Those are valuable. Keep the wrong belief in the message.
- Some are vague and leave out key details, the way real people do.
- Don't make it dramatic like a movie. Real fear is usually blunt and messy.
- Never write an answer or advice, only the user's message.

## Output

Return one JSON object per line (JSONL), with no other text:

{"phase": "before|during|after", "urgency": "critical|high|medium|low", "where": "...", "who": "...", "complication": "...", "state": "calm|worried|panicking|shock", "question": "..."}

## Task

Write {n} messages for the **{phase}** phase.
