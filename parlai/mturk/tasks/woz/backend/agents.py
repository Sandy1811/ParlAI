from typing import List, Dict, Text, Any, Optional, Union

from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.mturk.core.shared_utils import AssignState
from parlai.mturk.tasks.woz.backend.commands import Command, QueryCommand


class NonMTurkAgent(Agent):
    def __init__(self, options: Opt) -> None:
        super(NonMTurkAgent, self).__init__(options, shared=None)

    def get_messages(self) -> List[Dict[Text, Any]]:
        # Note: Messages must contain a 'text' field
        return []

    def clear_messages(self) -> None:
        pass  # ToDo: Implement

    def is_final(self):
        return AssignState.STATUS_DONE

    def get_status(self):
        return AssignState.STATUS_DONE

    def set_status(self, *args, **kwargs) -> None:
        pass

    @property
    def worker_id(self):
        return None

    @property
    def assignment_id(self):
        return None  # ToDo: Implement

    @property
    def feedback(self):
        return None  # ToDo: Implement

    def submitted_hit(self) -> bool:
        return True


class WOZKnowledgeBaseAgent(NonMTurkAgent):
    """
    Agent that represents a knowledge base.
    """

    @staticmethod
    def add_cmdline_args(parser: ParlaiParser) -> None:
        """Add command line arguments for this agent."""
        pass

    def __init__(self, opt: Opt):
        super(WOZKnowledgeBaseAgent).__init__(opt)
        self.role = "KnowledgeBase"
        self.demo_role = "KnowledgeBase"
        self._messages = []

    def observe(self, message: Union[Dict[Text, Any], QueryCommand]) -> None:
        if isinstance(message, QueryCommand):
            pass
        else:
            super(WOZKnowledgeBaseAgent, self).observe(message)

    def act(self) -> Dict[Text, Any]:
        """Generates a response to the last observation.

        Returns:
            Message with reply
        """
        observation = self.observation

        if observation is None:
            return {"text": "Knowledge base invoked without observation."}

        query = observation.get("query")
        echo.log_write(f"KBQuery: {query}")

        if not query:
            return {"text": "Knowledge base invoked with empty query."}

        try:
            constraints = self._parse(query)
            apartment, count = api.call_api("apartment_search", constraints=constraints)
            reply = {
                "id": "KnowledgeBase",
                "text": f"Found {count} apartments. Example: {json.dumps(apartment)}.",
            }
        except Exception as e:
            reply = {
                "id": "KnowledgeBase",
                "text": f"Could not interpret your query: {e}",
            }

        self._messages.append(reply)

        return reply