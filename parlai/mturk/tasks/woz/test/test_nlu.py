import unittest

from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection

class NLUTestCase(unittest.TestCase):

    def test_basic_io(self):
        nlu = NLUServerConnection()
        candidates = nlu.get_intents_and_entities("Hello")
        self.assertIsInstance(candidates, list)
        self.assertEqual(len(candidates), 3)

    def test_distinct_pretext(self):
        nlu = NLUServerConnection()
        best_candidate_confirm = nlu.get_intents_and_entities("yes. May I have your name, please?", max_num_suggestions=1)[0]
        best_candidate_deny = nlu.get_intents_and_entities("No. May I have your name, please?", max_num_suggestions=1)[0]
        best_candidate_curtsy = nlu.get_intents_and_entities("You are welcome! May I have your name, please?", max_num_suggestions=1)[0]

        self.assertNotEqual(best_candidate_confirm, best_candidate_deny)
        self.assertNotEqual(best_candidate_confirm, best_candidate_curtsy)
        self.assertNotEqual(best_candidate_deny, best_candidate_curtsy)


if __name__ == '__main__':
    unittest.main()
