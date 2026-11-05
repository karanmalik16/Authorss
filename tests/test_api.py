"""
Integration tests for Canon Ledger Flask Web Application and REST API.
"""

import unittest
import json
from app import app, active_bible

class TestCanonLedgerAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_index_route(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'CANON LEDGER', res.data)
        self.assertIn(b'Continuity Sentinel', res.data)

    def test_02_load_demo(self):
        res = self.client.post('/api/demo/load')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        
        # Verify 3 chapters loaded
        self.assertEqual(len(data['bible']['chapters']), 3)
        
        # Verify exactly 5 planted errors detected
        flags = data['bible']['flags']
        self.assertEqual(len(flags), 5)
        
        titles = [f['title'] for f in flags]
        # Vivienne eye color
        self.assertTrue(any('Contradictory Eye Color: Lady Vivienne' in t for t in titles))
        # Justinian 3-day travel
        self.assertTrue(any('Spatiotemporal Impossibility: Travel to Ashen Fortress' in t for t in titles))
        # Corvus severed right hand
        self.assertTrue(any('Physical Impossibility: Master Corvus (Severed Right Hand)' in t for t in titles))
        # Shadow iron in water
        self.assertTrue(any('World Rule Violation: Shadow-iron in Running Water' in t for t in titles))
        # Epistemic secret leak named to Lord Ronald
        self.assertTrue(any('Epistemic Leak: Lord Ronald Knows Undisclosed Secret' in t for t in titles))

    def test_03_get_bible(self):
        self.test_02_load_demo()
        res = self.client.get('/api/bible')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('stats', data)
        self.assertEqual(data['stats']['total_chapters'], 3)
        self.assertGreater(data['stats']['total_words'], 500)
        self.assertGreater(data['stats']['total_entities'], 5)

    def test_04_flag_status_decision(self):
        self.test_02_load_demo()
        res = self.client.get('/api/bible')
        data = res.get_json()
        flag = data['flags'][0]
        flag_id = flag['id']

        # Dismiss flag
        d_res = self.client.post(f'/api/flags/{flag_id}/status', json={
            'status': 'dismissed',
            'author_note': 'Tested author dismissal'
        })
        self.assertEqual(d_res.status_code, 200)
        self.assertTrue(d_res.get_json()['success'])

        # Check updated flag in bible
        res_after = self.client.get('/api/bible')
        data_after = res_after.get_json()
        updated_flag = next(f for f in data_after['flags'] if f['id'] == flag_id)
        self.assertEqual(updated_flag['status'], 'dismissed')
        self.assertEqual(updated_flag['author_note'], 'Tested author dismissal')

    def test_05_export_endpoints(self):
        self.test_02_load_demo()
        
        # Test Markdown Export
        res_md = self.client.get('/api/export/markdown')
        self.assertEqual(res_md.status_code, 200)
        self.assertIn(b'# Story Bible', res_md.data)
        
        # Test JSON Export
        res_json = self.client.get('/api/export/json')
        self.assertEqual(res_json.status_code, 200)
        parsed = json.loads(res_json.data.decode('utf-8'))
        self.assertIn('chapters', parsed)
        
        # Test Audit Report Export
        res_rep = self.client.get('/api/export/report')
        self.assertEqual(res_rep.status_code, 200)
        self.assertIn(b'Continuity Audit Flags', res_rep.data)

    def test_06_demo_guide(self):
        res = self.client.get('/api/demo/guide')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('real_world_examples', data)
        self.assertGreaterEqual(len(data['real_world_examples']), 3)
        self.assertIn('steps', data)
        self.assertEqual(len(data['steps']), 5)

    def test_07_custom_chapter_upload_and_edit(self):
        # Reset
        self.client.post('/api/reset')
        
        # Upload Chapter 1
        res1 = self.client.post('/api/chapters/upload', json={
            'title': 'The Iron Citadel',
            'text': 'Queen Mara had obsidian dark eyes. The citadel was a two-week march from the capital.'
        })
        self.assertEqual(res1.status_code, 200)
        
        # Upload Chapter 2 with contradiction
        res2 = self.client.post('/api/chapters/upload', json={
            'title': 'The Council Chamber',
            'text': 'Queen Mara opened her azure blue eyes and gazed at her advisors.'
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(len(data2['new_flags']), 1)
        self.assertEqual(data2['new_flags'][0]['category'], 'character_trait')
        
        # Edit Chapter 2 text to fix it
        ch2_id = data2['chapter']['id']
        fix_res = self.client.post(f'/api/chapters/{ch2_id}/fix', json={
            'text': 'Queen Mara opened her obsidian dark eyes and gazed at her advisors.'
        })
        self.assertEqual(fix_res.status_code, 200)
        self.assertIn('obsidian dark eyes', fix_res.get_json()['chapter']['raw_text'])
        # Contradiction resolved: no pending flags remain, flag marked as fixed
        self.assertEqual(fix_res.get_json()['pending_flags_count'], 0)
        b_res = self.client.get('/api/bible').get_json()
        self.assertEqual(len(b_res['flags']), 1)
        self.assertEqual(b_res['flags'][0]['status'], 'fixed')
        self.assertEqual(b_res['flags'][0]['author_note'], 'Resolved by edit.')

    def test_08_references_endpoint(self):
        res = self.client.get('/api/references')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('competitors', data)
        self.assertGreaterEqual(len(data['competitors']), 10)
        self.assertIn('demand_evidence', data)
        self.assertGreaterEqual(len(data['demand_evidence']), 3)

    def test_09_edit_rebuilds_sentence_numbers(self):
        """
        Verify that saving a chapter rebuilds flags with fresh sentence numbers
        and eliminates stale sentence citations.
        """
        self.test_02_load_demo()
        b_res = self.client.get('/api/bible')
        b_data = b_res.get_json()
        
        # In demo Chapter 2, find Vivienne eye color flag
        v_flag = next(f for f in b_data['flags'] if 'Eye Color' in f['title'])
        old_sent_num = v_flag['new_sentence_num']
        
        # Get Chapter 2 text and insert an extra sentence before Vivienne's sentence
        ch2 = next(c for c in b_data['chapters'] if c['id'] == 2)
        original_text = ch2['raw_text']
        modified_text = original_text.replace(
            "The high council chamber",
            "The thunder cracked violently across the night sky. The high council chamber"
        )
        
        # Save edit
        save_res = self.client.post('/api/chapters/2/fix', json={'text': modified_text})
        self.assertEqual(save_res.status_code, 200)
        
        # Verify flag sentence number shifted by +1
        b_res2 = self.client.get('/api/bible')
        b_data2 = b_res2.get_json()
        v_flag2 = next(f for f in b_data2['flags'] if 'Eye Color' in f['title'])
        self.assertEqual(v_flag2['new_sentence_num'], old_sent_num + 1)
        
        # Now fix the conflict in Chapter 2 prose (violet -> emerald)
        fixed_text = modified_text.replace("piercing violet eyes", "piercing emerald eyes")
        save_res2 = self.client.post('/api/chapters/2/fix', json={'text': fixed_text})
        self.assertEqual(save_res2.status_code, 200)
        
        b_res3 = self.client.get('/api/bible')
        b_data3 = b_res3.get_json()
        # Vivienne eye color conflict should be marked fixed with 'Resolved by edit.'
        v_fixed = next(f for f in b_data3['flags'] if 'Eye Color' in f['title'])
        self.assertEqual(v_fixed['status'], 'fixed')
        self.assertEqual(v_fixed['author_note'], 'Resolved by edit.')
        # And should not remain pending
        pending_flags = [f for f in b_data3['flags'] if f['status'] == 'pending']
        self.assertFalse(any('Eye Color' in f['title'] for f in pending_flags))

    def test_10_author_decisions_preserved_on_save(self):
        """
        Verify that prior author decisions (accepted, dismissed) and author notes
        are strictly preserved when chapters are edited and saved.
        """
        self.test_02_load_demo()
        b_res = self.client.get('/api/bible')
        b_data = b_res.get_json()
        
        # Accept travel flag
        travel_flag = next(f for f in b_data['flags'] if 'Travel' in f['title'])
        self.client.post(f"/api/flags/{travel_flag['id']}/status", json={
            'status': 'accepted',
            'author_note': 'Accepted: will address travel time in Book 2 revision'
        })
        
        # Save edit to Chapter 3
        ch3 = next(c for c in b_data['chapters'] if c['id'] == 3)
        self.client.post('/api/chapters/3/fix', json={'text': ch3['raw_text'] + "\n\nA silent mist rose."})
        
        # Check that travel flag remains accepted with note
        b_res2 = self.client.get('/api/bible')
        b_data2 = b_res2.get_json()
        rebuilt_travel = next(f for f in b_data2['flags'] if 'Travel' in f['title'])
        self.assertEqual(rebuilt_travel['status'], 'accepted')
        self.assertEqual(rebuilt_travel['author_note'], 'Accepted: will address travel time in Book 2 revision')

if __name__ == '__main__':
    unittest.main()
