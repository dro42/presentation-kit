# Thesis Defense — Slide Checklist

Structure and pacing for a bachelor's or master's thesis defense. Use this checklist when scaffolding a deck via `assets/templates/thesis-defense.tex`. The shape mirrors the marp counterpart so the same content can be authored in either format.

## Talk envelope

- **Speaking time:** ~15 minutes (talk) + ~10–15 minutes Q&A is a common bachelor's-defense envelope. Master's defenses are often 20+10 or 25+15. Confirm with the supervisor or programme office — the rules vary by institution and programme.
- **Slide budget:** 12–15 content frames + title + thank-you + backup section. **~1 frame per minute of talk** is the rule of thumb.
- **Audience:** supervisor, second examiner (sometimes a third), and any programme-committee members. Assume domain familiarity for the thesis topic, but assume zero familiarity with the specific experimental setup.

## Required structure (in order)

1. **Title slide** — thesis title, subtitle, your name, supervisor name(s), institute / department, date.
2. **Why this thesis** (motivation, 1–2 frames) — the gap or problem in 2–3 sentences. The audience should be able to repeat back the thesis statement after this section. Avoid generic "X is important" openers; lead with the specific gap your thesis closes.
3. **Research questions** (1 frame) — exactly the RQs as they appear in the written thesis. Numbered (RQ1, RQ2, …). If the written thesis has 4+ RQs, consider showing 3 on the slide and listing the others as "additional sub-questions, see § 3.2."
4. **Experimental setup / methodology context** (1–2 frames) — what was built, on what hardware, against what comparator. One architecture diagram is worth three bullet lists here.
5. **Methodology** (1 frame) — the *experimental design*: independent variable, controlled variables, sample size, statistical test. The committee will probe this; do not skip it.
6. **Results — one frame per RQ** (3–4 frames) — for each RQ, show the headline number plus a single visual. Direction of difference and magnitude in one sentence. Avoid raw tables of 30 numbers; pre-digested charts or summary statistics.
7. **Discussion** (1 frame) — what the results mean (interpretation, not restatement), threats to validity, practical implications. This is where the committee evaluates whether you understand the limitations of your own work.
8. **Conclusion** (1 frame) — one-line answer per RQ, plus the headline contribution. The slide should be readable in 30 seconds; it's what the committee re-reads while deliberating.
9. **Future work** (1 frame) — 3–4 concrete follow-ups. Demonstrates you understand the work's boundaries.
10. **Thank you** (1 frame, `[plain]`) — your name + supervisor + contact. Used as the static slide during Q&A.
11. **Backup section** (3–8 frames, `\appendix`) — methodology details, additional metrics, ablations, code samples. Material you'd want available *if asked* but not part of the main flow.

## Content principles

- **One claim per frame.** If a frame has two distinct claims, split it into two frames.
- **Three to five bullets max.** Beyond five, the audience reads instead of listening.
- **Speaker notes on every content frame.** `\note{...}` captures the 30–60 second narration for each slide. Even if you don't print them, the discipline of writing them out exposes weak narrative transitions.
- **Numbers must be reproducible.** Every quantitative claim ("median latency improved by 18 %") needs a method-derivable provenance. The committee will ask "with what test, at what n, with what alpha."
- **No screenshot of code unless the talk is about the code.** A 90-line YAML manifest belongs in the thesis appendix, not on a defense slide. Show the *diagram* of what the code does.
- **No animated reveals unless they teach something.** Three `\pause` calls in a row break flow; the audience starts dreading clicks.

## Visual identity

The bundled `beamerthemeMinimal.sty` is a token-driven Madrid extension — override the brand primary/secondary/accent colors and the footer text to match your institution. The marp counterpart (`minimal.css`) shares the same token names; both themes can be updated in parallel from one source of brand truth.

If your supervisor mandates a plainer look (some examiners prefer it for academic neutrality), the default Beamer theme with `\setbeamertemplate{navigation symbols}{}` is the standard low-risk choice. Avoid Madrid out of the box unless the brand colors are configured; the default royal blue clashes with most institutional palettes.

If you have an institutional template (logo, official color palette), recreate it as a personal theme:

```bash
# Save your institutional theme into your user-data directory
bash scripts/save-theme.sh beamer my-institute ./beamerthemeMyInstitute.sty
```

It then lives at `~/.local/share/presentation-kit/themes/beamer/beamerthemeMyInstitute.sty` and survives plugin updates.

## Day-of pacing rehearsal

Before the defense:

1. Rehearse the talk *aloud* with a timer. Target ~93 % of the slot — leaves a small buffer for unexpected clarification.
2. Identify the 3 frames most likely to draw committee questions; pre-write the backup slides that answer them.
3. Print or render the speaker-notes PDF (`\setbeameroption{show only notes}` or use `pdfpc`).
4. Test the venue's projector ratio (most lecture halls are 16:9; smaller seminar rooms can be 4:3). Match `\documentclass[aspectratio=...]{beamer}` accordingly.
5. Bring the deck on two separate USB sticks + cloud copy. Don't rely on the venue WiFi.

## What committees commonly probe

- **"Why this comparator?"** — defend the choice of baseline / comparison. Cover this in the methodology frame.
- **"How many runs? Is the difference significant?"** — sample size and statistical test must be on the methodology slide or in backup.
- **"What if you changed X?"** — sensitivity / robustness. Have an ablation slide ready in backup.
- **"What didn't work?"** — be ready to discuss negative results honestly. Hiding failure modes erodes credibility.
- **"How does this generalize?"** — threats to validity (slide 7). Acknowledging boundaries strengthens the work.
- **"Where would you take this next?"** — future-work slide does the heavy lifting, but be prepared to defend the *prioritization*.

## Anti-patterns to avoid

- Reading bullets verbatim. The audience can read; your job is the connective tissue.
- Backup section with 20+ frames. Five or six well-chosen backups beat twenty unfocused ones.
- Apologizing for limitations ("unfortunately, due to time constraints…"). State the limitation as a *design choice* with rationale.
- Skipping the methodology slide ("everyone knows how X works"). The second examiner often doesn't.
- A "References" slide with 40 citations in 8-pt font. References belong in the written thesis; cite inline in the talk only where load-bearing.
