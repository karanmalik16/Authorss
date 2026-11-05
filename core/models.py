"""
Data models and JSON schema definitions for Canon Ledger.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

@dataclass
class Citation:
    chapter_id: int
    chapter_title: str
    sentence_num: int
    quote: str
    attribute_key: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Entity:
    id: str
    name: str
    category: str  # 'character', 'location', 'artifact', 'faction'
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_chapter_id: int = 1
    citations: List[dict] = field(default_factory=list)
    notes: str = ""

    def update_attributes(self, new_attributes: Dict[str, Any]):
        """
        Keeps the first established value for each attribute.
        A later, different value creates a flag rather than overwriting stored value.
        """
        for k, v in new_attributes.items():
            if k not in self.attributes or not self.attributes[k]:
                self.attributes[k] = v

    def add_citation(self, citation: dict):
        """
        Adds a citation only if not duplicate (same quote, chapter, and sentence).
        Omits contradictory citations that conflict with established canon attributes.
        """
        # If this citation asserts an attribute value that contradicts established canon, ignore it
        attr_key = citation.get('attribute_key')
        attr_val = citation.get('value')
        if attr_key and attr_key in self.attributes and attr_val:
            established_val = str(self.attributes[attr_key]).lower()
            incoming_val = str(attr_val).lower()
            if incoming_val != established_val and incoming_val not in established_val and established_val not in incoming_val:
                return

        q = (citation.get('quote') or '').strip().lower()
        c = citation.get('chapter_id')
        s = citation.get('sentence_num')
        for existing in self.citations:
            eq = (existing.get('quote') or '').strip().lower()
            ec = existing.get('chapter_id')
            es = existing.get('sentence_num')
            if q == eq and c == ec and s == es:
                return  # Duplicate citation
        self.citations.append(citation)

    def add_citations(self, citations: List[dict]):
        for cit in citations:
            self.add_citation(cit)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class WorldRule:
    id: str
    name: str
    domain: str  # 'magic', 'physics', 'geography', 'biology', 'social'
    statement: str
    citations: List[dict] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class TimelineEvent:
    id: str
    chapter_id: int
    chapter_title: str
    sentence_num: int
    timestamp_desc: str  # e.g., "Day 1, Midnight", "Two weeks after the Council"
    event_description: str
    participants: List[str] = field(default_factory=list)
    location: str = ""
    quote: str = ""
    order_index: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class KnowledgeItem:
    id: str
    fact_summary: str
    is_secret: bool
    first_chapter_id: int
    source_quote: str
    known_by: List[str] = field(default_factory=list)
    unknown_to: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class ContradictionFlag:
    id: str
    fingerprint: str
    title: str
    category: str  # 'character_trait', 'timeline', 'physical_state', 'world_rule', 'epistemic_leak', 'location_geography'
    severity: str  # 'high', 'medium', 'low'
    earlier_chapter_id: int
    earlier_chapter_title: str
    earlier_sentence_num: int
    earlier_quote: str
    new_chapter_id: int
    new_chapter_title: str
    new_sentence_num: int
    new_quote: str
    explanation: str
    suggested_fix: str
    status: str = "pending"  # 'pending', 'accepted', 'dismissed', 'fixed'
    author_note: str = ""

    @staticmethod
    def generate_fingerprint(earlier_quote: str, new_quote: str, category: str) -> str:
        """Deterministic fingerprint so dismissals are remembered across re-scans."""
        raw = f"{category.strip().lower()}|{earlier_quote.strip().lower()}|{new_quote.strip().lower()}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Chapter:
    id: int
    book_id: str
    title: str
    order_index: int
    raw_text: str
    word_count: int = 0
    sentences: List[dict] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

def format_chapter_display(cid: int, raw_title: str) -> str:
    """Formats chapter title without redundant 'Ch 1: Chapter 1: ...' prefixes."""
    import re
    clean = re.sub(r'^[#\s*_-]+', '', raw_title or '').strip()
    clean = re.sub(rf'^Chapter\s+{cid}\s*[:\-–—]\s*', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^Chapter\s+\d+\s*[:\-–—]?\s*', '', clean, flags=re.IGNORECASE)
    if clean:
        return f"Ch. {cid} · {clean}"
    return f"Chapter {cid}"

class StoryBible:
    """
    Central repository for all canon lore, facts, rules, timeline events, and flags.
    """
    def __init__(self, title: str = "My Novel Series"):
        self.series_title = title
        self.active_book = "Book 1"
        self.books = ["Book 1"]
        self.chapters: Dict[int, Chapter] = {}
        self.entities: Dict[str, Entity] = {}
        self.world_rules: Dict[str, WorldRule] = {}
        self.timeline_events: List[TimelineEvent] = []
        self.knowledge_items: List[KnowledgeItem] = []
        self.flags: List[ContradictionFlag] = []
        self.dismissed_fingerprints: set = set()

    def add_knowledge_item(self, item: KnowledgeItem):
        """Deduplicates knowledge items by ID, preserving earliest discovery chapter and quote."""
        for idx, existing in enumerate(self.knowledge_items):
            existing_id = existing.id if hasattr(existing, 'id') else (existing.get('id') if isinstance(existing, dict) else None)
            if existing_id == item.id:
                existing_chap = existing.first_chapter_id if hasattr(existing, 'first_chapter_id') else existing.get('first_chapter_id', 999)
                item_chap = item.first_chapter_id if hasattr(item, 'first_chapter_id') else item.get('first_chapter_id', 999)
                if existing_chap <= item_chap:
                    return
                self.knowledge_items[idx] = item
                return
        self.knowledge_items.append(item)

    def get_or_create_entity(self, name: str, category: str = 'character', entity_id: Optional[str] = None) -> Entity:
        if not entity_id:
            import re
            clean = re.sub(r'^(lady|lord|master|captain|sir|count|countess|king|queen|duke|archduke|prince|princess)\s+', '', name.strip().lower())
            entity_id = clean.replace(" ", "_")
        if entity_id not in self.entities:
            self.entities[entity_id] = Entity(
                id=entity_id,
                name=name.strip(),
                category=category
            )
        return self.entities[entity_id]

    def add_or_update_entity(self, incoming: Entity) -> Entity:
        """
        Merges an incoming extracted entity into the Story Bible.
        Preserves the first established value for each attribute (does not overwrite).
        Removes duplicate citations (same quote, chapter, and sentence).
        """
        target = self.get_or_create_entity(incoming.name, incoming.category, entity_id=incoming.id)
        if incoming.aliases:
            for alias in incoming.aliases:
                if alias not in target.aliases:
                    target.aliases.append(alias)
        target.update_attributes(incoming.attributes)
        target.add_citations(incoming.citations)
        if incoming.first_chapter_id and (target.first_chapter_id is None or incoming.first_chapter_id < target.first_chapter_id):
            target.first_chapter_id = incoming.first_chapter_id
        if incoming.notes and not target.notes:
            target.notes = incoming.notes
        return target

    def add_flag(self, flag: ContradictionFlag) -> bool:
        """
        Adds a flag if its fingerprint has not been dismissed.
        Returns True if added, False if suppressed.
        """
        if flag.fingerprint in self.dismissed_fingerprints:
            flag.status = 'dismissed'
            if not any(existing.fingerprint == flag.fingerprint for existing in self.flags):
                self.flags.append(flag)
            return True
            
        # Avoid exact duplicate flags in current list
        for existing in self.flags:
            if existing.fingerprint == flag.fingerprint:
                return False
                
        self.flags.append(flag)
        return True

    def dismiss_flag(self, flag_id: str, note: str = "") -> bool:
        for f in self.flags:
            if f.id == flag_id:
                f.status = 'dismissed'
                f.author_note = note
                self.dismissed_fingerprints.add(f.fingerprint)
                return True
        return False

    def accept_flag(self, flag_id: str, note: str = "") -> bool:
        for f in self.flags:
            if f.id == flag_id:
                f.status = 'accepted'
                f.author_note = note
                return True
        return False

    def fix_flag(self, flag_id: str, note: str = "") -> bool:
        for f in self.flags:
            if f.id == flag_id:
                f.status = 'fixed'
                f.author_note = note
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "series_title": self.series_title,
            "active_book": self.active_book,
            "books": self.books,
            "chapters": [c.to_dict() for c in sorted(self.chapters.values(), key=lambda x: x.order_index)],
            "entities": [e.to_dict() for e in self.entities.values()],
            "world_rules": [r.to_dict() for r in self.world_rules.values()],
            "timeline_events": [t.to_dict() for t in self.timeline_events],
            "knowledge_items": [k.to_dict() if hasattr(k, 'to_dict') else k for k in self.knowledge_items],
            "flags": [f.to_dict() for f in self.flags],
            "dismissed_fingerprints": list(self.dismissed_fingerprints)
        }

    def export_as_markdown(self) -> str:
        lines = []
        lines.append(f"# Story Bible: {self.series_title}")
        lines.append(f"*Exported by Canon Ledger*\n")
        
        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("- [Characters](#characters)")
        lines.append("- [Locations](#locations)")
        lines.append("- [World Rules & Lore](#world-rules--lore)")
        lines.append("- [Timeline](#timeline)")
        lines.append("- [Who Knows What (Epistemic State)](#who-knows-what)")
        lines.append("- [Continuity Audit Flags](#continuity-audit-flags)\n")
        
        # Characters
        lines.append("## Characters\n")
        characters = [e for e in self.entities.values() if e.category == 'character']
        if not characters:
            lines.append("*No characters recorded yet.*\n")
        for char in sorted(characters, key=lambda c: c.name):
            lines.append(f"### {char.name}")
            if char.aliases:
                lines.append(f"- **Aliases / Titles:** {', '.join(char.aliases)}")
            lines.append(f"- **First Appeared:** Chapter {char.first_chapter_id}")
            if char.attributes:
                lines.append("- **Known Attributes:**")
                for k, v in char.attributes.items():
                    key_fmt = k.replace('_', ' ').capitalize()
                    lines.append(f"  - **{key_fmt}:** {v}")
            if char.citations:
                lines.append("- **Key Citations:**")
                for cit in char.citations[:5]:  # top 5
                    lines.append(f"  - *Ch {cit.get('chapter_id')}, Sent {cit.get('sentence_num')}:* \"{cit.get('quote')}\"")
            lines.append("")

        # Locations
        lines.append("## Locations\n")
        locations = [e for e in self.entities.values() if e.category == 'location']
        if not locations:
            lines.append("*No locations recorded yet.*\n")
        for loc in sorted(locations, key=lambda l: l.name):
            lines.append(f"### {loc.name}")
            if loc.attributes:
                for k, v in loc.attributes.items():
                    lines.append(f"- **{k.capitalize()}:** {v}")
            if loc.citations:
                lines.append("- **Citations:**")
                for cit in loc.citations[:3]:
                    lines.append(f"  - *Ch {cit.get('chapter_id')}:* \"{cit.get('quote')}\"")
            lines.append("")

        # World Rules
        lines.append("## World Rules & Lore\n")
        if not self.world_rules:
            lines.append("*No world rules recorded yet.*\n")
        for rule in self.world_rules.values():
            lines.append(f"### {rule.name} *({rule.domain.capitalize()})*")
            lines.append(f"> \"{rule.statement}\"\n")
            if rule.citations:
                lines.append(f"- *Source:* Ch {rule.citations[0].get('chapter_id')}: \"{rule.citations[0].get('quote')}\"")
            lines.append("")

        # Timeline
        lines.append("## Timeline\n")
        if not self.timeline_events:
            lines.append("*No timeline events recorded yet.*\n")
        for ev in sorted(self.timeline_events, key=lambda x: (x.chapter_id, x.sentence_num)):
            lines.append(f"- **[Ch {ev.chapter_id} • {ev.timestamp_desc}]** {ev.event_description}")
            if ev.quote and ev.quote.strip().lower() != ev.event_description.strip().lower():
                lines.append(f"  > *\"{ev.quote}\"*")
        lines.append("")

        # Who Knows What
        lines.append("## Who Knows What\n")
        if not self.knowledge_items:
            lines.append("*No secret facts or knowledge tracks recorded.*\n")
        for item in (self.knowledge_items.values() if isinstance(self.knowledge_items, dict) else self.knowledge_items):
            item_data = item if isinstance(item, dict) else item.to_dict()
            lines.append(f"### Fact: {item_data.get('fact_summary')}")
            lines.append(f"- **Revealed In:** Chapter {item_data.get('first_chapter_id')}")
            lines.append(f"- **Characters In The Know:** {', '.join(item_data.get('known_by', [])) or 'None'}")
            lines.append(f"- **Kept In The Dark:** {', '.join(item_data.get('unknown_to', [])) or 'None'}")
            lines.append(f"- **Source Evidence:** \"{item_data.get('source_quote')}\"\n")

        # Continuity Flags
        lines.append("## Continuity Audit Flags\n")
        if not self.flags:
            lines.append("✨ *No continuity errors detected.*\n")
        else:
            for flag in self.flags:
                status_icon = "⚠️" if flag.status == 'pending' else ("✅" if flag.status == 'fixed' else "🚫")
                lines.append(f"### {status_icon} [{flag.severity.upper()}] {flag.title} ({flag.status.upper()})")
                lines.append(f"**Explanation:** {flag.explanation}\n")
                lines.append(f"| Earlier Evidence (Ch {flag.earlier_chapter_id}: {flag.earlier_chapter_title}, Sent #{flag.earlier_sentence_num}) | Current Conflict (Ch {flag.new_chapter_id}: {flag.new_chapter_title}, Sent #{flag.new_sentence_num}) |")
                lines.append("| :--- | :--- |")
                lines.append(f"| \"{flag.earlier_quote}\" | \"{flag.new_quote}\" |")
                lines.append(f"\n- **Author Fix Suggestion:** {flag.suggested_fix}")
                if flag.author_note:
                    lines.append(f"- **Author Note:** {flag.author_note}")
                lines.append("")

        return "\n".join(lines)
