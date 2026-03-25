# Datasheet for Zer0n-Bench v1.0

## Motivation

**For what purpose was the dataset created?**
To provide a verifiable, tamper-evident benchmark for vulnerability detection models. Existing datasets lack provenance integrity (who generated the label?) and often contain "static obsolescence." Zer0n-Bench addresses this by anchoring every label to the Avalanche blockchain, allowing any researcher to independently verify that labels have not been altered since publication.

**Who created the dataset?**
The authors of "Zer0n-Bench: A Provenance-Enabled Vulnerability Dataset with Blockchain-Backed Integrity" (Data4SoftSec '26).

## Composition

**What do the instances that comprise the dataset represent?**
Each instance is a synthetic software vulnerability scenario (a representative code path or API endpoint) accompanied by:
- A vulnerability label (Vulnerable + CWE ID, or Safe)
- Metadata about the AI agents used to generate/verify the label
- A blockchain integrity proof (SHA-256 hash anchored to Avalanche Fuji C-Chain)

Target identifiers are AI-generated representative paths modeled after real-world repository structures (GitHub >500 stars, Etherscan Top-1000 TVL). They are **not** live URLs or pointers to real source files.

**How many instances are there?**
10,050 total instances:
- 5,000 Web Applications (PHP, JavaScript, Python, Java)
- 3,500 Smart Contracts (Solidity on Avalanche)
- 1,550 APIs (REST/GraphQL endpoints)

**Does the dataset contain all possible instances or is it a sample?**
It is a curated synthetic sample designed to cover the OWASP Top 10 and CWE Top 25 with realistic category distributions.

**Is there a label or target associated with each instance?**
Yes. Each instance has a "Vulnerable" (with CWE ID) or "Safe" label.
Labels are assigned a "Confidence Tier":
- **HIGH:** Confirmed by both Zer0n Agents and static analysis (Slither/Semgrep).
- **AI-CONSENSUS:** Confirmed by Red/Blue Agent consensus (static tools silent).
- **DISPUTED:** Disagreement between AI and static tools (flagged for manual review).

## Collection Process

**How was the data associated with each instance acquired?**
All targets are **synthetically generated** vulnerability scenarios modeled after real-world structures:
- **Web Applications:** Synthetic code paths modeled after high-star GitHub repositories (>500 stars, 2024).
- **Smart Contracts:** Synthetic Solidity vulnerability scenarios modeled after Avalanche Fuji testnet contract patterns. No private or mainnet contracts were analyzed.
- **APIs:** Synthetic REST/GraphQL endpoint scenarios modeled after public OpenAPI/Swagger specifications.

**What mechanisms or procedures were used to collect the data?**
The Zer0n Framework pipeline:
1. **Red Agent (Gemini 2.0 Pro, Temp 0.3):** Generates synthetic vulnerability scenarios.
2. **Blue Agent (Gemini 1.5 Pro, Temp 0.1):** Critiques and verifies findings.
3. **Consensus:** Findings agreed upon by both agents (or human review) are hashed via SHA-256.
4. **Anchoring:** Hash is committed to Avalanche Fuji C-Chain via the ZeronMultiSig smart contract (`0x9603145DFEEA4c3292186457BA2ab9b9562BA32c`).

**Over what timeframe was the data collected?**
January 2025 – February 2026. The dataset represents a snapshot of synthetic vulnerability scenarios generated during this period.

## Preprocessing/Cleaning/Labeling

**Was any preprocessing/cleaning/labeling of the data done?**
Yes:
- Duplicate target identifiers were deduplicated (unique suffixes appended).
- Payload PoC snippets are truncated to 512 tokens for LLM context limits.
- Labels were normalized to a binary Vulnerable/Safe schema with a CWE ID for each vulnerable entry.

**How were the labels verified?**
By a 3-layer validation process:
1. **Cross-Tool Agreement:** Checked against Slither (smart contracts) and Semgrep (web/API). Results in `validation/agreement_full.csv` (6,195 entries verified; the remainder were tool-silent and classified as AI-CONSENSUS).
2. **NVD Anchoring:** ~10% of entries cross-referenced against CVE records via CWE pattern matching.
3. **Human Review (IAA Study):** A stratified sample of n=1,000 entries independently annotated by 4 security-trained experts (Expert_A, Expert_B, Expert_C, Expert_D). Fleiss' κ=0.76 (substantial agreement), 89.4% pairwise agreement. Full results in `validation/iaa_results.csv`.

## Uses

**Has the dataset been used for any tasks already?**
Yes, for benchmarking the Zer0n Framework's detection capabilities (F1=78.8%), testing blockchain-based tamper detection, and inter-annotator agreement analysis.

**What (other) tasks could the dataset be used for?**
- Training/fine-tuning LLMs for vulnerability classification.
- Evaluating static analysis tool coverage across CWE types.
- Research into dataset integrity verification and provenance auditing.
- Studying label noise and inter-annotator agreement in security classification tasks.

## Ethical Considerations

**Was any potentially sensitive data collected?**
No real systems were targeted. All instances are **synthetic vulnerability scenarios** generated by AI and modeled after existing public security research benchmarks (OWASP Juice Shop, DVWA, standard CTF challenges). Smart contract scenarios are modeled after Avalanche Fuji testnet patterns — no mainnet contracts were analyzed and no funds were at risk. No personally identifiable information (PII) is present in the dataset. No active exploitation of any real system occurred.

**Known Limitations**
- ~90% of labels are AI-generated; human verification covers n=1,000 entries (10%)
- LLM memorization bias cannot be excluded for scenarios modeled on publicly known CVEs
- Class imbalance: 73.8% vulnerable / 26.2% safe — apply class weighting before training
- Language coverage: No C/C++ or Rust targets; results may not generalize to systems programming
- Temporal snapshot: Labels reflect vulnerability patterns as of Feb 2026; some CWE classifications may evolve
- Synthetic identifiers: Targets are not live URLs — dataset cannot be used for active vulnerability scanning

## Distribution

**Will the dataset be distributed to third parties?**
Yes, open access via Zenodo (DOI: 10.5281/zenodo.18721352).

**How will the dataset be distributed?**
JSON format (per-category and combined), accompanied by CSV validation proofs, blockchain integrity proofs, and verification scripts.

**License:**
Creative Commons Attribution 4.0 International (CC BY 4.0). Users must cite the Zenodo DOI.

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**
The authors. Updates will be released as new versions (v1.1, v1.2) with extended coverage and new blockchain anchors on Avalanche.

**How can the owner/curator/manager of the dataset be contacted?**
Please contact the correspondence author via the email provided in the accompanying paper.
