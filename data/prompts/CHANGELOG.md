# Prompt changelog

Prompt files contain only what the model reads. Why each version changed goes here.
(v2–v4 also have their changelog inside the file. That text was sent to the model too,
which is why it moved here from v5 on.)

## question_gen_v7
- Typo examples now use everyday words that don't appear in flood messages. In v6 the
  model copied the flood-word examples: "basment" 9 times in 30 messages, "hlp" 3 times.
- The scenario is background: mention a detail only when it matters. In v6 all three
  messages in one call said "no car", even where it didn't matter.
- Never name the emotion directly (v6 wrote "im in shock.").

## question_gen_v6
- Typo examples added. v5 had almost no real spelling mistakes, only lowercase,
  "thru" and broken English from the non-English-speaker scenario.
- (Script) "someone who can't swim" is no longer picked for the after phase. In v5 it
  produced forced details like "my wife cant swim and has diabetes, insulin...".

## question_gen_v5
- Much shorter prompt: short, to the point, a bit scared, spelling mistakes.
- The script picks a target length for each message (very short / short / medium).
  In the v4 test only 4 of 15 messages were under 25 words and none were 2–6 words:
  the model didn't follow "most are short, some very short".
- Changelog moved out of the prompt file.

## question_gen_v4
- Length rules and no greetings (v3: 42 words on average, 4 of 15 started with "Hi").

## question_gen_v3
- The script picks the scenario at random for each call (v2 drifted to easy cases).

## question_gen_v2
- Fixed label lists, "in the water" added, urgency label added.

## question_gen_v1
- First version.

## question_gen_multi_v2 (DeepSeek, multi-disaster)
- v1 test (20 questions, 4 disasters): the scenario took over. "injury" made 3 of 5 wildfire
  messages about a broken ankle, "phone battery low" made heat messages about the phone,
  "alone" was filler. Fixed: scenario is hidden background, at most one detail per batch.
- v1 messages like "no car where do we go" don't say which disaster. The app has no disaster
  tag, so 4 of 5 messages must carry a clue in the words (see, hear, smell, feel).
- Phase definitions made stricter ("before" = nothing is happening yet).

## question_gen_multi_v3 (DeepSeek, multi-disaster)
- v2 fixed the "which disaster" clue, but "injury" still appeared in 3 of 5 wildfire messages
  ("at most one" was ignored). Now the script picks one message number k and the extra
  details (where, who, complication) apply to message k only. The other rows store None.

## question_gen_multi_v4 (DeepSeek, multi-disaster)
- v3 full run: only about 70% of sampled rows carried a clue to the specific disaster; weakest were the
  storm family (thunderstorm 1/5, hurricane 2/5, tornado 2/5, ice storm 2/5). Typical failure: a generic
  message that fits any storm ("power lines down across the street, is it safe to walk my dog?").
- Changed one thing: every message (not 4 of 5) needs a clue that would not fit another disaster, with a
  self-check and a different clue per message.
- Result (blind check, 80 v3 rows vs 80 v4 rows, thunderstorm/hurricane/tornado/ice storm): clear disaster clue
  50% (v3) vs 55% (v4), which is noise. v4 did NOT fix it, so v3 stays the prompt for the full dataset.
  Cause: "after" messages are naturally generic (22% have a clue, vs 74% "before" and 60% "during"):
  "downed line in the yard, safe to walk?" is the same question after any storm. Not a prompt problem.
