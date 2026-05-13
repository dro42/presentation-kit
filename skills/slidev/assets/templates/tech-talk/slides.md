---
theme: ./slidev-theme-minimal
title: <TALK TITLE>
info: |
  ## <TALK TITLE>
  <SUBTITLE>
class: text-center
transition: slide-left
mdc: true
---

# <TALK TITLE>

<SUBTITLE>

**<NAME>** · <ROLE> @ <ORG>
<VENUE> · YYYY-MM-DD

<!-- ~30 min, ~20 content slides + backup. -->

---

## The hook

> <The war story, the surprising number, the "wait what" moment that frames the talk>

<!-- 60s. Visual > bullets here. -->

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

---

## Prior art

- **<APPROACH A>** — what it does well, what it doesn't
- **<APPROACH B>** — what it does well, what it doesn't
- **<APPROACH C>** — what it does well, what it doesn't

---
layout: two-cols
---

## Our approach

- <One-sentence headline>
- <Key design decision 1>
- <Key design decision 2>

::right::

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400 h-80 flex items-center justify-center">
REPLACE-architecture.svg
</div>

---

## Design deep-dive: <COMPONENT 1>

```ts {1-3|5-9|all}
interface Input {
  // ...
}

function compute(x: Input): Result {
  const a = x.value * 2;
  const b = a + 1;
  return { final: b };
}
```

- The interesting bit — the algorithm or data structure
- Why it's correct or why it scales

---

## Design deep-dive: <COMPONENT 2>

- Inputs / outputs
- The trade-off we made and why
- The thing we discovered while building this

---

## Implementation notes

- **Language / runtime:** <choice and why>
- **Built vs reused:** <what we wrote, what we leveraged>
- **Operational surface:** <how it's deployed, scaled, observed>

---

## Live demo

<!--
Register AsciinemaPlayer (see asciinema/assets/embed-snippets/slidev.md)
and place demo.cast under public/, then:

<AsciinemaPlayer src="/demo.cast" :cols="100" :rows="30" theme="monokai" />
-->

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400">
  Live demo or embedded asciinema cast
</div>

---
layout: two-cols
---

## Results: <HEADLINE METRIC>

- **<NUMBER> <UNIT>** vs <BASELINE> at <FACTOR>×
- Test conditions: <briefly>
- Statistical significance: <one line>

::right::

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400 h-72 flex items-center justify-center">
REPLACE-headline-metric.svg
</div>

---

## Results: <SUPPORTING METRIC>

- <Sub-metric 1>: <number>
- <Sub-metric 2>: <number>
- <Caveat / scope of validity>

---

## What we got wrong

- **<MISTAKE 1>** — what we thought, what actually happened, what we changed
- **<MISTAKE 2>** — same shape

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
layout: end
---

# Questions?

<NAME> · <EMAIL>

---
layout: section
---

# Backup

---

## Backup: alternative design considered

- What we considered
- Why we didn't pick it
- Conditions under which it would win

---

## Backup: detailed benchmarks

- Workload A: <numbers>
- Workload B: <numbers>
- Workload C: <numbers>

---

## Backup: FAQ

> <Anticipated question>

<One-paragraph answer>
