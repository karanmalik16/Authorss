import unittest
from app import app, active_bible

class TestStepsVerification(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_complete_step_flow(self):
        # 1. Restart / Load Demo Story
        res = self.client.post('/api/demo/load')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        flags = data['bible']['flags']
        pending = [f for f in flags if f['status'] == 'pending']
        self.assertEqual(len(pending), 5, f"Expected exactly 5 pending flags, got {len(pending)}")
        
        expected_titles = [
            "Contradictory Eye Color: Lady Vivienne",
            "Spatiotemporal Impossibility: Travel to Ashen Fortress",
            "Epistemic Leak: Lord Ronald Knows Undisclosed Secret",
            "Physical Impossibility: Master Corvus (Severed Right Hand)",
            "World Rule Violation: Shadow-iron in Running Water"
        ]
        
        actual_titles = [f['title'] for f in pending]
        for exp in expected_titles:
            self.assertIn(exp, actual_titles, f"Missing expected flag: {exp}")

        # Check secret leak earlier citation:
        leak_flag = next(f for f in pending if "Lord Ronald" in f['title'])
        self.assertEqual(leak_flag['earlier_sentence_num'], 4)
        self.assertEqual(leak_flag['earlier_chapter_title'], "Ch. 1 · The Midnight Crypt")

        # 2. Edit Chapter 2: change 'violet' to 'emerald'
        ch2 = next(c for c in data['bible']['chapters'] if c['id'] == 2)
        new_text = ch2['raw_text'].replace('piercing violet eyes', 'piercing emerald eyes')
        fix_res = self.client.post('/api/chapters/2/fix', json={'text': new_text})
        self.assertEqual(fix_res.status_code, 200)
        fix_data = fix_res.get_json()
        self.assertEqual(fix_data['pending_flags_count'], 4)

        # 3. Verify bible state (simulate refresh)
        b_res = self.client.get('/api/bible')
        b_data = b_res.get_json()
        
        p_after = [f for f in b_data['flags'] if f['status'] == 'pending']
        self.assertEqual(len(p_after), 4)
        self.assertFalse(any("Eye Color" in f['title'] for f in p_after))

        fixed_flags = [f for f in b_data['flags'] if f['status'] == 'fixed']
        self.assertEqual(len(fixed_flags), 1)
        self.assertEqual(fixed_flags[0]['title'], "Contradictory Eye Color: Lady Vivienne")
        self.assertEqual(fixed_flags[0]['author_note'], "Resolved by edit.")

if __name__ == '__main__':
    unittest.main()
