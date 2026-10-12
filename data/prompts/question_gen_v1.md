# Question generation prompt — v1

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

- **Where**: car, house, apartment, basement, rooftop, small patch of land, campsite,
  walking outside, workplace, school
- **Who is with them**: alone, kids, baby, elderly parent, pet, someone injured,
  someone who can't swim, strangers
- **Complications**: power out, phone battery low, no car, night time, injury,
  medical condition, doesn't speak English well
- **Emotional state**: calm and practical, worried, panicking, in shock

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

{"phase": "before|during|after", "where": "...", "who": "...", "complication": "... or none", "state": "calm|worried|panicking|shock", "question": "..."}

## Task

Write {n} messages for the **{phase}** phase.
