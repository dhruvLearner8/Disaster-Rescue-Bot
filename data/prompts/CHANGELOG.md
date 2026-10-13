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
