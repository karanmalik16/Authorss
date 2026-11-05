"""
Market references and competitor benchmarking for Canon Ledger.
Preliminary market research as of November 2026.
"""

from typing import List, Dict

BENCHMARK_META = {
    "as_of_date": "As of November 2026",
    "status_note": "Preliminary Market Research (Subject to Live Product Evaluation)"
}

COMPETITOR_TOOLS = [
    {
        "name": "Canon Ledger",
        "url": "",
        "display_name": "Canon Ledger (This Project)",
        "category": "Continuity Sentinel",
        "story_bible": "Living Bible (Auto-extracted from manuscript)",
        "auto_extraction": "Demo rules only",
        "contradiction_check": "Strict Side-by-Side Verifiable Quotes",
        "author_control": "100% Author Sovereignty (Never Rewrites Prose)",
        "target_audience": "Novelists, Series Authors, Developmental Editors",
        "edge_note": "Prototype: rules are tuned to the demo story; citation checks work on any text (.txt, .md, .docx); drops unverified flags; remembers dismissals permanently."
    },
    {
        "name": "Sudowrite",
        "url": "https://sudowrite.com",
        "docs_url": "https://docs.sudowrite.com",
        "display_name": "Sudowrite",
        "category": "AI Co-Writer",
        "story_bible": "Story Bible with character cards & universe lore",
        "auto_extraction": "Includes 'Import Novel' feature to auto-generate bible entries; primary mode is drafting",
        "contradiction_check": "Context injection for scene generation; not a forensic citation-based continuity auditor",
        "author_control": "Co-writer (Generates & rewrites prose)",
        "target_audience": "Fiction writers seeking drafting assistance",
        "edge_note": "Focuses on generative drafting and scene expansion rather than auditing existing prose."
    },
    {
        "name": "Novelcrafter",
        "url": "https://www.novelcrafter.com",
        "display_name": "Novelcrafter",
        "category": "AI Writing Studio",
        "story_bible": "The Codex / Series Codex with Progressions",
        "auto_extraction": "Detects entity mentions; allows lore sheets and series-level sharing",
        "contradiction_check": "AI Workshop chat queries & prompt context injection",
        "author_control": "Co-writer / Generation prompts",
        "target_audience": "Tech-savvy indie authors and series planners",
        "edge_note": "Offers progression tracking, but requires Codex curation and focuses primarily on drafting."
    },
    {
        "name": "Chronicle",
        "url": "https://www.producthunt.com/products/chronicle-13",
        "display_name": "Chronicle",
        "category": "Local Planning Tool",
        "story_bible": "Local story bible & relational timeline",
        "auto_extraction": "Describes automated story bible generation from text files",
        "contradiction_check": "Visual timeline & entity views; lacks automated contradiction citation checks",
        "author_control": "Manual / Local planner",
        "target_audience": "Writers wanting local-only offline organization",
        "edge_note": "Strong local privacy, but does not provide side-by-side contradiction detection with exact quotes."
    },
    {
        "name": "LoreKeep",
        "url": "https://apps.apple.com/app/id6791226620",
        "display_name": "LoreKeep",
        "category": "Mobile Worldbuilder",
        "story_bible": "Manual lore cards & relationships",
        "auto_extraction": "User creates entities manually in workspace",
        "contradiction_check": "AI Analyzer compares pasted scene against bible",
        "author_control": "Advisory feedback",
        "target_audience": "iPad / iOS fiction writers & TTRPG creators",
        "edge_note": "Platform-locked to iPadOS/iOS; requires manual bible entry before checking."
    },
    {
        "name": "LitMemo",
        "url": "https://www.litmemo.com",
        "display_name": "LitMemo",
        "category": "Project Management",
        "story_bible": "Wiki & character sheets",
        "auto_extraction": "Manual wiki creation",
        "contradiction_check": "AI flags timeline & past visit discrepancies",
        "author_control": "Advisory alert",
        "target_audience": "Novelist teams, webtoon writers, game masters",
        "edge_note": "Flags timeline slips, but relies on upfront manual note-taking."
    },
    {
        "name": "Galleys",
        "url": "https://galleys.ai",
        "display_name": "Galleys",
        "category": "AI Manuscript Editor",
        "story_bible": "Internal developmental ledger",
        "auto_extraction": "Full document scanning",
        "contradiction_check": "Structural continuity & prose repetition scans",
        "author_control": "Developmental report",
        "target_audience": "Full-length novel authors in post-draft revision",
        "edge_note": "Focuses on post-complete draft structural analysis rather than real-time chapter-by-chapter tracking."
    },
    {
        "name": "Plottr",
        "url": "https://plottr.com/series-bible-software/",
        "display_name": "Plottr",
        "category": "Visual Outliner",
        "story_bible": "Series Bible & Character Templates (Manual)",
        "auto_extraction": "None (Manual entry)",
        "contradiction_check": "None",
        "author_control": "Manual planner",
        "target_audience": "Series planners and outliners",
        "edge_note": "Visual timeline grids are great for pre-writing, but offer no automated continuity verification."
    },
    {
        "name": "Aeon Timeline",
        "url": "https://aeontimeline.com",
        "display_name": "Aeon Timeline",
        "category": "Timeline Database",
        "story_bible": "Relational Entity & Event Timeline",
        "auto_extraction": "Syncs with Scrivener/Ulysses; dates entered manually",
        "contradiction_check": "Calculates date math & age clashes from manual dates",
        "author_control": "Manual",
        "target_audience": "Complex multi-POV and multi-era novelists",
        "edge_note": "Industry benchmark for manual date calculation, but requires manual date entry for every scene."
    },
    {
        "name": "Campfire Write",
        "url": "https://www.campfirewriting.com",
        "display_name": "Campfire Write",
        "category": "Worldbuilding Suite",
        "story_bible": "Modular Character Webs, Maps, Timelines",
        "auto_extraction": "None (Manual entry)",
        "contradiction_check": "None",
        "author_control": "Manual",
        "target_audience": "Fantasy & Sci-Fi worldbuilders",
        "edge_note": "Deep modular lore sheets, but maintaining them across 100k words becomes high friction."
    },
    {
        "name": "CanonGuard AI",
        "url": "https://www.turbostarter.dev/ideas/other/canon-guard-ai",
        "display_name": "CanonGuard AI",
        "category": "Product Concept",
        "story_bible": "Conceptual Automated Bible",
        "auto_extraction": "Proposed in concept",
        "contradiction_check": "Proposed plot-hole & character scan",
        "author_control": "Advisory",
        "target_audience": "Proposed indie authors",
        "edge_note": "Unreleased incubator concept; highlights market appetite for automated continuity checkers."
    }
]

