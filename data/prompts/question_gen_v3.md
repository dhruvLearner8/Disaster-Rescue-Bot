# Question generation prompt — v3

Changes from v2:
- The script now picks the scenario (phase, where, who, complication, state) at random
  for each call and fills it in below, so the spread across scenarios is even. v2 let
  the model choose, and it drifted to easy cases (40% "alone", 2 of 30 "shock").
- Each call writes {n} messages for that one scenario, each in a different writing style.
- The model only labels urgency. The script records the other labels itself.

## Context

We are building an AI assistant that runs fully offline on a phone, for people in
the US and Canada who are dealing with a flood. There is no internet, so the app is
the only help the person can reach in that moment besides calling 911.

To train and test it, we need realistic messages that real people would type into
the app. Your job is to write those messages. You are NOT writing answers.

## The three phases

1. **before**: the flood is coming or nearby, but the person is not in the water or
   trapped yet. They are deciding what to do.
2. **during**: the person is in danger right now.
3. **after**: the flood has peaked and the water is calm or going down. The danger is
   less obvious: electricity, gas, contaminated water, animals, damaged buildings, mould.

## Make them sound real

- People type on a phone, with one hand, under stress. Most messages are short.
- Use typos, missing punctuation, lowercase or ALL CAPS, and slang where it fits.
- Some messages contain a wrong belief ("the water's calm so my car can make it").
  Those are valuable. Keep the wrong belief in the message.
- Some are vague and leave out key details, the way real people do.
- Don't make it dramatic like a movie. Real fear is usually blunt and messy.
- Never write an answer or advice, only the user's message.
- The scenario details below are a starting point. A message doesn't have to mention
  every detail, just as a real person wouldn't.

## Urgency

Label how dangerous each situation really is. This is separate from the phase and
from how the person feels: a calm person can be in critical danger.

- **critical**: life at risk within minutes (car in moving water, swept away, gas smell)
- **high**: serious danger soon if they make the wrong choice
- **medium**: real risk, but there is time to think
- **low**: planning or general questions

## This scenario

- phase: {phase}
- where: {where}
- who is with them: {who}
- complication: {complication}
- emotional state: {state}

Write {n} different messages for this scenario. Make each one a different situation
and a different writing style.
