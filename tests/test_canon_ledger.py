"""
Unit tests for Canon Ledger.
Tests extraction, contradiction detection, citation verification, dismissal memory, and exports.
"""

import unittest
import os
import json
from core.models import StoryBible, Chapter, ContradictionFlag
from core.file_parser import split_into_sentences, parse_manuscript_file
from core.extractor import ManuscriptExtractor
from core.checker import ContradictionChecker

class TestCanonLedger(unittest.TestCase):
    def setUp(self):
        self.bible = StoryBible(title="Test Chronicle")
        self.extractor = ManuscriptExtractor()
        self.checker = ContradictionChecker(self.bible)
        
        # Load sample chapters
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ch1_path = os.path.join(base_dir, "sample_manuscript", "chapter_1.md")
        self.ch2_path = os.path.join(base_dir, "sample_manuscript", "chapter_2.md")
        self.ch3_path = os.path.join(base_dir, "sample_manuscript", "chapter_3.md")

    def test_sentence_splitting(self):
        sample = 'Dr. Morbius stepped forward. "Stop!" he yelled. The night was cold.'
        sents = split_into_sentences(sample)
        self.assertEqual(len(sents), 3)
        self.assertEqual(sents[0]['sentence_num'], 1)

    def test_chapter_1_extraction(self):
        with open(self.ch1_path, 'r', encoding='utf-8') as f:
            text = f.read()
        sents = split_into_sentences(text)
        ch1 = Chapter(id=1, book_id="Book 1", title="Chapter 1: The Midnight Crypt", order_index=1, raw_text=text, sentences=sents)
        extracted = self.extractor.extract_chapter(ch1)
        
        # Check entities
        char_names = [e.name for e in extracted['entities']]
        self.assertTrue(any('Vivienne' in n for n in char_names), "Vivienne should be extracted")
        self.assertTrue(any('Corvus' in n for n in char_names), "Corvus should be extracted")
        
        # Check attributes
        vivienne = next((e for e in extracted['entities'] if 'Vivienne' in e.name), None)
        self.assertIsNotNone(vivienne)
        self.assertIn('emerald', vivienne.attributes.get('eye_color', ''))
        
        corvus = next((e for e in extracted['entities'] if 'Corvus' in e.name), None)
        self.assertIsNotNone(corvus)
        self.assertTrue('right hand' in corvus.attributes.get('physical_injury', '').lower())
        
        # Check world rule
        self.assertTrue(len(extracted['world_rules']) > 0)
        rule = extracted['world_rules'][0]
        self.assertIn('shadow-iron', rule.statement.lower())

    def test_chapter_2_contradictions(self):
        # Ingest Chapter 1
        with open(self.ch1_path, 'r', encoding='utf-8') as f:
            text1 = f.read()
        ch1 = Chapter(id=1, book_id="Book 1", title="Chapter 1", order_index=1, raw_text=text1, sentences=split_into_sentences(text1))
        extracted1 = self.extractor.extract_chapter(ch1)
        self.bible.chapters[1] = ch1
        for e in extracted1['entities']:
            ent = self.bible.get_or_create_entity(e.name, e.category)
            ent.attributes.update(e.attributes)
            ent.citations.extend(e.citations)
        for r in extracted1['world_rules']:
            self.bible.world_rules[r.id] = r
        for k in extracted1['knowledge_items']:
            self.bible.knowledge_items.append(k)

        # Now check Chapter 2
        with open(self.ch2_path, 'r', encoding='utf-8') as f:
            text2 = f.read()
        ch2 = Chapter(id=2, book_id="Book 1", title="Chapter 2", order_index=2, raw_text=text2, sentences=split_into_sentences(text2))
        
        flags = self.checker.check_chapter(ch2)
        # Store chapter 2 in bible
        self.bible.chapters[2] = ch2
        
        flag_categories = [f.category for f in flags]
        
        # Planted errors expected:
        # 1. Eye color change (character_trait)
        # 2. Impossible travel duration (timeline)
        # 3. Knowledge leak (epistemic_leak)
        self.assertIn('character_trait', flag_categories, "Should catch Vivienne's violet eye color shift")
        self.assertIn('timeline', flag_categories, "Should catch impossible afternoon return from 3-day ride")
        self.assertIn('epistemic_leak', flag_categories, "Should catch Lord Ronald knowing secret strangulation cord")
        
        # Verify citations are strictly populated
        for flag in flags:
            self.assertTrue(len(flag.earlier_quote) > 0, "Flag must have earlier quote citation")
            self.assertTrue(len(flag.new_quote) > 0, "Flag must have new quote citation")

    def test_chapter_3_contradictions(self):
        # Ingest Ch 1 & 2
        self.test_chapter_2_contradictions()
        
        # Ingest Chapter 3
        with open(self.ch3_path, 'r', encoding='utf-8') as f:
            text3 = f.read()
        ch3 = Chapter(id=3, book_id="Book 1", title="Chapter 3", order_index=3, raw_text=text3, sentences=split_into_sentences(text3))
        
        flags = self.checker.check_chapter(ch3)
        self.bible.chapters[3] = ch3
        flag_categories = [f.category for f in flags]
        
        # Planted errors expected:
        # 1. Severed right hand gripping sword (physical_state)
        # 2. Shadow-iron in running water (world_rule)
        self.assertIn('physical_state', flag_categories, "Should catch Corvus gripping sword with severed right hand")
        self.assertIn('world_rule', flag_categories, "Should catch shadow-iron dagger wading through running water")

    def test_dismissal_memory(self):
        # Ingest Ch 1 and check Ch 2
        self.test_chapter_2_contradictions()
        
        # Find eye color flag
        eye_flag = next((f for f in self.bible.flags if f.category == 'character_trait'), None)
        self.assertIsNotNone(eye_flag)
        
        # Dismiss it
        flag_id = eye_flag.id
        fingerprint = eye_flag.fingerprint
        dismissed = self.bible.dismiss_flag(flag_id, note="Intentional magical glamor in revised draft")
        self.assertTrue(dismissed)
        self.assertIn(fingerprint, self.bible.dismissed_fingerprints)
        
        # Re-check Chapter 2
        ch2 = self.bible.chapters.get(2)
        new_flags = self.checker.check_chapter(ch2)
        # The eye color flag should NOT be re-added or marked pending
        reappeared = any(f.fingerprint == fingerprint and f.status == 'pending' for f in new_flags)
        self.assertFalse(reappeared, "Dismissed flag must not reappear as pending")

    def test_bible_export_markdown(self):
        self.test_chapter_3_contradictions()
        md = self.bible.export_as_markdown()
        self.assertIn("# Story Bible: Test Chronicle", md)
        self.assertIn("## Characters", md)
        self.assertIn("## Continuity Audit Flags", md)

if __name__ == '__main__':
    unittest.main()
