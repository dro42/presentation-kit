---
marp: true
theme: gaia
paginate: true
size: 16:9
header: "<TALK TITLE>"
footer: "<NAME> · <VENUE> · YYYY-MM-DD"
title: "<TALK TITLE>"
author: "<NAME>"
---

<!-- _class: lead -->
<!-- _paginate: false -->

# <TALK TITLE>

<SUBTITLE: clarify scope or hook>

**<NAME>** · <ROLE> @ <ORG>
<VENUE> · YYYY-MM-DD

<!-- ~30 min, ~20 content slides + backup. Tech-talk shape. -->

---

## The hook

> <The war story, the surprising number, the "wait what" moment that frames the talk>

<!-- 60s. Make the audience want to hear the rest. Visual > bullets here. -->

---

## The problem

- <One-sentence problem statement>
- <Why it matters — who feels the pain, how often, how bad>
- <Why it's hard — the constraint that rules out the obvious solution>

---

## Why this is hard

- **<CONSTRAINT 1>** — one-line explanation
- **<CONSTRAINT 2>** — one-line explanation
- **<CONSTRAINT 3>** — one-line explanation

<!-- Naming constraints is what separates a tech talk from a marketing talk. -->

---

## Prior art

- **<APPROACH A>** — what it does well, what it doesn't
- **<APPROACH B>** — what it does well, what it doesn't
- **<APPROACH C>** — what it does well, what it doesn't

<!-- Cite 1-2 anchor references per approach. Be respectful of prior work. -->

---

## Our approach (high level)

![bg right:42%](./figures/REPLACE-architecture.svg)

- <One-sentence headline of what we built>
- <Key design decision 1>
- <Key design decision 2>

---

## Design deep-dive: <COMPONENT 1>

![bg right:45%](./figures/REPLACE-component-1.svg)

- <Inputs / outputs>
- <The interesting bit — the algorithm or data structure>
- <Why it's correct or why it scales>

---

## Design deep-dive: <COMPONENT 2>

- <Inputs / outputs>
- <The trade-off we made and why>
- <The thing we discovered while building this>

---

## Implementation notes

- **Language / runtime:** <choice and why>
- **Built vs reused:** <what we wrote, what we leveraged>
- **Operational surface:** <how it's deployed, scaled, observed>

---

## Live demo

<Live demo or embedded asciinema cast>

```
demo: ./demo.cast    # /asciinema skill produces .cast + narration script
```

<!-- 3-5 minutes. The demo should be the second-most memorable thing after the hook. -->

---

## Results: <HEADLINE METRIC>

![bg right:45%](./figures/REPLACE-headline-metric.svg)

- **<NUMBER> <UNIT>** — vs <BASELINE> at <FACTOR>×
- Test conditions: <briefly>
- Statistical significance: <one line>

---

## Results: <SUPPORTING METRIC>

- <Sub-metric 1>: <number>
- <Sub-metric 2>: <number>
- <Caveat / scope of validity>

---

## What we got wrong

- **<MISTAKE 1>** — what we thought, what actually happened, what we changed
- **<MISTAKE 2>** — same shape

<!-- Audiences love negative results from credible speakers. -->

---

## Lessons learned

- <LESSON 1 — generalizable beyond this project>
- <LESSON 2 — generalizable beyond this project>
- <LESSON 3 — generalizable beyond this project>

---

## Future directions

- <DIRECTION 1>
- <DIRECTION 2>
- <DIRECTION 3>

---

## Resources

- **Code:** <URL>
- **Paper / writeup:** <URL>
- **Slides:** <URL>
- **Contact:** <EMAIL> · <SOCIAL HANDLE>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Questions?

<EMAIL>

---

<!-- _class: lead -->

# Backup slides

For Q&A — additional benchmarks, design alternatives, FAQ

---

## Backup: <ALTERNATIVE DESIGN we considered>

- <What we considered>
- <Why we didn't pick it>
- <Conditions under which it would win>

---

## Backup: <DETAILED BENCHMARKS>

- <Workload A>: <numbers>
- <Workload B>: <numbers>
- <Workload C>: <numbers>

---

## Backup: <FAQ — the question that always comes up>

> <Anticipated question>

<One-paragraph answer>
