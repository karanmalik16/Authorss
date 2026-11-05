# CANON LEDGER
### *The Living Story Bible & Continuity Sentinel for Novelists*

> **"Canon Ledger reads the author's manuscript, builds a living story bible, and flags contradictions with links to the exact earlier passages. It NEVER writes or rewrites prose. The author decides every fix."**

---

## 1. Problem Statement

Authors writing 80,000 to 100,000+ word novels or multi-book fantasy and sci-fi series face an immense cognitive burden:
* **Physical traits drift:** Characters change eye color, hair, or handedness across chapters (e.g. emerald green in Chapter 1 vs violet in Chapter 2).
* **Physical impossibilities:** Severed limbs or injured hands suddenly grip greatswords with both hands.
* **Travel duration violations:** A journey established as a 3-day hard mountain trek is completed in a single afternoon.
* **World rules & magical laws break:** Enchanted metals that dissolve in running water are wielded while wading through a river.
* **Epistemic leaks ("Who knows what and when"):** Characters speak about confidential secrets before they were ever told.
* **AI co-writers aggravate the problem:** Generative AI tools hallucinate, forget earlier chapters between chat sessions, and aggressively try to rewrite the author's voice.

**Readers spot these errors immediately and punish them in reviews.** Canon Ledger acts as a silent continuity sentinel that works on existing manuscripts, demands verifiable citations for every alert, preserves dismissals, and protects author sovereignty.

---

## 2. Core Architecture & Philosophy

```
[Manuscript Chapters: .txt / .md / .docx / paste]
                      │
                      ▼
        [Chapter & Sentence Tokenizer]
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
[Contradiction Checker]     [Extraction Engine]
  • Character Attributes     • Characters & Traits
  • Physical States          • Locations & Travel Times
  • Travel / Geography       • World Rules & Lore
  • Magic Constraints        • Timeline Milestones
  • Epistemic Knowledge      • Secret Knowledge Tracker
  • Strict Citation Check               │
        │                               │
        ▼                               ▼
[Side-by-Side Flag Evidence]  [Living Story Bible]
  • Earlier Sentence Quote      • Exportable JSON / Markdown
  • Current Sentence Quote      • Persistent Dismissals
  • Author Action (Accept/Fix)  • Author Sovereignty Guarantee
```

* **Zero-Hallucination Citation Verification:** Every flag *must* have both the earlier quote and the new quote verifiably present in the manuscript. If a quote cannot be verified in the source text, the flag is automatically dropped.
* **Dismissal Memory:** When an author dismisses a false alarm or intentional figurative phrase, Canon Ledger stores a deterministic hash fingerprint (`sha256(category + earlier_quote + new_quote)`). The false alarm will never reappear on future scans.
* **No Prose Generation:** Canon Ledger never touches the author's draft without explicit author confirmation.

---

## 3. Competitive Landscape & Reference Analysis
*(Preliminary Market Research as of November 2026 · Live Product Evaluation Pending)*

Canon Ledger fills a structural gap between generative AI writing tools and traditional manual planning databases:

