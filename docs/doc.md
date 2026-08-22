# `docs/` Reference Library Guide

## Purpose

The `docs/` directory is the project's **reference library**, not project knowledge that Claude needs to ingest permanently.

It contains large building codes, nonlinear-analysis standards, and seismic-performance guidance used to verify modelling and research decisions. The repository currently separates these into:

- `docs/BuildingCodes/BNBC/` — BNBC 2020 parts and index.
- `docs/BuildingCodes/US/` — ACI, ASCE 7-22 and ASTM references.
- `docs/NL-Codes/` — nonlinear-analysis, seismic-performance, fragility and performance-based-engineering references.

The repository tree confirms these three main reference groups. The BNBC directory contains Parts 1–10 plus an index; the US directory contains ACI, ASCE 7-22 and ASTM material; and the nonlinear-analysis directory contains ASCE 41-23 and multiple FEMA documents, including the FEMA P-58 series. 

## Important Claude Instruction

**Do NOT upload the PDFs in `docs/` to the Claude Project as permanent project knowledge unless there is a specific reason to do so.**

They are large primary/authoritative documents, many are readily obtainable from official or public sources, and permanently ingesting all of them would unnecessarily consume project context.

Instead:

1. Treat this file as the **map to the reference library**.
2. When a specific technical question requires a code/reference, identify the relevant document here.
3. Retrieve or consult the authoritative source when needed.
4. Cite the exact document and clause/section/page in research outputs.
5. Never rely on a remembered paraphrase when the exact provision matters.

The PDFs in the repository remain useful as a versioned reference archive.

---

# 1. BNBC 2020

### Location

`docs/BuildingCodes/BNBC/`

### Contents

The directory contains:

- `BNBC_2020_Index.pdf`
- `BNBC_2020_Part-1.pdf`
- `BNBC_2020_Part-2.pdf`
- `BNBC_2020_Part-3.pdf`
- `BNBC_2020_Part-4.pdf`
- `BNBC_2020_Part-5.pdf`
- `BNBC_2020_Part-6.pdf`
- `BNBC_2020_Part-7.pdf`
- `BNBC_2020_Part-8.pdf`
- `BNBC_2020_Part-9.pdf`
- `BNBC_2020_Part-10.pdf`

### Primary use

BNBC 2020 is the **primary governing design reference for this research**.

Use it when determining:

- seismic hazard and zoning
- site classification
- design response spectra
- seismic coefficients
- response modification factors
- structural-system classification
- load combinations
- RC member design requirements
- reinforcement limits
- ductile detailing
- drift requirements
- irregularity provisions
- structural analysis requirements
- material/design assumptions used to construct the parametric building models

The repository currently includes the complete Part 1–10 collection rather than only the seismic section.

### Rule

When the research makes a claim of the form:

> "BNBC 2020 requires/provides/specifies X"

verify the actual BNBC provision before accepting the claim.

Do not substitute ACI, ASCE, FEMA or another international standard for a BNBC requirement unless the research explicitly establishes that relationship.

---

# 2. ACI / US Structural Design References

### Location

`docs/BuildingCodes/US/`

### Contents

- `ACI_Code.pdf`
- `ASCE-7-22/`
  - `ASCE-7-22-Part1-Upto Seismic.pdf`
  - `ASCE-7-22-Part2-Wind.pdf`
  - `ASCE-7-22-Part3-Commentary.pdf`
- `ASTM-Standard.pdf`
- `ASTM_bluebook.pdf`

### Primary use

These documents are **supporting technical references**, not substitutes for BNBC 2020.

Use them when investigating:

- RC material behaviour
- reinforcement/material testing conventions
- seismic loading methodology
- comparison with US practice
- terminology and methodological background
- assumptions inherited from US-based seismic literature
- validation of modelling approaches where BNBC is silent or less explicit

### Important distinction

Do not automatically import an ASCE 7, ACI or ASTM provision into a BNBC-based design.

For example:

**BNBC requirement → primary design basis**

**ACI/ASCE/ASTM → supporting/comparative reference**