MARKET_DEMAND_EVIDENCE = [
    {
        "source": "Sudowrite Community Feature Request #63877",
        "source_name": "Sudowrite",
        "url": "https://feedback.sudowrite.com/feedback/63877",
        "title": "Need Auto-Scan of Previous Stories to Build Series Bibles",
        "quote": "I'd like sudowrite to be able to scan my previous stories, to make bibles for series.",
        "is_paraphrase": False,
        "significance": "Validates the primary value proposition of Canon Ledger's automated extraction engine."
    },
    {
        "source": "Novela Publishing Analysis",
        "source_name": "Novela",
        "url": "https://novela.so/en/blog/story-bible-that-gets-used",
        "title": "The Story Bible That Gets Used",
        "quote": "Most story bibles get created, then ignored.",
        "is_paraphrase": False,
        "significance": "Highlights why manual tools (Plottr, Campfire, Notion) fail authors in multi-book series."
    },
    {
        "source": "Influence AI Continuity Analysis",
        "source_name": "Influence AI",
        "url": "https://www.inkfluenceai.com/blog/best-ai-novel-continuity-checking-2026",
        "title": "Best AI Novel Continuity Checking 2026",
        "quote": "Continuity depends on your manual note-taking. The Story Bible is not populated automatically from your text.",
        "is_paraphrase": True,
        "significance": "Directly defines Canon Ledger's competitive moat: zero manual setup, strict quote citations, and zero prose rewriting."
    }
]