| Tool & Reference URL | Category | Story Bible Mode | Auto-Extraction | Contradiction Checking | Author Control Philosophy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Canon Ledger**<br>*(This Project)* | **Continuity Sentinel** | **Living Bible (Auto-extracted from manuscript)** | **Full** (Chapter & sentence citations) | **Strict Side-by-Side Verifiable Quotes** | **100% Author Sovereignty** (Never rewrites prose) |
| **Sudowrite**<br>[sudowrite.com](https://sudowrite.com) | AI Co-Writer | Manual Story Bible cards & universe lore | Includes "Import Novel" auto-generation; primary mode is drafting | Context injection for drafting; no forensic citation audit | Co-Writer (Generates & rewrites text) |
| **Novelcrafter**<br>[novelcrafter.com](https://www.novelcrafter.com) | AI Writing Studio | The Codex & Series Codex with Progressions | Detects entity mentions; allows lore sheets and series sharing | AI Chat queries & prompt context injection | Co-Writer / Prompt assistant |
| **Chronicle**<br>[producthunt](https://www.producthunt.com/products/chronicle-13) | Local Planning Tool | Local story bible & relational timeline | Describes automated story bible generation from text files | Visual timeline & entity views; lacks automated contradiction checks | Manual / Local planner |
| **LoreKeep**<br>[apple.com](https://apps.apple.com/app/id6791226620) | Mobile Worldbuilder | Manual lore cards & relationships | User creates entities manually in workspace | AI Analyzer flags plot/character contradictions against bible | Advisory feedback |
| **LitMemo**<br>[litmemo.com](https://www.litmemo.com) | Creative Project Tool | Manual wiki & character sheets | Manual wiki creation | AI flags timeline & past visit discrepancies | Advisory alert |
| **Galleys**<br>[galleys.ai](https://galleys.ai) | AI Manuscript Editor | Internal developmental ledger | Full document scan | Full-manuscript developmental audit & repetition scans | Developmental report |
| **Plottr**<br>[plottr.com](https://plottr.com/series-bible-software/) | Visual Outliner | Visual Series Bible (Manual) | None (Manual entry) | None | Manual planner |
| **Aeon Timeline**<br>[aeontimeline.com](https://aeontimeline.com) | Timeline Database | Relational event & entity database | Syncs with Scrivener/Ulysses; dates entered manually | Calculates mathematical date & age clashes from manual dates | Manual planner |
| **Campfire Write**<br>[campfirewriting.com](https://www.campfirewriting.com) | Worldbuilding Suite | Modular character webs & maps | None (Manual entry) | None | Manual planner |
| **CanonGuard AI**<br>[turbostarter.dev](https://www.turbostarter.dev/ideas/other/canon-guard-ai) | Product Concept | Proposed automated bible | Conceptual | Proposed plot-hole & character scan | Advisory |

### Market Demand Evidence:
* **Sudowrite Request [#63877](https://feedback.sudowrite.com/feedback/63877):** Writers explicitly plead for automated scanning of past books to build series bibles because manual entry causes fatigue.
* **Novela Publishing Study (["The Story Bible That Gets Used"](https://novela.so/en/blog/story-bible-that-gets-used)):** Shows manual story bibles get abandoned by authors because maintaining them is high-friction.
* **Inkfluence AI 2026 Analysis (["Best AI Novel Continuity Checking"](https://www.inkfluenceai.com/blog/best-ai-novel-continuity-checking-2026)):** Outlines the necessity of automatic extraction from existing manuscripts.

*See [docs/COMPETITIVE_ANALYSIS.md](file:///c:/Users/KARON/OneDrive/3d/docs/COMPETITIVE_ANALYSIS.md) for full detailed evaluation.*

---

## 4. Demo Features

### Must-Have (MVP):
1. **Chapter Ingestion in Order:** Upload `.txt`, `.md`, `.docx`, or paste text directly.
2. **Automatic Extraction:** Entities (characters, locations), attributes (eyes, injuries, handedness), travel times, world rules, and timeline events tied to chapter and sentence numbers.
3. **Contradiction Sentinel:** Compares new chapters against the established bible, generating side-by-side evidence with highlighted earlier and current passages.
4. **Author Decision System:** Accept, Dismiss, or Fix flags. Dismissals are permanently remembered.
5. **Editable Story Bible:** View and edit characters, places, and rules with clickable citation references back to manuscript sentences.
6. **Export:** Export Story Bible as Markdown or JSON, and export full Contradiction Audit Reports.

### Nice-to-Have (Included in Canon Ledger):
* **"Who Knows This?" Matrix:** Interactive table mapping secret facts against characters, highlighting who knows what, who is in the dark, and catching unauthorized leaks.
* **Chronological Timeline View:** Narrative timeline cards linking extracted events, relative timestamps, and chapter references.
* **Dual Interface:** Full-stack responsive Web App and zero-dependency terminal CLI.

---

## 4. Quickstart: Running the Application

### Option A: Launch the Web UI
```bash
# Install dependencies (Flask standard dependencies)
pip install -r requirements.txt

# Run the web server
python app.py
```
Open your browser to: **`http://127.0.0.1:5000`**

Click **"✨ Load Demo Story"** to immediately load the 3-chapter manuscript with 5 planted errors!

---

### Option B: Run the CLI Auditor
```bash
# Run the built-in demo audit:
python cli.py --demo

# Run audit on a folder of chapter files and export reports:
python cli.py --dir sample_manuscript/ --export-report audit_report.md --export-bible story_bible.json
```

---

### Option C: Run the Test Suite
```bash
python -m unittest discover tests
```
*Executes all 13 unit and integration tests verifying sentence splitting, extraction, contradiction checking, dismissal memory, API endpoints, and exports.*

---

## 5. The 3-Minute Demo Script

| Time | Step | Action | What to Say / Demonstrate |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:40** | **The Problem** | Click **"🎙️ Demo Script"** modal | *"Authors cannot hold 100,000 words in memory. Published books by J.K. Rowling (Priori Incantatem order slip), George R.R. Martin (eye color & horse gender shifts), and Tolkien suffered continuity fatigue. Canon Ledger solves this as a sentinel—it never rewrites prose."* |
| **0:40 - 1:15** | **Chapter 1 Ingestion** | Click **"✨ Load Demo Story"** | *"Chapter 1 establishes baseline canon: Lady Vivienne's emerald-green eyes, Master Corvus's right hand severed at Oakhaven, the 3-day ride to Ashen Fortress, shadow-iron dissolving in running water, and the secret strangulation cord known only to 3 people."* |
| **1:15 - 2:05** | **Chapter 2 Audit** | Switch to **Continuity Sentinel** tab | *"In Chapter 2, watch three instant flags trigger with side-by-side citations: (1) Vivienne's eyes shifting to violet, (2) Sir Justinian returning in an afternoon from a 3-day ride, and (3) an Epistemic Leak: Lord Ronald blurting out the classified murder method."* |
| **2:05 - 2:35** | **Author Control & Dismissal** | Click **"Accept"** on Flag 1, **"Dismiss"** on figurative flag | *"The author decides every fix. We accept the eye color error. For a poetic phrase, we click 'Dismiss'—Canon Ledger stores its fingerprint so this false alarm never nags us again."* |
| **2:35 - 3:00** | **Chapter 3 & Export** | Review **"Who Knows This?"** tab & Click **"Export"** | *"In Chapter 3, Corvus gripping a sword with severed right fingers and shadow-iron in running water are caught. We inspect the 'Who Knows This?' knowledge matrix and export the Story Bible as Markdown or JSON."* |

---

## 6. Managing Risks

1. **False Positives:** Addressed via mandatory quote verification (unverified flags are dropped) and deterministic dismissal fingerprints that respect author intent.
2. **Long Manuscripts:** Chapter-by-chapter ingestion updates the story bible iteratively, avoiding prompt token exhaustion or massive context loss.
3. **Scope Discipline:** Core focus remains on 100% reliable contradiction citations and total author sovereignty over story prose.