If the research adopts a US provision because BNBC does not adequately define something, document that as an explicit methodological decision.

---

# 3. ASCE 41-23

### Location

`docs/NL-Codes/ASCE 41-23.pdf`

### Primary use

Use for:

- seismic evaluation of existing buildings
- nonlinear structural modelling concepts
- component modelling
- acceptance criteria
- deformation-based performance evaluation
- nonlinear static/dynamic analysis methodology
- comparison of modelling assumptions
- performance-based seismic engineering context

### Caution

ASCE 41 is an **evaluation standard**, not automatically the governing design standard for the BNBC 2020 buildings in this study.

Use it to support nonlinear evaluation methodology where appropriate, and clearly identify which provisions are being adopted.

---

# 4. FEMA Nonlinear / Seismic References

### Location

`docs/NL-Codes/`

Current major references include:

- `FEMA P-1050-2.pdf`
- `FEMA P-2082-1.pdf`
- `FEMA-349.pdf`
- `FEMA-440.pdf`
- `FEMA-445.pdf`
- `Fema356.pdf`

These should be treated as **methodological references**, not automatically applicable code requirements.

---

## 4.1 FEMA 356

### Use for

Historical/nonlinear-performance methodology, including:

- nonlinear static procedures
- performance objectives
- component acceptance concepts
- deformation-based evaluation
- foundations of later performance-based seismic procedures

### Caution

FEMA 356 is superseded by later developments in several areas. Do not cite it as the current authority merely because it is present in the repository.

Use it primarily for methodological background or when tracing the origin of a procedure.

---

## 4.2 FEMA 440

### Use for

Nonlinear static / pushover methodology, especially:

- equivalent-linearisation concepts
- displacement modification
- relationship between nonlinear static response and seismic demand

Use when explaining or evaluating nonlinear static analysis methodology.

---

## 4.3 FEMA 445

### Use for

Performance-based seismic design methodology and framework development.

Use primarily for:

- conceptual performance-based engineering methodology
- performance objectives
- design-process context
- methodological background

---

## 4.4 FEMA 349

### Use for

Seismic design/evaluation methodology and performance-based engineering background.

Use only where its specific methodology is relevant; do not treat it as a generic source for every nonlinear-analysis claim.

---

# 5. FEMA P-1050-2

### Use for

Modern seismic design / performance-based seismic engineering guidance and background.

Use when the research requires:

- modern seismic design methodology
- performance-based engineering concepts
- seismic response interpretation
- comparison with current US practice

Always verify the exact topic and section before citing it.

---

# 6. FEMA P-2082-1

### Use for

Seismic hazard, performance and risk-related methodological background.

Use when the research discusses:

- seismic risk
- earthquake effects
- performance interpretation
- hazard-related engineering context

Do not use it as a replacement for the BNBC 2020 hazard model.

---

# 7. FEMA P-58 Series

### Location

`docs/NL-Codes/FEMA-P-58/`

Contains:

- `FEMA_P-58-1 Methodology.pdf`
- `FEMA_P-58-2 Implementation_compressed.pdf`
- `FEMA_P-58-4 Environmental-Impacts.pdf`
- `FEMA_P-58-5 ExpectedPerformance.pdf`
- `FEMA_P-58-6 GuidelinesForDesign.pdf`
- `FEMA_P-58-7 BuildingThePerformanceYouNeed.pdf`

### Primary use

Use this family when the research expands from simple drift prediction toward **performance-based earthquake engineering (PBEE)** and loss/risk-oriented assessment.

Particularly relevant for:

- performance metrics
- damage states
- component-level consequences
- probabilistic performance
- expected damage/loss
- performance-based design
- interpretation of engineering demand parameters

This material becomes especially important if the project evolves beyond:

`ground motion → PIDR`

toward:

`ground motion → structural response → damage → consequence/performance`.

### Important

Do not claim that a FEMA P-58 methodology has been implemented merely because P-58 is cited. The actual implemented variables, probability model, damage model and consequence model must exist in the code.

---

# 8. Reference Selection Hierarchy

When multiple references appear to support the same statement, use this hierarchy.

