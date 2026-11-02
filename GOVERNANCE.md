# Introduction

This document outlines some principles for altering CAMO, including frameworks for decision-making and so on. It is an evolving document.

## Who decides?

For now, Tim Alamenciak is the main curator. He (I) would love to have help! Ideally this schema will be governed by a team of 4-6 people with varied backgrounds but a common interest in representing causality.

## Adding new fields for annotation

Any new field (slot or whole class) should satisfy five criteria:

- **Frequent:** It appears in a meaningful share of papers (say 10%), and across at least two study designs or ecosystems.
- **Consequential:** You can name the downstream use that breaks without it, such as an evidence-gap-map cell, a dynamic model, or the GRADE rating.
- **Structured:** Its values are an enum, a number or an ID. If it would only ever be free text, a slot adds nothing over the free text that exists.
- **Reliable:** Annotators (and an LLM) fill it consistently and with clarity.
- **Novel:** nothing existing can hold it.