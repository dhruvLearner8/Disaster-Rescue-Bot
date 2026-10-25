We are building an offline AI assistant for phones that helps people in the US and
Canada during disasters. Today's disaster: {disaster}. Write messages that real people
would type into it while they are living through this disaster. Write only the person's
message, never an answer.

How people write:
- Short and to the point. They start with the problem, with no greeting.
- They are scared or at least tense, typing fast on a phone, so they make spelling
  mistakes, skip punctuation and use lowercase or ALL CAPS. Most messages have at least
  one typo. The kinds of typos, shown with everyday words (make your own typos on
  the words in your message, don't reuse these):
  - missing letters: tomorow, probly, finaly
  - swapped or doubled letters: becuase, freind, alll
  - shortcuts: pls, u, rn, ppl, w (for with)
  - missing spaces or wrong autocorrect: alot, were (for we're), there (for their)
- Each message starts with different words and uses different slang. Do not repeat an
  opening or a slang word across messages.

What people ask:
- A real person with a specific problem right now and only a few facts. They ask what
  to do, whether something is safe, or whether they can do something ("can i...",
  "is it ok to...", "should we...").
- Sometimes they believe something wrong that many people really believe in this
  disaster, or they hope for an easy way out. Keep that wrong belief in the message.
- They don't mention every detail of their situation. The scenario below is
  background: only mention a detail when it matters to their question. Never name
  their emotion directly ("im in shock", "im panicking"). Show it in how they write.

What the phases mean for {disaster}:
- before: {phase_before}
- during: {phase_during}
- after: {phase_after}

Urgency, judged on the real danger and not on how scared they sound:
critical = life at risk within minutes, high = serious danger if they choose wrong,
medium = real risk but time to think, low = planning or general questions.

Scenario:
- disaster: {disaster}
- phase: {phase}
- where: {where}
- who is with them: {who}
- complication: {complication}
- emotional state: {state}

Write {n} different messages for this scenario, each a different situation, with
these lengths:
{lengths}

Reply with JSON only, in this shape:
{{"messages": [{{"urgency": "critical", "question": "..."}}]}}
