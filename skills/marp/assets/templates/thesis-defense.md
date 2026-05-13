---
marp: true
theme: gaia
paginate: true
size: 16:9
header: "BA2 Defense · Sidecar vs Ambient"
footer: "Andreas Drozd · FH Campus Wien · YYYY-MM-DD"
title: "Sidecar vs. Ambient: Telemetry Reliability and Automated Canary Remediation"
author: "Andreas Drozd"
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Sidecar vs. Ambient

Telemetry Reliability and Automated Canary Remediation in a GitOps-Managed Kubernetes Environment

**Ing. Andreas Drozd**
Supervisor: Priv.-Doz. Dr. Karl M. Goeschka
CSDC · FH Campus Wien · YYYY-MM-DD

---

## Why this thesis

- Service meshes are now standard infrastructure
- Two paradigms compete: **sidecar** (per-pod proxy) vs **ambient** (shared per-node)
- Their telemetry is **assumed comparable** — but is it, under canary deployments with fault injection?

<!-- 90s. Set the stakes: automated canary decisions ride on this telemetry. -->

---

## Research questions

- **RQ1 — Decision correctness:** how do false-positive and false-negative rates of automated canary abort decisions differ between modes?
- **RQ2 — Remediation speed:** how does end-to-end remediation latency compare?
- **RQ3 — Telemetry fidelity:** what differences in metric completeness, label attribution, and signal stability exist?

---

## Experimental setup

![bg right:42%](./figures/REPLACE-cluster-arch.svg)

- k3s on 2× Raspberry Pi 5 (16 GB)
- Istio **sidecar 1.28** vs **ambient 1.29**
- podinfo v6.5.4 / v6.6.0 — 90/10 canary split
- Fault injection via Argo Workflows (HTTP 500 + latency)

---

## Methodology

- Single independent variable: mesh mode
- Clean-state reset between every run (GitOps-controlled mode switch)
- 10 runs per mode at each fault percentage
- Timing chain: T0 (fault start) → T1 (alert fires) → T5 (traffic shift complete)

---

## RQ1: Decision correctness

![bg right:45%](./figures/REPLACE-rq1-decision-matrix.svg)

- Sidecar: X false positives, Y false negatives
- Ambient: X' false positives, Y' false negatives
- **Direction of difference and magnitude in one sentence**

---

## RQ2: Remediation speed

![bg right:45%](./figures/REPLACE-rq2-timing-boxplot.svg)

- Median T1−T0 (alert latency): sidecar X s vs ambient Y s
- Median T5−T0 (full remediation): sidecar X s vs ambient Y s
- **Statistical test** result in one line

---

## RQ3: Telemetry fidelity

- Metric completeness: % of expected series present
- Label attribution: source/destination resolution accuracy
- Signal stability: variance across runs
- **Mode-by-mode comparison, one chart**

---

## Discussion

- Where sidecar wins, where ambient wins
- Threats to validity (cluster scale, hardware homogeneity, fault model)
- Practical implication: which mode for which workload profile

---

## Conclusion

- RQ1 answer in one sentence
- RQ2 answer in one sentence
- RQ3 answer in one sentence
- Contribution: reproducible GitOps-managed comparison harness

---

## Future work

- Larger-scale cluster (multi-node ambient)
- Production traffic patterns vs synthetic
- L7 policy enforcement comparison
- eBPF-based meshes (Cilium) as a third arm

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Thank you

Questions and discussion

andidrd@gmail.com
github.com/dro42/sem6_ba2_service_mesh_latex

---

<!-- _class: lead -->

# Backup slides

For Q&A — methodology details, additional metrics, ablations

---

## Backup: Alert pipeline

![bg right:50%](./figures/REPLACE-alert-pipeline.svg)

- PrometheusRule → Alertmanager → Argo Events webhook → Sensor → Workflow
- Why event-driven over polling

---

## Backup: Mode-switch GitOps flow

- ArgoCD app-of-apps pattern
- `modes/{none,istio-sidecar,istio-ambient}` directories
- Mean switch time: REPLACE s
