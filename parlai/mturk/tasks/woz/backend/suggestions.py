import json
import os

from parlai import PROJECT_PATH
from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection
from parlai.mturk.tasks.woz.backend import constants
from parlai.mturk.tasks.woz.backend import template_filler


class WizardSuggestion:
    def __init__(self, intent2reply_file, num_suggestions=3, max_num_suggestions=10,
                 nlu_server_address=constants.DEFAULT_RASA_NLU_SERVER_ADDRESS):
        with open(intent2reply_file) as in_file:
            self.intent2reply = json.load(in_file)
        self.num_suggestions = num_suggestions
        self.max_num_suggestions = max_num_suggestions
        self.nlu = NLUServerConnection(server_address=nlu_server_address)

    def get_suggestions(
        self, wizard_utterance, kb_item, return_intents=False
    ):
        intents, entities = self.nlu.get_suggestions(text=wizard_utterance,
                                                     max_num_suggestions=self.max_num_suggestions)

        if return_intents:
            return intents

        suggestions = []
        for intent in intents:
            if intent in self.intent2reply:
                fn_fill = getattr(template_filler, f'fill_{intent}')

                suggestion = fn_fill(self.intent2reply, kb_item)
                if suggestion:
                    suggestions.append(suggestion)

            if len(suggestions) >= self.num_suggestions:
                break

        if len(suggestions) == 0:
            suggestions.append(wizard_utterance)

        return suggestions


if __name__ == '__main__':
    kb_item = {"id": 660,
               "Price": 22,
               "AllowsChanges": False,
               "MinutesTillPickup": 20,
               "ServiceProvider": "Uber",
               "DriverName": "Ella",
               "CarModel": "Ford",
               "LicensePlate": "432 LSA",
               "DepartureLocation": "Tegel Airport, International Arrivals",
               "ArrivalLocation": "Hyatt Alexanderplatz"}
    #utterance_1 = 'Okay thanks a lot and goodbye'
    #utterance_2 = 'I want a cab to Alexanderplatz'
    utterance_3 = 'Right, Could you provide your name?'
    #utterance_4 = 'Get me to the airport please'
    #utterance_5 = 'pls pick me up from the main station'
    utterance_6 = 'No problem, where can the driver pick you up from?'
    utterance_7 = 'whats your name?'
    utterance_8 = 'where do you like to go, sir?'
    utterance_9 = 'thats all booked for you now.'
    #utterance_10 = 'i wanna go to the shopping mall'
    #utterance_11 = 'from Rykestrasse 34' # crashes with a ß
    #utterance_12 = 'to the station'
    #utterance_13 = 'I want to go to the East Entrance of the Central Station'
    #utterance_14 = 'Pick me up from Main Street 42'
    utterance_15 = 'Your car will arrive in 34 minutes and your driver will be Carl in some old car. He is from Uber btw.'

    base_dir = os.path.join(PROJECT_PATH, 'resources', 'book_ride')
    ws = WizardSuggestion(intent2reply_file=os.path.join(base_dir, 'intent2reply.json'))

    for utterance in [utterance_3, utterance_6, utterance_7, utterance_8, utterance_9, utterance_15]:
        # Use rasa to get an intent label
        suggestions = ws.get_suggestions(wizard_utterance=utterance, kb_item=kb_item)

        print(f'Suggestions for "{utterance}": {suggestions}')
        print('----------------------------------------------')