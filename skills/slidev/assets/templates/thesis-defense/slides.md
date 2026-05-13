---
theme: ./slidev-theme-minimal
title: <FULL THESIS TITLE>
info: |
  ## <FULL THESIS TITLE>
  <SUBTITLE>
class: text-center
transition: slide-left
mdc: true
---

# <FULL THESIS TITLE>

<SUBTITLE>

**<NAME>**
Supervisor: <SUPERVISOR>
<INSTITUTE> · YYYY-MM-DD

---

## Why this thesis

- <One-sentence problem statement>
- <The two paradigms / camps / approaches in tension>
- <The gap your thesis closes — the assumed-but-unverified or the missing>

<!-- 90s. Set the stakes. -->

---

## Research questions

- **RQ1 — <DIMENSION>:** <RQ1 in one sentence>
- **RQ2 — <DIMENSION>:** <RQ2 in one sentence>
- **RQ3 — <DIMENSION>:** <RQ3 in one sentence>

---
layout: two-cols
---

## Experimental setup

- <Hardware / platform>
- <Comparator A> vs <Comparator B>
- <Workload / dataset / fault model>
- <How the experiment is driven>

::right::

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400 h-72 flex items-center justify-center">
REPLACE-architecture.svg
</div>

---

## Methodology

- Single independent variable: <variable>
- Clean-state reset between every run
- <N> runs per condition at each <factor level>
- Timing chain: $T_0 \to T_1 \to T_n$

---
layout: two-cols
---

## RQ1: <DIMENSION>

- <Comparator A>: <number> <unit>
- <Comparator B>: <number> <unit>

> Direction of difference and magnitude in one sentence

::right::

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400 h-72 flex items-center justify-center">
REPLACE-rq1.svg
</div>

---
layout: two-cols
---

## RQ2: <DIMENSION>

- <Comparator A> median: <number> <unit>
- <Comparator B> median: <number> <unit>
- Statistical test result in one line

::right::

<div class="border-2 border-gray-300 rounded p-8 text-center text-gray-400 h-72 flex items-center justify-center">
REPLACE-rq2.svg
</div>

---

## RQ3: <DIMENSION>

- <Sub-metric 1>: <one-line finding>
- <Sub-metric 2>: <one-line finding>
- <Sub-metric 3>: <one-line finding>
- **<Comparator A> vs <Comparator B>, one chart**

---

## Discussion

- Where <Comparator A> wins, where <Comparator B> wins
- Threats to validity (<scale>, <hardware homogeneity>, <fault model>)
- Practical implication: which mode for which workload profile

---

## Conclusion

- RQ1 answer in one sentence
- RQ2 answer in one sentence
- RQ3 answer in one sentence
- **Contribution:** <reproducible artifact / new insight / measurement framework>

---

## Future work

- <Direction 1 — larger scale>
- <Direction 2 — realistic workloads>
- <Direction 3 — additional comparator>
- <Direction 4 — different layer of the stack>

---
layout: end
---

# Thank you

Questions and discussion

<EMAIL>
<REPO-OR-PROJECT-URL>

---
layout: section
---

# Backup

---

## Backup: <COMPONENT-A>

- <Pipeline step 1>
- <Pipeline step 2>
- <Pipeline step 3>

Why this design choice over the alternative.

---

## Backup: <COMPONENT-B>

- <Key configuration detail 1>
- <Key configuration detail 2>
- <Notable metric: <number> <unit>>
