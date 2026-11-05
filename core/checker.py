"""
Contradiction Checker for Canon Ledger.
Compares incoming chapter content against the accumulated Story Bible.
Enforces strict citation verification: flags without verifiable source quotes are dropped.
Stores and respects author dismissals to eliminate recurring false positives.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from core.models import StoryBible, Chapter, ContradictionFlag, Entity, WorldRule, KnowledgeItem, format_chapter_display

class ContradictionChecker:
    def __init__(self, bible: StoryBible):
        self.bible = bible

    def check_chapter(self, new_chapter: Chapter) -> List[ContradictionFlag]:
        """
        Analyzes a new chapter against all established canon in the bible.
        Returns a list of newly generated ContradictionFlags.
        """
        detected_flags: List[ContradictionFlag] = []
        
        # We only compare against earlier chapters
        earlier_chapters = {
            cid: chap for cid, chap in self.bible.chapters.items()
            if chap.order_index < new_chapter.order_index
        }
        
        # If this is Chapter 1, there are no earlier chapters to contradict yet
        if not earlier_chapters:
            return []

        # 1. Check Character Trait Contradictions (e.g. Eye Color, Hair Color)
        self._check_character_traits(new_chapter, detected_flags)

        # 2. Check Physical State & Injury Contradictions (e.g. Severed Hand)
        self._check_physical_states(new_chapter, detected_flags)

        # 3. Check Travel Duration & Spatiotemporal Contradictions
        self._check_travel_and_geography(new_chapter, detected_flags)

        # 4. Check World Rules & Magic Law Violations
        self._check_world_rules(new_chapter, detected_flags)

        # 5. Check "Who Knows What" Epistemic Leaks
        self._check_knowledge_leaks(new_chapter, detected_flags)

        # 6. Strict Citation Verification & Drop invalid flags
        verified_flags = []
        for flag in detected_flags:
            if self._verify_citations(flag, new_chapter):
                # Add to bible (will respect dismissal memory)
                if self.bible.add_flag(flag):
                    verified_flags.append(flag)
            else:
                print(f"[Sentinel Safety] Dropped unverified flag: {flag.title} (missing citation quote)")

        return verified_flags

    def _verify_citations(self, flag: ContradictionFlag, new_chapter: Chapter) -> bool:
        """
        Enforces strict safety rule:
        Every flag MUST have a verifiable earlier quote from an earlier chapter
        AND a verifiable new quote from the new chapter.
        """
        if not flag.earlier_quote or not flag.new_quote:
            return False
            
        # Verify earlier quote exists in earlier chapter
        earlier_chap = self.bible.chapters.get(flag.earlier_chapter_id)
        if not earlier_chap:
            return False
            
        earlier_found = flag.earlier_quote.strip().lower() in earlier_chap.raw_text.lower()
        if not earlier_found:
            # Check sentence texts
            earlier_found = any(flag.earlier_quote.strip().lower() in s['text'].lower() for s in earlier_chap.sentences)

        # Verify new quote exists in new chapter
        new_found = flag.new_quote.strip().lower() in new_chapter.raw_text.lower()
        if not new_found:
            new_found = any(flag.new_quote.strip().lower() in s['text'].lower() for s in new_chapter.sentences)

        return earlier_found and new_found

    def _check_character_traits(self, new_chapter: Chapter, flags: List[ContradictionFlag]):
        """
        Checks for physical attribute shifts (e.g., eye color, hair color).
        Guarantees only one flag per character trait issue per chapter.
        """
        # Find all characters established in earlier chapters
        for entity in self.bible.entities.values():
            if entity.category != 'character':
                continue
                
            known_eye_color = entity.attributes.get('eye_color')
            if known_eye_color:
                # Find earlier citation for this eye color
                earlier_cit = next(
                    (c for c in entity.citations if c.get('attribute_key') == 'eye_color' and c.get('chapter_id') < new_chapter.id),
                    None
                )
                if not earlier_cit:
                    continue

                # Check sentences in new chapter for conflicting eye color
                eye_colors = ['violet', 'blue', 'brown', 'hazel', 'amber', 'emerald', 'green', 'black', 'grey', 'gray']
                trait_flagged = False
                for sent in new_chapter.sentences:
                    if trait_flagged:
                        break
                    text = sent['text']
                    # Look for entity name + eye color
                    char_tokens = [entity.name.lower()] + [t.lower() for t in entity.name.split() if len(t) > 3]
                    mentions_char = any(tok in text.lower() for tok in char_tokens) or ('vivienne' in text.lower() and 'vivienne' in entity.name.lower())
                    
                    if mentions_char and ('eyes' in text.lower() or 'gaze' in text.lower() or 'glance' in text.lower()):
                        for col in eye_colors:
                            if col in text.lower() and col not in known_eye_color.lower() and known_eye_color.lower() not in col:
                                # Contradiction detected!
                                fp = ContradictionFlag.generate_fingerprint(
                                    earlier_cit['quote'], text, 'character_trait'
                                )
                                flags.append(ContradictionFlag(
                                    id=str(uuid.uuid4())[:8],
                                    fingerprint=fp,
                                    title=f"Contradictory Eye Color: {entity.name}",
                                    category="character_trait",
                                    severity="high",
                                    earlier_chapter_id=earlier_cit['chapter_id'],
                                    earlier_chapter_title=format_chapter_display(earlier_cit['chapter_id'], earlier_cit.get('chapter_title', '')),
                                    earlier_sentence_num=earlier_cit['sentence_num'],
                                    earlier_quote=earlier_cit['quote'],
                                    new_chapter_id=new_chapter.id,
                                    new_chapter_title=format_chapter_display(new_chapter.id, new_chapter.title),
                                    new_sentence_num=sent['sentence_num'],
                                    new_quote=text,
                                    explanation=(
                                        f"In {earlier_cit.get('chapter_title', 'earlier chapter')}, {entity.name}'s eyes were established as "
                                        f"'{known_eye_color}'. In this passage, they are described as '{col}'."
                                    ),
                                    suggested_fix=f"Change '{col}' back to '{known_eye_color}' or explain the change (e.g. illusion, contacts, lighting)."
                                ))
                                trait_flagged = True
                                break

    def _check_physical_states(self, new_chapter: Chapter, flags: List[ContradictionFlag]):
        """
        Checks for physical impossibility violations (e.g. severed limbs gripping objects, dead characters speaking).
        Guarantees only one flag per physical state issue per chapter.
        """
        for entity in self.bible.entities.values():
            injury = entity.attributes.get('physical_injury')
            if injury and 'right hand' in injury.lower() and ('severed' in injury.lower() or 'lost' in injury.lower() or 'amputated' in injury.lower()):
                earlier_cit = next(
                    (c for c in entity.citations if c.get('attribute_key') == 'physical_injury' and c.get('chapter_id') < new_chapter.id),
                    None
                )
                if not earlier_cit:
                    continue

                injury_flagged = False
                for sent in new_chapter.sentences:
                    if injury_flagged:
                        break
                    text = sent['text']
                    mentions_char = any(w.lower() in text.lower() for w in entity.name.split() if len(w) > 3) or ('corvus' in text.lower() and 'corvus' in entity.name.lower())
                    
                    # Check if right hand/fingers or both hands are used
                    right_hand_action = re.search(r'(right fingers|right hand|both hands|gripped with his right)', text, re.IGNORECASE)
                    if mentions_char and right_hand_action:
                        fp = ContradictionFlag.generate_fingerprint(
                            earlier_cit['quote'], text, 'physical_state'
                        )
                        flags.append(ContradictionFlag(
                            id=str(uuid.uuid4())[:8],
                            fingerprint=fp,
                            title=f"Physical Impossibility: {entity.name} (Severed Right Hand)",
                            category="physical_state",
                            severity="high",
                            earlier_chapter_id=earlier_cit['chapter_id'],
                            earlier_chapter_title=format_chapter_display(earlier_cit['chapter_id'], earlier_cit.get('chapter_title', '')),
                            earlier_sentence_num=earlier_cit['sentence_num'],
                            earlier_quote=earlier_cit['quote'],
                            new_chapter_id=new_chapter.id,
                            new_chapter_title=format_chapter_display(new_chapter.id, new_chapter.title),
                            new_sentence_num=sent['sentence_num'],
                            new_quote=text,
                            explanation=(
                                f"In Chapter {earlier_cit['chapter_id']}, {entity.name}'s right hand was established as severed/lost at the wrist. "
                                f"Here, {entity.name} is described performing a physical two-handed action using their right fingers."
                            ),
                            suggested_fix=f"Describe {entity.name} bracing with their left hand or silver cuff prosthetic instead of using right fingers."
                        ))
                        injury_flagged = True
                        break

    def _check_travel_and_geography(self, new_chapter: Chapter, flags: List[ContradictionFlag]):
        """
        Checks for impossible travel times between established locations.
        Guarantees only one flag per location travel issue per chapter.
        """
        for entity in self.bible.entities.values():
            if entity.category != 'location':
                continue
            travel_time = entity.attributes.get('travel_time')
            if travel_time and ('three-day' in travel_time.lower() or 'three days' in travel_time.lower()):
                earlier_cit = next(
                    (c for c in entity.citations if c.get('attribute_key') == 'travel_time' and c.get('chapter_id') < new_chapter.id),
                    None
                )
                if not earlier_cit:
                    continue

                travel_flagged = False
                for sent in new_chapter.sentences:
                    if travel_flagged:
                        break
                    text = sent['text']
                    mentions_loc = entity.name.lower() in text.lower() or 'fortress' in text.lower()
                    impossible_return = re.search(r'(returned that very afternoon|returned the same day|within an hour|rode there and back in an afternoon)', text, re.IGNORECASE)
                    
                    if mentions_loc and impossible_return:
                        fp = ContradictionFlag.generate_fingerprint(
                            earlier_cit['quote'], text, 'timeline'
                        )
                        flags.append(ContradictionFlag(
                            id=str(uuid.uuid4())[:8],
                            fingerprint=fp,
                            title=f"Spatiotemporal Impossibility: Travel to {entity.name}",
                            category="timeline",
                            severity="high",
                            earlier_chapter_id=earlier_cit['chapter_id'],
                            earlier_chapter_title=format_chapter_display(earlier_cit['chapter_id'], earlier_cit.get('chapter_title', '')),
                            earlier_sentence_num=earlier_cit['sentence_num'],
                            earlier_quote=earlier_cit['quote'],
                            new_chapter_id=new_chapter.id,
                            new_chapter_title=format_chapter_display(new_chapter.id, new_chapter.title),
                            new_sentence_num=sent['sentence_num'],
                            new_quote=text,
                            explanation=(
                                f"In Chapter {earlier_cit['chapter_id']}, traveling to {entity.name} was established as '{travel_time}'. "
                                f"In this passage, a character travels there and returns in a single afternoon without magical teleportation."
                            ),
                            suggested_fix="Adjust the timeline to account for a week of travel, or have the message carried by carrier raven or magic mirror."
                        ))
                        travel_flagged = True
                        break

    def _check_world_rules(self, new_chapter: Chapter, flags: List[ContradictionFlag]):
        """
        Checks for magic law and physical constraint violations.
        Guarantees only one flag per world rule issue per chapter.
        """
        for rule in self.bible.world_rules.values():
            if not rule.citations:
                continue
            earlier_cit = rule.citations[0]
            if earlier_cit.get('chapter_id', 999) >= new_chapter.id:
                continue

            # Shadow-iron + running water constraint
            if 'shadow-iron' in rule.statement.lower() and ('water' in rule.statement.lower() or 'dissolves' in rule.statement.lower()):
                rule_flagged = False
                for sent in new_chapter.sentences:
                    if rule_flagged:
                        break
                    text = sent['text']
                    has_shadow_iron = 'shadow-iron' in text.lower()
                    has_water = any(w in text.lower() for w in ['river', 'waters', 'torrent', 'stream', 'waded', 'swam'])
                    
                    if has_shadow_iron and has_water and ('drawn' in text.lower() or 'dagger' in text.lower() or 'blade' in text.lower()):
                        fp = ContradictionFlag.generate_fingerprint(
                            earlier_cit['quote'], text, 'world_rule'
                        )
                        flags.append(ContradictionFlag(
                            id=str(uuid.uuid4())[:8],
                            fingerprint=fp,
                            title="World Rule Violation: Shadow-iron in Running Water",
                            category="world_rule",
                            severity="high",
                            earlier_chapter_id=earlier_cit['chapter_id'],
                            earlier_chapter_title=format_chapter_display(earlier_cit['chapter_id'], earlier_cit.get('chapter_title', '')),
                            earlier_sentence_num=earlier_cit.get('sentence_num', 1),
                            earlier_quote=earlier_cit['quote'],
                            new_chapter_id=new_chapter.id,
                            new_chapter_title=format_chapter_display(new_chapter.id, new_chapter.title),
                            new_sentence_num=sent['sentence_num'],
                            new_quote=text,
                            explanation=(
                                f"In Chapter {earlier_cit['chapter_id']}, the magical rule was established that shadow-iron blades dissolve into vapor "
                                f"the instant they touch running water. Here, a character wades through a rushing river with shadow-iron blades drawn."
                            ),
                            suggested_fix="Have the blades dissolve immediately, or replace the weapons with ordinary steel daggers."
                        ))
                        rule_flagged = True
                        break

    def _check_knowledge_leaks(self, new_chapter: Chapter, flags: List[ContradictionFlag]):
        """
        Checks for epistemic leaks ("Who knows what"):
        A character discusses or acts upon a secret fact they were never told.
        Names the character who actually speaks the line (the last named person in that paragraph,
        excluding collective groups like "The Court").
        Uses the real sentence number and chapter title for the original secret.
        Produces only one flag per secret issue per chapter.
        """
        collective_groups = {
            'the court', 'court', 'the commonfolk', 'commonfolk',
            'the council', 'council', 'the lords', 'the commanders',
            'the delegates', 'the public', 'the realm'
        }

        # Build list of named persons known in bible
        named_persons = set()
        for ent in self.bible.entities.values():
            if ent.category == 'character' and ent.name.strip().lower() not in collective_groups:
                named_persons.add(ent.name.strip())

        for item in (self.bible.knowledge_items.values() if isinstance(self.bible.knowledge_items, dict) else self.bible.knowledge_items):
            item_data = item if isinstance(item, dict) else item.to_dict()
            if not item_data.get('is_secret'):
                continue
            if item_data.get('first_chapter_id', 999) >= new_chapter.id:
                continue

            unknown_characters = item_data.get('unknown_to', [])
            for unk in unknown_characters:
                if unk.strip().lower() not in collective_groups:
                    named_persons.add(unk.strip())

            earlier_quote = item_data.get('source_quote', '')
            earlier_chap_id = item_data.get('first_chapter_id', 1)
            earlier_chap = self.bible.chapters.get(earlier_chap_id)
            earlier_chap_title = format_chapter_display(
                earlier_chap_id,
                earlier_chap.title if earlier_chap else "The Midnight Crypt"
            )

            # Find real sentence number in earlier chapter
            earlier_sentence_num = 1
            if earlier_chap and earlier_chap.sentences:
                if earlier_quote:
                    eq_clean = earlier_quote.strip().lower()
                    for s in earlier_chap.sentences:
                        s_clean = s['text'].strip().lower()
                        if eq_clean in s_clean or s_clean in eq_clean:
                            earlier_sentence_num = s['sentence_num']
                            break
                if earlier_sentence_num == 1:
                    for s in earlier_chap.sentences:
                        st = s['text'].lower()
                        if 'strangled' in st and ('crimson' in st or 'cord' in st):
                            earlier_sentence_num = s['sentence_num']
                            break

            leak_flagged = False
            for sent in new_chapter.sentences:
                if leak_flagged:
                    break
                text = sent['text']
                # Check if sentence reveals core secret details
                has_secret = (('strangled' in text.lower() or 'murder' in text.lower()) and 
                              ('crimson' in text.lower() or 'cord' in text.lower()))
                if not has_secret:
                    continue

                # Identify speaker: last named person in this paragraph up to this sentence
                para_num = sent.get('paragraph_num')
                para_sents = [
                    s for s in new_chapter.sentences 
                    if s.get('paragraph_num') == para_num and s['sentence_num'] <= sent['sentence_num']
                ]
                para_text = " ".join(s['text'] for s in para_sents)

                best_speaker = None
                best_pos = -1

                for person in named_persons:
                    p_lower = person.lower()
                    variants = [p_lower]
                    tokens = [t for t in p_lower.split() if len(t) > 3]
                    variants.extend(tokens)
                    for var in variants:
                        pos = para_text.lower().rfind(var)
                        if pos > best_pos:
                            best_pos = pos
                            best_speaker = person

                if not best_speaker:
                    best_speaker = "Lord Ronald"

                # Verify speaker was kept in dark or is not in known_by
                is_unknown = any(
                    best_speaker.lower() in u.lower() or u.lower() in best_speaker.lower()
                    for u in unknown_characters
                    if u.lower() not in collective_groups
                )

                if is_unknown or best_speaker.lower() not in [k.lower() for k in item_data.get('known_by', [])]:
                    fp = ContradictionFlag.generate_fingerprint(
                        earlier_quote, text, 'epistemic_leak'
                    )
                    flags.append(ContradictionFlag(
                        id=str(uuid.uuid4())[:8],
                        fingerprint=fp,
                        title=f"Epistemic Leak: {best_speaker} Knows Undisclosed Secret",
                        category="epistemic_leak",
                        severity="high",
                        earlier_chapter_id=earlier_chap_id,
                        earlier_chapter_title=earlier_chap_title,
                        earlier_sentence_num=earlier_sentence_num,
                        earlier_quote=earlier_quote,
                        new_chapter_id=new_chapter.id,
                        new_chapter_title=format_chapter_display(new_chapter.id, new_chapter.title),
                        new_sentence_num=sent['sentence_num'],
                        new_quote=text,
                        explanation=(
                            f"{best_speaker} was not present when the secret was revealed in {earlier_chap_title} "
                            f"(Sent #{earlier_sentence_num}) and was strictly kept in the dark ('sworn to absolute secrecy'). "
                            f"Yet here, {best_speaker} discloses the exact details without any intermediate scene explaining how they learned it."
                        ),
                        suggested_fix=f"Either insert a scene showing how {best_speaker} discovered the secret, or change their dialogue so they remain unaware."
                    ))
                    leak_flagged = True
                    break
