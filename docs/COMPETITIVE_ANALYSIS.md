# Competitive Landscape & Market Reference Analysis
### *Canon Ledger: Benchmarking Story Bibles, Timeline Managers, and Continuity Checkers*

**Date:** November 2026  
**Project:** Canon Ledger — Living Story Bible & Continuity Sentinel  

---

## 1. Executive Summary

Authors writing long novels (80,000–100,000+ words) and multi-book series consistently face cognitive overload tracking physical traits, timeline dates, world rules, and character knowledge states. 

A thorough investigation of the 2026 writing software ecosystem reveals a critical split in the market:
1. **Generative AI Co-Writers (Sudowrite, Novelcrafter):** Focus heavily on *generating* or *rewriting* prose, using story bibles primarily as prompt-injection memory rather than forensic checkers.
2. **Traditional Relational Planners (Plottr, Aeon Timeline, Campfire Write, Chronicle):** Excellent manual databases, but require laborious manual data entry for every scene, character, and event.
3. **Niche Continuity Checkers (LoreKeep, LitMemo, Galleys):** Either restricted to mobile platforms (iPad), tailored to post-draft developmental overhauls, or requiring manual note-taking before checking.

**Canon Ledger occupies the white space:** It ingests the author's *existing manuscript*, *automatically constructs* the living story bible, delivers *side-by-side verifiable citation flags*, *remembers author dismissals*, and strictly enforces **100% author sovereignty** by never rewriting prose.

---

## 2. Competitive Feature Matrix

