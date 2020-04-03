from typing import Text, List, Any, Dict, Optional, Tuple

import requests

from parlai.mturk.tasks.woz.backend import constants


class NLUServerConnection:
    def __init__(self, server_address: Optional[Text] = None) -> None:
        self.server_address = (
            server_address or constants.DEFAULT_RASA_NLU_SERVER_ADDRESS
        )
        # ToDo: Implement something to startup the nlu server (or decide to not do this programmatically)
        # TODO: Also make sure the _right_ model is chosen, i.e. via a "domain" parameter

    def query(self, text: Text) -> Dict[Text, Any]:
        response = requests.post(self.server_address, data=f'{{"text": "{text}"}}')
        if response.status_code != 200:
            raise ConnectionError(f"Could not access NLU server: {response.reason}")
        return response.json()

    def get_intents_and_entities(
        self,
        text: Text,
        domain: Optional[Text] = None,
        comparing: bool = False,
        max_num_suggestions: int = 3,
    ) -> Tuple[List[Text], List[Text]]:
        response = self.query(
            f"{'true' if comparing else 'false'}:{domain or 'general'}:{text}"
        )
        response["intent_ranking"].sort(key=(lambda v: -v["confidence"]))
        suggestions = [
            intent["name"] for intent in response["intent_ranking"]
        ]
        return suggestions[:max_num_suggestions], response['entities']


if __name__ == '__main__':
    nlu = NLUServerConnection()
    print(nlu.get_intents_and_entities("hello"))
