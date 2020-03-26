import os

from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from parlai import PROJECT_PATH
from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection
from parlai.mturk.tasks.woz.backend import save_load


class WizardSuggestion:
    def __init__(self, vectorizer_file, idx2text_file, intent2idx_file, vector_space_file):
        self.vectorizer = joblib.load(vectorizer_file)
        self.idx2text = joblib.load(idx2text_file)
        self.intent2idx = joblib.load(intent2idx_file)
        self.vector_space = save_load.hdf_to_sparse_csx_matrix(*os.path.split(vector_space_file),
                                                               sparse_format='csr')

    def suggest_wizard_reply(self, wizard_utterance, kb_items, nlu_context, return_intents=False):
        intents, entities = nlu_context

        # TODO: Do something with the entities and KB item(s)
        if return_intents:
            return intents

        suggestions = []
        u = self.vectorizer.transform([wizard_utterance])

        for intent in intents:
            idx = np.array(self.intent2idx[intent])
            S = cosine_similarity(self.vector_space[idx], u)

            jdx = np.argmax(S)
            data_idx = idx[jdx]

            suggestions.append(self.idx2text[data_idx])

        return suggestions


if __name__ == '__main__':
    kb_item = {"id": 660,
               "Price": 22,
               "AllowsChanges": False,
               "MinutesTillPickup": 20,
               "ServiceProvider": "Uber",
               "DriverName": "Ella",
               "CarModel": "Ford",
               "LicensePlate": "432 LSA"}
    utterance_1 = 'Okay thanks a lot and goodbye'
    utterance_2 = 'I want a cab to Alexanderplatz'
    utterance_3 = 'Right, Could you provide your name?'
    utterance_4 = 'Get me to the airport please'
    utterance_5 = 'pls pick me up from the main station'
    utterance_6 = 'No problem, where can the driver pick you up from?'
    utterance_7 = 'whats your name?'
    utterance_8 = 'where do you like to go, sir?'
    utterance_9 = 'thats all booked for you now.'
    utterance_10 = 'i wanna go to the shopping mall'
    utterance_11 = 'from Rykestrasse 34' # crashes with a ß
    utterance_12 = 'to the station'

    nlu = NLUServerConnection()
    base_dir = os.path.join(PROJECT_PATH, 'resources')
    ws = WizardSuggestion(vectorizer_file=os.path.join(base_dir, 'vectorizer.joblib'),
                          vector_space_file=os.path.join(base_dir, 'X.hdf'),
                          idx2text_file=os.path.join(base_dir, 'idx2text.joblib'),
                          intent2idx_file=os.path.join(base_dir, 'intent2idx.joblib'))

    for utterance in [utterance_1, utterance_2, utterance_3, utterance_4, utterance_5, utterance_11,
                      utterance_6, utterance_7, utterance_8, utterance_9, utterance_10, utterance_12]:
        # Use rasa to get an intent label
        nlu_context = nlu.get_suggestions(utterance)
        suggestions = ws.suggest_wizard_reply(wizard_utterance=utterance, kb_items=[kb_item],
                                              nlu_context=nlu_context)

        print(f'Intents for "{utterance}": {nlu_context[0]}')
        print(f'Suggestions for "{utterance}": {suggestions}')
        print('----------------------------------------------')