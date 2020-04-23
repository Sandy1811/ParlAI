import collections
import json
import logging
import os
import subprocess
import time
from typing import Text, Dict, Any, List, Optional, Tuple

import requests

from parlai import PROJECT_PATH
from parlai.chat_service.core.shared_utils import print_and_log
from parlai.mturk.tasks.woz.backend import constants
from parlai.mturk.tasks.woz.backend import static_test_assets
from parlai.mturk.tasks.woz.backend import template_filler


class WizardSuggestion:
    def __init__(
        self,
        scenario_list: List,
        resources_dir: Text,
        start_nlu_servers: bool = False,
        num_suggestions: int = 3,
        max_num_suggestions: int = 10
    ):
        self.scenario_resources = collections.defaultdict(dict)
        self.resources_dir = resources_dir

        for scenario in scenario_list:
            try:
                with open(os.path.join(resources_dir, scenario, constants.INTENT_TO_REPLY_FILE_NAME),
                          'r', encoding='utf-8') as in_file:
                    self.scenario_resources[scenario][constants.INTENT_TO_REPLY_KEY] = json.load(in_file)
                self.scenario_resources[scenario][constants.START_NLU_SERVER_SCRIPT_PATH_KEY] = os.path.join(
                    resources_dir, scenario, constants.START_NLU_SERVER_SCRIPT_FILE_NAME
                )
                self.scenario_resources[scenario][constants.RASA_NLU_SERVER_ADDRESS_KEY] = \
                    constants.RASA_NLU_SERVER_ADDRESS_TEMPLATE.format(port=constants.SCENARIO_PORT_MAP[scenario])
                if start_nlu_servers:
                    self.start_nlu_server(scenario)
            except FileNotFoundError as e:
                print_and_log(100, f"ERROR: Could not find scenario file: {e}", should_print=True)

        self.num_suggestions = num_suggestions
        self.max_num_suggestions = max_num_suggestions

    def nlu_server_ready(self, scenario):
        try:
            response = requests.post(self.scenario_resources[scenario][constants.RASA_NLU_SERVER_ADDRESS_KEY],
                                 data=f'{{"text": "Oida"}}')
        except Exception:
            return False

        return response.status_code == 200

    def poll_nlu_server(self, scenario, poll_interval=1., max_tries=200):
        i = 0
        while not self.nlu_server_ready(scenario) and i < max_tries:
            time.sleep(poll_interval)
            i += 1

        return i < max_tries

    def start_nlu_server(self, scenario):
        if not self.nlu_server_ready(scenario): # Check whether there already is a running server
            cmd = [f'{self.scenario_resources[scenario][constants.START_NLU_SERVER_SCRIPT_PATH_KEY]}',
                   f'{os.path.join(self.resources_dir, scenario)}']

            p = subprocess.Popen(cmd)
            self.scenario_resources[scenario][constants.RASA_NLU_SERVER_PROCESS_KEY] = p

    def stop_nlu_server(self, scenario):
        if constants.RASA_NLU_SERVER_PROCESS_KEY in self.scenario_resources[scenario]:
            self.scenario_resources[scenario][constants.RASA_NLU_SERVER_PROCESS_KEY].kill()
        else:
            logging.warning(f'Cannot kill server for scenario={scenario}, because the process was started externally!')

    def get_suggestions(
        self,
        wizard_utterance: Text,
        primary_kb_item: Dict[Text, Any],
        secondary_kb_item: Dict[Text, Any] = None,
        api_name: Optional[Text] = None,
        comparing: bool = False,
        return_intents: bool = False,
    ) -> Tuple[List[Text], bool]:
        possibly_wrong_item_selected = (
            None  # Will be set `True` if top intent cannot be filled
        )

        intents, entities = self.get_intents_and_entities(
            text=wizard_utterance,
            scenario=api_name,
            comparing=comparing,
        )
        if return_intents:
            return intents, False

        suggestions = []
        for intent in intents:
            if intent in self.scenario_resources[api_name][constants.INTENT_TO_REPLY_KEY]:
                fn_fill = getattr(template_filler, f'fill_{intent}')

                suggestion = fn_fill(self.scenario_resources[api_name][constants.INTENT_TO_REPLY_KEY],
                                     primary_kb_item)
                if suggestion:
                    suggestions.append(suggestion)

                if possibly_wrong_item_selected is None:
                    possibly_wrong_item_selected = suggestion is None

            if len(suggestions) >= self.num_suggestions:
                break

        if len(suggestions) == 0:
            suggestions.append(wizard_utterance)

        if possibly_wrong_item_selected is None or not api_name:
            possibly_wrong_item_selected = False

        return suggestions, possibly_wrong_item_selected

    def query(self, text: Text, scenario: Text) -> Dict[Text, Any]:
        payload = {'text': text}
        try:
            response = requests.post(self.scenario_resources[scenario][constants.RASA_NLU_SERVER_ADDRESS_KEY],
                                     data=json.dumps(payload))
        except:
            raise ConnectionError(f"Could not access NLU server")
        if response.status_code != 200:
            raise ConnectionError(f"Could not access NLU server: {response.reason}")
        return response.json()

    def get_intents_and_entities(
        self,
        text: Text,
        scenario: Text,
        comparing: bool = False
    ) -> Tuple[List[Text], List[Text]]:
        try:
            response = self.query(text=text, scenario=scenario)
        except ConnectionError as e:
            print_and_log(100, f"ERROR: Failed NLU connection: {e}")
            return [], []
        response["intent_ranking"].sort(key=(lambda v: -v["confidence"]))
        suggestions = [
            intent["name"] for intent in response["intent_ranking"]
        ]
        return suggestions[:self.max_num_suggestions], response['entities']


if __name__ == '__main__':

    #scenarios = ['book_ride', 'ride_change', 'hotel_search', 'ride_status']
    scenarios = ['party_plan', 'party_rsvp', 'plane_search', 'restaurant_reserve', 'restaurant_search']
    ws = WizardSuggestion(scenario_list=scenarios, resources_dir=os.path.join(PROJECT_PATH, 'resources'),
                          start_nlu_servers=True)

    #scens = ['get_book_ride_item', 'get_ride_change_item', 'get_hotel_search_item',
    #             'get_ride_status_item']
    scens = ['get_party_plan_item', 'get_party_rsvp_item', 'get_plane_search_item',
             'get_restaurant_reserve_item', 'get_restaurant_search_item']
    for sc in scens:
        print(f'---- {sc} ----')
        kb_item, utterances, scenario = getattr(static_test_assets, sc)()
        ws.poll_nlu_server(scenario=scenario)
        for utterance in utterances:
            # Use rasa to get an intent label
            suggestions = ws.get_suggestions(wizard_utterance=utterance, primary_kb_item=kb_item,
                                             api_name=scenario)

            print(f'Suggestions for "{utterance}": {suggestions}')
            print('----------------------------------------------')
        ws.stop_nlu_server(scenario)
        print('====================================================================================')
        print('====================================================================================')