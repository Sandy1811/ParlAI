import os

from scipy import sparse
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import tables

from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection


class WizardSuggestion:
    def __init__(self, vectorizer_file, idx2text_file, intent2idx_file, vector_space_file):
        self.vectorizer = joblib.load(vectorizer_file)
        self.idx2text = joblib.load(idx2text_file)
        self.intent2idx = joblib.load(intent2idx_file)
        self.vector_space = hdf_to_sparse_csx_matrix(*os.path.split(vector_space_file), sparse_format='csr')

    def suggest_wizard_reply(self, wizard_utterance, kb_items, nlu_context):
        intents, entities = nlu_context

        u = self.vectorizer.transform([wizard_utterance])

        for intent in intents:
            idx = np.array(self.intent2idx[intent])
            S = cosine_similarity(self.vector_space[idx], u)

            #jdx = np.argpartition(-S.reshape(-1,), 5)[:5]
            jdx = np.argmax(S)
            data_idx = idx[jdx]

            print(f'Utterance: {wizard_utterance}; intent={intent}')
            print(f'\t{self.idx2text[data_idx]}')


def hdf_to_sparse_csx_matrix(path, name, sparse_format):
    attrs = _get_attrs_from_hdf_file(path, name, 'csx', ['data', 'indices', 'indptr', 'shape'])
    constructor = getattr(sparse, '{}_matrix'.format(sparse_format))

    return constructor(tuple(attrs[:3]), shape=tuple(attrs[3]))


def hdf_to_sparse_coo_matrix(path, name):
    attrs = _get_attrs_from_hdf_file(path, name, 'coo', ['data', 'rows', 'cols', 'shape'])

    return sparse.coo_matrix((attrs[0], tuple(attrs[1:3])), shape=attrs[3])


def _get_attrs_from_hdf_file(path, name, sparse_format, attributes):
    with tables.open_file(os.path.join(path, name), 'r') as f:
        attrs = []
        for attr in attributes:
            attrs.append(getattr(f.root, '{}_{}'.format(sparse_format, attr)).read())
    return attrs

def suggest_wizard_reply(wizard_utterance, kb_items, nlu_context):
    pass
    # 1. Take classified intent and look up intent in dictionary
    # 2. From all the sentences for this intent, re-order by cosine sim with what the user said
    # 3. Include a response selector


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
    utterance_11 = 'from Rykestrasse 34'
    utterance_12 = 'to the station'

    nlu = NLUServerConnection()
    for utterance in [utterance_1, utterance_2, utterance_3, utterance_4, utterance_5, utterance_11,
                      utterance_6, utterance_7, utterance_8, utterance_9, utterance_10, utterance_12]:
        # Use rasa to get an intent label
        nlu_context = nlu.get_suggestions(utterance)
        print(utterance, nlu_context)

    base_dir = '/Users/thomas/research/data/dataset-collection-2020/book_ride/mturk_dialogues/'
    ws = WizardSuggestion(vectorizer_file=os.path.join(base_dir, 'vectorizer.joblib'),
                          vector_space_file=os.path.join(base_dir, 'X.hdf'),
                          idx2text_file=os.path.join(base_dir, 'idx2text.joblib'),
                          intent2idx_file=os.path.join(base_dir, 'intent2idx.joblib'))
    ws.suggest_wizard_reply(wizard_utterance=utterance_2, kb_items=[kb_item], nlu_context=nlu.get_suggestions(utterance_2))

    suggest_wizard_reply(wizard_utterance=utterance_2, kb_items=[kb_item], nlu_context=nlu_context)