| Tool & Reference URL | Category | Story Bible Mode | Auto-Extraction from Manuscript | Contradiction Checking Mechanism | Author Control Philosophy | Key Limitation / Gap Filled by Canon Ledger |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Canon Ledger**<br>*(This Project)* | **Continuity Sentinel** | **Living Bible (Auto-extracted)** | **Full** (Chapter & sentence citations) | **Strict Side-by-Side Verifiable Quotes** | **100% Author Sovereignty** (Never rewrites prose) | **N/A (The Benchmark)** |
| **Sudowrite**<br>[sudowrite.com](https://sudowrite.com)<br>[docs](https://docs.sudowrite.com) | AI Co-Writer | Manual Story Bible cards & universe lore | Includes "Import Novel" auto-generation; primary mode is drafting | Context injection for drafting; no forensic citation audit | Co-Writer (Generates & rewrites text) | Co-writes rather than checks; prone to series context amnesia. |
| **Novelcrafter**<br>[novelcrafter.com](https://www.novelcrafter.com) | AI Writing Studio | The Codex & Series Codex | Detects entity mentions; allows lore sheets and series sharing | AI Chat queries & context prompts | Co-Writer / Prompt assistant | Heavy manual curation needed; focused on drafting new scenes. |
| **Chronicle**<br>[producthunt](https://www.producthunt.com/products/chronicle-13) | Local Planning Tool | Local story bible & relational timeline | Describes automated story bible generation from text files | Visual timeline & entity views; lacks automated contradiction checks | 100% Manual | Zero automated contradiction detection. |
| **LoreKeep**<br>[apple.com](https://apps.apple.com/app/id6791226620) | Mobile Worldbuilder | Manual lore cards & relationships | None (Manual bible creation) | AI Analyzer flags plot/character contradictions against bible | Advisory feedback | Locked to iPad/iOS; requires manual bible entry before checking. |
| **LitMemo**<br>[litmemo.com](https://www.litmemo.com)<br>[producthunt](https://www.producthunt.com/products/litmemo) | Creative Project Tool | Manual wiki & character sheets | None | AI flags timeline & past visit discrepancies | Advisory alert | Focuses on team project management; relies on manual notes. |
| **Galleys**<br>[galleys.ai](https://galleys.ai) | AI Manuscript Editor | Internal developmental ledger | Full document scan | Full-manuscript developmental audit & repetition scanner | Developmental report | Geared toward complete post-draft structural audits, not living chapter-by-chapter series tracking. |
| **Plottr**<br>[plottr.com](https://plottr.com/series-bible-software/) | Visual Outliner | Visual Series Bible (100% manual) | None | None | Manual planner | Visual timeline grids, but zero automated checking or extraction. |
| **Aeon Timeline**<br>[aeontimeline.com](https://aeontimeline.com) | Timeline Database | Relational event & entity database | None (Syncs with Scrivener/Ulysses) | Calculates mathematical date & age clashes from manual dates | Manual planner | Industry standard for date math, but requires manual date entry for every single scene. |
| **Campfire Write**<br>[campfirewriting.com](https://www.campfirewriting.com) | Worldbuilding Suite | Modular character webs & maps | None | None | Manual planner | Deep modular lore sheets, but maintaining them across 100k words becomes exhausting. |
| **CanonGuard AI**<br>[turbostarter.dev](https://www.turbostarter.dev/ideas/other/canon-guard-ai) | Product Concept | Conceptual automated bible | Conceptual | Proposed plot-hole & character scan | Advisory | Unreleased product concept; proves market appetite. |

---

## 3. Evidence of Market Demand

### 1. Sudowrite Community Feature Request [#63877](https://feedback.sudowrite.com/feedback/63877)
* **User Demand:** Authors frequently request automated scanning of prior books and chapters to build series bibles.
* **Problem Identified:** Manually writing hundreds of character sheets, location profiles, and magic constraints for an existing 3-book series takes weeks. When authors try to do it by hand, the cognitive overhead causes them to abandon the effort.
* **Canon Ledger Solution:** One-click ingestion of `.txt`, `.md`, or `.docx` chapters automatically extracts characters, physical traits, travel durations, and rules tied directly to chapter and sentence IDs.

### 2. Novela Publishing Research: ["The Story Bible That Gets Used"](https://novela.so/en/blog/story-bible-that-gets-used)
* **Core Finding:** Most story bibles get initiated during early worldbuilding enthusiasm and are abandoned as word count expands past Chapter 10.
* **Problem Identified:** A tool that requires the author to pause drafting to manually update 15 attributes whenever a character gets a scar will inevitably fall out of date.
* **Canon Ledger Solution:** The living bible extracts lore organically as chapters are written and added, requiring zero extra maintenance steps.

### 3. Inkfluence AI: ["Best AI Novel Continuity Checking 2026"](https://www.inkfluenceai.com/blog/best-ai-novel-continuity-checking-2026)
* **Core Finding:** Contemporary AI tools suffer from a structural flaw: they either hallucinate "corrections" because they lack verbatim citations, or they force the author into using the AI to co-write prose.
* **Canon Ledger Solution:** Strict citation verification ensures that if a flag cannot cite both the exact earlier sentence and current sentence, it is automatically dropped. And Canon Ledger never rewrites the author's prose.

---

## 4. Canon Ledger's Four Core Moats

```
                     CANON LEDGER
            ┌─────────────┴─────────────┐
            ▼                           ▼
1. Zero-Friction Ingestion    2. Verifiable Citations
   • Reads TXT, MD, DOCX         • Side-by-side comparison
   • Sentence-level granularity  • Drops unverified claims
   • Chapter-by-chapter memory   • Zero hallucinated alerts
            │                           │
            ▼                           ▼
3. Dismissal Persistence       4. Absolute Author Sovereignty
   • Deterministic SHA-256 hash  • Sentinel, NOT co-writer
   • False alarms never recur    • Never generates prose
   • Respects author intent      • Author decides every fix
```

1. **Zero-Friction Ingestion:** Works on what the author has already written (Word documents, Markdown files, or plain text) rather than forcing them into a proprietary text editor.
2. **Verifiable Citations:** Solves the #1 risk of AI tools—false positives and hallucinated errors. Every alert provides the exact earlier quote, chapter number, sentence number, and current conflicting quote.
3. **Dismissal Persistence:** Literary fiction is filled with poetic metaphor (e.g., *"eyes burning with icy fire"*). When the author clicks "Dismiss", Canon Ledger registers a deterministic hash fingerprint so the author is never nagged about that passage again.
4. **Absolute Author Sovereignty:** Unlike tools that treat AI as a replacement author, Canon Ledger is purely an auditor. The author retains 100% creative control.
