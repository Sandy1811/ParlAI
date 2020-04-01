import json
import os

from parlai import PROJECT_PATH
from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection


class WizardSuggestion:
    def __init__(self, intent2reply_file):
        with open(intent2reply_file) as in_file:
            self.intent2reply = json.load(in_file)

    def get_suggestions(self, wizard_utterance, kb_item, nlu_context, return_intents=False):
        intents, entities = nlu_context

        if return_intents:
            return intents

        suggestions = []
        for intent in intents:
            if intent in ['provide_ride_details', 'provide_driver_details']:
                suggestions.append(
                    self.intent2reply[intent].format(service_provider=kb_item['ServiceProvider'],
                                                     driver_name=kb_item['DriverName'],
                                                     minutes_till_pickup=kb_item['MinutesTillPickup'],
                                                     car_model=kb_item['CarModel'], booking_id=kb_item['id'],
                                                     license_plate=kb_item['LicensePlate'], price=kb_item['Price'])
                )
            else:
                suggestions.append(self.intent2reply.get(intent, 'None'))

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

    nlu = NLUServerConnection()
    base_dir = os.path.join(PROJECT_PATH, 'resources')
    ws = WizardSuggestion(intent2reply_file=os.path.join(base_dir, 'intent2reply.json'))

    for utterance in [utterance_3, utterance_6, utterance_7, utterance_8, utterance_9, utterance_15]:
        # Use rasa to get an intent label
        nlu_context = nlu.get_suggestions(utterance)
        suggestions = ws.get_suggestions(wizard_utterance=utterance, kb_item=kb_item,
                                               nlu_context=nlu_context)

        print(f'Intents for "{utterance}": {nlu_context[0]}')
        print(f'Suggestions for "{utterance}": {suggestions}')
        print('----------------------------------------------')