### For BNBC design requirements

**BNBC 2020 > supporting international standards > secondary literature**

### For nonlinear structural evaluation

**Applicable current standard/guideline > established FEMA/ASCE methodology > research papers > tutorials**

### For scientific methodology

**Peer-reviewed primary paper > authoritative technical report > review paper > textbook/tutorial**

### For OpenSeesPy implementation

Use the **official OpenSees/OpenSeesPy documentation** and validated examples. OpenSeesPy's official documentation provides command definitions and examples for modelling and analysis. citeturn0search6turn0search5

---

# 9. When Claude Should Consult Which Reference

| Research task | Primary reference |
|---|---|
| BNBC seismic zone / hazard | BNBC 2020 |
| BNBC response spectrum | BNBC 2020 |
| BNBC R-factor / structural system | BNBC 2020 |
| RC member/detailing requirement | BNBC 2020 + applicable ACI provisions where explicitly relevant |
| Load combinations | BNBC 2020 |
| Seismic loading comparison | BNBC 2020 + ASCE 7 |
| RC material/testing background | BNBC / ACI / ASTM |
| Nonlinear component modelling | ASCE 41 + relevant primary literature |
| Pushover methodology | FEMA 440 + relevant literature |
| Historical performance-based methodology | FEMA 356 |
| Performance-based seismic engineering | FEMA P-1050 / relevant FEMA guidance |
| Seismic risk/performance | FEMA P-2082-1 |
| PBEE / damage / loss | FEMA P-58 |
| Nonlinear evaluation | ASCE 41-23 |
| OpenSeesPy commands | Official OpenSeesPy documentation |
| Research-specific modelling choice | Peer-reviewed literature + mechanics-based justification |

---

# 10. How to Use the Repository PDFs

The PDFs should be considered a **local reference archive**.

They are not the project's permanent knowledge base.

When a question arises:

### Example 1 — BNBC R-factor

Do not answer from memory.

1. Identify the BNBC seismic/system provision.
2. Locate the relevant table/section.
3. Verify the exact value.
4. Record the citation.
5. Implement it in the model/configuration.
6. Add the source to the methodology documentation.

### Example 2 — PIDR damage threshold

Do not assume a value is "BNBC 2020."

1. Identify the proposed threshold.
2. Determine its actual source.
3. Check whether it is a design criterion, evaluation criterion, empirical threshold, or research convention.
4. Cite the original source.
5. Explain why it is appropriate for this study.

### Example 3 — OpenSeesPy material model

1. Identify the material command.
2. Consult official OpenSeesPy documentation.
3. Check the original material-model paper.
4. Verify parameter definitions and sign conventions.
5. Validate the implementation against a benchmark before using it for production simulations.

---

# 11. Do Not Do This

Claude must **not**:

- treat every PDF in `docs/` as equally authoritative;
- quote a clause without verifying it;
- use FEMA guidance as if it were BNBC code;
- use ACI/ASCE requirements as automatic BNBC requirements;
- cite a document simply because its filename contains the relevant keyword;
- assume an old FEMA procedure is still the preferred current methodology;
- fabricate page/section numbers;
- claim that a provision is "code-required" when it is only a modelling convention;
- use the repository PDFs as a substitute for current official sources when a current revision matters.

---

# 12. Relationship to the Research Code

The reference hierarchy should ultimately feed the implementation:

```text
Authoritative reference
        ↓
Verified provision / methodology
        ↓
Research assumption
        ↓
Model parameter
        ↓
OpenSeesPy implementation
        ↓
Numerical verification
        ↓
Simulation dataset
        ↓
ML / fragility analysis
        ↓
Research conclusion
```

Every important modelling parameter should be traceable backward through this chain.

---

# 13. Maintenance

When adding a new reference to `docs/`:

1. Add it to the appropriate category.
2. Add it to this document.
3. State its purpose.
4. State whether it is:
   - governing
   - supporting
   - historical
   - methodological
   - comparative
5. Do not add large documents merely because they are tangentially related.

The `docs/` directory should remain a **curated research reference library**, not a document dump.
