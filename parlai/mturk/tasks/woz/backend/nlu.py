from typing import Text, List, Any, Dict, Optional

import requests

DEFAULT_RASA_NLU_SERVER_ADDRESS = "http://localhost:5005/model/parse"


class NLUServerConnection:
    def __init__(self, server_address: Optional[Text] = None) -> None:
        self.server_address = server_address or DEFAULT_RASA_NLU_SERVER_ADDRESS
        # ToDo: Implement something to startup the nlu server (or decide to not do this programmatically)

    def query(self, text: Text) -> Dict[Text, Any]:
        response = requests.post(self.server_address, data=f'{{"text": "{text}"}}')
        if response.status_code != 200:
            raise ConnectionError("Could not access NLU server.")
        return response.json()

    def get_suggestions(
        self,
        text: Text,
        domain: Optional[Text] = None,
        comparing: bool = False,
        max_num_suggestions: int = 3,
    ) -> List[Text]:
        response = self.query(f"{'true' if comparing else 'false'}:{domain}:{text}")
        suggestions = [
            intent["name"] for intent in response["intent_ranking"]
        ]  # ToDo: Make sure this is sorted by confidence
        return suggestions[:max_num_suggestions]


if __name__ == '__main__':
    nlu = NLUServerConnection()
    print(nlu.get_suggestions("hello"))
