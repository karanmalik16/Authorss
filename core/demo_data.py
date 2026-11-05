"""
Demo presets, sample story data, and walkthrough guide for Canon Ledger.
Includes the 3-chapter manuscript with 5 planted continuity errors + 1 false alarm for dismissal testing.
"""

from typing import List, Dict

DEMO_CHAPTERS = [
    {
        "id": 1,
        "title": "Chapter 1: The Midnight Crypt",
        "file_path": "sample_manuscript/chapter_1.md"
    },
    {
        "id": 2,
        "title": "Chapter 2: Council of Whispers",
        "file_path": "sample_manuscript/chapter_2.md"
    },
    {
        "id": 3,
        "title": "Chapter 3: The River Crossing",
        "file_path": "sample_manuscript/chapter_3.md"
    }
]

REAL_WORLD_EXAMPLES = [
    {
        "author": "J.K. Rowling",
        "book": "Harry Potter and the Goblet of Fire (Original Edition)",
        "error": "Priori Incantatem Wand Sequence",
        "details": "During the graveyard duel, Voldemort's wand disgorged victims in reverse order. James Potter emerged before Lily Potter, implying James died second, contradicting the canon established in Book 1 where James died first protecting his family.",
        "reader_impact": "Discovered by millions of readers; forced an erratum and reprint in subsequent editions."
    },
    {
        "author": "George R.R. Martin",
        "book": "A Song of Ice and Fire",
        "error": "Character Physical Attributes & Eye Shifts",
        "details": "Joffrey Baratheon and Renly Baratheon had shifts in eye color across chapters (green vs blue), and horse sexes famously switched mid-ride between A Game of Thrones and A Clash of Kings.",
        "reader_impact": "Noticed by avid fans on Westeros.org forums and catalogued as continuity bloopers."
    },
    {
        "author": "J.R.R. Tolkien",
        "book": "The Lord of the Rings",
        "error": "Lunar Phases and Travel Timelines",
        "details": "Tolkien had to meticulously chart lunar calendars and rewrite passages because different groups of characters experienced full moons on mismatched dates across Middle-earth.",
        "reader_impact": "Tolkien spent months recalculating astronomical timelines by hand in his private story bibles."
    }
]

DEMO_SCRIPT_STEPS = [
    {
        "step": 1,
        "time": "0:00 - 0:40",
        "title": "The Problem: Continuity Fatigue in Long Fiction",
        "script": "Human memory cannot hold 100,000 words across months of writing. Eye colors slip, travel times defy physics, world rules shatter, and dead or injured limbs suddenly act. Readers spot these immediately and punish authors in Amazon/Goodreads reviews. General AI tools try to rewrite prose and hallucinate; Canon Ledger is different: it acts as a silent Sentinel. It builds a living story bible and demands strict side-by-side citations for every flag—and it NEVER rewrites your prose."
    },
    {
        "step": 2,
        "time": "0:40 - 1:20",
        "title": "Ingestion & Living Story Bible Generation",
        "script": "Watch as Chapter 1 ('The Midnight Crypt') is ingested. Canon Ledger parses sentences, records characters (Lady Vivienne, Master Corvus), extracts their attributes (emerald-green eyes, right hand severed at Oakhaven), logs travel distances (Ashen Fortress = 3-day hard ride), magic rules (shadow-iron dissolves in running water), and secret knowledge (Archduke murder known only to Vaelen, Corvus, Vivienne)."
    },
    {
        "step": 3,
        "time": "1:20 - 2:10",
        "title": "Ingesting Chapter 2: Detecting Contradictions with Evidence",
        "script": "Now we upload Chapter 2 ('Council of Whispers'). Notice the instant alerts: Flag 1 shows Vivienne's eyes shifting from emerald-green to violet side-by-side with exact sentence quotes. Flag 2 flags Sir Justinian claiming a same-afternoon return from a 3-day ride. Flag 3 flags an Epistemic Leak: Lord Ronald blurting out the secret strangulation cord when he was never told!"
    },
    {
        "step": 4,
        "time": "2:10 - 2:40",
        "title": "Author in Control: Accept, Dismiss & Dismissal Memory",
        "script": "The author decides every fix. We 'Accept' the eye color contradiction to note for our revision. For a figurative false alarm or authorial intent, we click 'Dismiss'. Canon Ledger hashes the citation fingerprint so this exact dismissal is permanently remembered and will never nag the author again."
    },
    {
        "step": 5,
        "time": "2:40 - 3:00",
        "title": "Chapter 3: Physical & World Rule Violations, Export",
        "script": "Ingesting Chapter 3 flags Master Corvus gripping a broadsword with severed right fingers, and an assassin carrying shadow-iron through running water. We review the 'Who Knows This?' knowledge matrix and export the complete Story Bible as JSON or Markdown. The manuscript remains 100% untouched by AI generation—the author retains full creative sovereignty."
    }
]
