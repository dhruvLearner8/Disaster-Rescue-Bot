We are building an offline AI assistant for phones that helps people in the US and
Canada during floods. Write messages that real people would type into it. Write only
the person's message, never an answer.

How people write:
- Short and to the point. They start with the problem, with no greeting.
- They are scared or at least tense, typing fast on a phone, so they make spelling
  mistakes, skip punctuation and use lowercase or ALL CAPS.
- Sometimes they believe something wrong ("water looks calm so we can drive thru").
  Keep that wrong belief in the message.
- They don't mention every detail of their situation.

Phases: "before" means the flood is coming and they're deciding what to do. "during"
means they're in danger right now. "after" means the water is calm or going down
(electricity, gas, dirty water, animals, damaged buildings).

Urgency, judged on the real danger and not on how scared they sound:
critical = life at risk within minutes, high = serious danger if they choose wrong,
medium = real risk but time to think, low = planning or general questions.

Scenario:
- phase: {phase}
- where: {where}
- who is with them: {who}
- complication: {complication}
- emotional state: {state}

Write {n} different messages for this scenario, each a different situation, with
these lengths:
{lengths}
