import json
import os
from typing import Text, Dict, Any, List, Optional, Tuple

from parlai import PROJECT_PATH
from parlai.mturk.tasks.woz.backend.nlu import NLUServerConnection
from parlai.mturk.tasks.woz.backend import constants
from parlai.mturk.tasks.woz.backend import static_test_assets
from parlai.mturk.tasks.woz.backend import template_filler


class WizardSuggestion:
    def __init__(
        self,
        intent2reply_file,
        num_suggestions=3,
        max_num_suggestions=10,
        nlu_server_address=constants.DEFAULT_RASA_NLU_SERVER_ADDRESS
    ):
        with open(intent2reply_file, "r", encoding="utf-8") as in_file:
            self.intent2reply = json.load(in_file)
        self.num_suggestions = num_suggestions
        self.max_num_suggestions = max_num_suggestions
        self.nlu = NLUServerConnection(server_address=nlu_server_address)

    def get_suggestions(
        self,
        wizard_utterance: Text,
        kb_item: Dict[Text, Any],
        scenario: Optional[Text] = None,
        comparing: bool = False,
        return_intents: bool = False,
    ) -> Tuple[List[Text], bool]:
        possibly_wrong_item_selected = (
            None  # Will be set `True` if top intent cannot be filled
        )

        intents, entities = self.nlu.get_intents_and_entities(
            text=wizard_utterance,
            max_num_suggestions=self.max_num_suggestions,
            scenario=scenario,
            comparing=comparing,
        )
        if return_intents:
            return intents, False

        suggestions = []
        for intent in intents:
            if intent in self.intent2reply:
                fn_fill = getattr(template_filler, f'fill_{intent}')

                suggestion = fn_fill(self.intent2reply, kb_item)
                if suggestion:
                    suggestions.append(suggestion)

                if possibly_wrong_item_selected is None:
                    possibly_wrong_item_selected = suggestion is None

            if len(suggestions) >= self.num_suggestions:
                break

        if len(suggestions) == 0:
            suggestions.append(wizard_utterance)

        if possibly_wrong_item_selected is None or not scenario:
            possibly_wrong_item_selected = False

        return suggestions, possibly_wrong_item_selected


if __name__ == '__main__':

    scenarios = ['get_book_ride_item', 'get_change_ride_item', 'get_search_hotel_item',
                 'get_ride_status_item']

    for sc in ['get_search_hotel_item']:
        kb_item, utterances, scenario = getattr(static_test_assets, sc)()
        base_dir = os.path.join(PROJECT_PATH, 'resources', scenario)
        ws = WizardSuggestion(
            intent2reply_file=os.path.join(base_dir, 'intent2reply.json'),
            nlu_server_address=constants.RASA_NLU_SERVER_ADDRESS_TEMPLATE.format(
                port=constants.SCENARIO_PORT_MAP[scenario]
            )
        )

        for utterance in utterances:
            # Use rasa to get an intent label
            suggestions = ws.get_suggestions(wizard_utterance=utterance, kb_item=kb_item,
                                             scenario=scenario)

            print(f'Suggestions for "{utterance}": {suggestions}')
            print('----------------------------------------------')
    print('====================================================================================')
    print('====================================================================================')
