---
marp: true
theme: gaia
paginate: true
size: 16:9
header: "<DEFENSE LABEL> · <SHORT TITLE>"
footer: "<NAME> · <INSTITUTE> · YYYY-MM-DD"
title: "<FULL THESIS TITLE>"
author: "<NAME>"
---

<!-- _class: lead -->
<!-- _paginate: false -->

# <FULL THESIS TITLE>

<SUBTITLE — one line describing scope or contribution>

**<NAME>**
Supervisor: <SUPERVISOR>
<INSTITUTE> · YYYY-MM-DD

---

## Why this thesis

- <One-sentence problem statement>
- <Two paradigms, two camps, or two competing approaches — frame the tension>
- <The gap your thesis closes — what is assumed but unverified, or what is missing>

<!-- 90s. Set the stakes; do not over-explain context. -->

---

## Research questions

- **RQ1 — <DIMENSION>:** <RQ1 in one sentence>
- **RQ2 — <DIMENSION>:** <RQ2 in one sentence>
- **RQ3 — <DIMENSION>:** <RQ3 in one sentence>

---

## Experimental setup

![bg right:42%](./figures/REPLACE-architecture.svg)

- <Hardware / platform>
- <Comparator A> vs <Comparator B>
- <Workload / dataset / fault model>
- <How the experiment is driven>

---

## Methodology

- Single independent variable: <variable>
- Clean-state reset between every run
- <N> runs per condition at each <factor level>
- Timing chain: <T0> → <T1> → <Tn>

---

## RQ1: <DIMENSION>

![bg right:45%](./figures/REPLACE-rq1.svg)

- <Comparator A>: <number> <unit>
- <Comparator B>: <number> <unit>
- **Direction and magnitude in one sentence**

---

## RQ2: <DIMENSION>

![bg right:45%](./figures/REPLACE-rq2.svg)

- <Comparator A> median: <number> <unit>
- <Comparator B> median: <number> <unit>
- **Statistical test** result in one line

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

<!-- _class: lead -->
<!-- _paginate: false -->

# Thank you

Questions and discussion

<EMAIL>
<REPO-OR-PROJECT-URL>

---

<!-- _class: lead -->

# Backup slides

For Q&A — methodology details, additional metrics, ablations

---

## Backup: <COMPONENT-A>

![bg right:50%](./figures/REPLACE-backup-1.svg)

- <Pipeline step 1>
- <Pipeline step 2>
- <Why this design choice over the alternative>

---

## Backup: <COMPONENT-B>

- <Key configuration detail 1>
- <Key configuration detail 2>
- <Notable metric: <number> <unit>>
