# Narration Reference

How to write a timestamped narration script that pairs with a `.cast` recording. The goal is a rehearsable companion document that lets you (or someone else) deliver the demo with consistent timing.

## Why narration matters

A 90-second terminal demo unaccompanied is fine for asynchronous viewing but loses 50 % of its value in a live talk. Narration:

- Forces you to pace the demo (instead of typing as fast as you can).
- Gives you a fallback if the demo fails live — read the script, skip the cast.
- Doubles as printed speaker notes.
- Makes the demo accessible to audience members watching from the back of the room or with hearing impairments.

## Script structure

```markdown
---
cast: demo.cast
title: <DEMO TITLE>
total_duration: 1:32
speaker: <NAME>
---

# Narration: <DEMO TITLE>

| Time   | Cast event             | Narration                                                             |
| ------ | ---------------------- | --------------------------------------------------------------------- |
| 00:00  | Title appears          | <One-sentence framing of what they're about to see>                   |
| 00:08  | First command runs     | <What the command does and why>                                       |
| 00:23  | Output appears         | <Highlight the line that matters>                                     |
| 00:41  | Second command runs    | <What changed since the last step>                                    |
| 01:05  | Result visible         | <The takeaway in one sentence>                                        |
| 01:22  | Final exit             | <Closing line, transition into the next slide>                        |
```

Pad the right column to ~70-80 chars; longer becomes hard to read on the lectern.

## Writing discipline

1. **Watch the cast once with a stopwatch.** Note the timestamps of every visible event you want to narrate.
2. **Write one cell per moment.** Resist the urge to merge "command runs + output appears" — they're separate beats with different narration density.
3. **Rehearse aloud with `asciinema play demo.cast`.** Time yourself.
4. **Adjust narration length, not cast timing.** If you can't finish the narration before the next cast moment, shorten the narration. Re-recording the cast to fit narration is a path to madness.
5. **Test with a colleague.** A fresh reader catches "this assumes context they don't have" issues you can't see.

## Pacing rules of thumb

| Cast event | Narration target |
|---|---|
| Command being typed | 0.5-1 s of narration ("now I'll run the deploy") |
| Multi-line output appearing | 2-3 s ("notice the error code 503 on line 4") |
| Long-running operation | Whatever it takes to fill the time + 1 s before completion |
| Idle pause / "let me find that file" | Don't record those. Re-record with `--idle-time-limit 1` |

The mistake to avoid: filling silence by reading the screen aloud. If the audience can read what's on the screen, you don't need to read it to them. Use the silence to explain *why* the command matters, not *what* it says.

## Printing the script

For a live talk, render the script as a portrait PDF using Marp or Beamer and bring a printed copy to the lectern:

```bash
# Marp render of the narration as a 1-page printable
marp narration.md --pdf --allow-local-files
```

(Add `theme: minimal` and `paginate: false` to the frontmatter for a single-page handout.)

## Localization

If the audience and the cast use different languages, narrate in the audience's language while keeping the cast commands in English. Add a `lang:` field to the frontmatter and bilingual cells:

```markdown
| Time   | Narration (English)     | Narration (Deutsch)             |
| ------ | ----------------------- | ------------------------------- |
| 00:00  | <English line>          | <German line>                   |
```

Switch which column you read from based on the audience.
