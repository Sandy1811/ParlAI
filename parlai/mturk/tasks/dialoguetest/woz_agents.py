from typing import Dict, Text, Any, Optional

from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser


class WOZKnowledgeBaseAgent(Agent):
    """
    Agent that represents a knowledge base.
    """

    @staticmethod
    def add_cmdline_args(parser: ParlaiParser) -> None:
        """
        Add command line arguments for this agent.
        """
        pass

    def __init__(self, opt: Opt, shared: Optional[bool] = None):
        """
        Initialize this agent.
        """
        super().__init__(opt)

    def act(self) -> Dict[Text, Any]:
        """
        Generate response to last seen observation.

        Replies with a randomly selected candidate if label_candidates or a
        candidate file are available.
        Otherwise, replies with the label if they are available.
        Oterhwise, replies with generic hardcoded responses if the agent has
        not observed any messages or if there are no replies to suggest.

        :returns: message dict with reply
        """
        observation = self.observation

        if observation is None:
            return {"text": "Knowledge base invoked without observation."}

        text = observation.get("text", "")

        if not text:
            return {"text": "Knowledge base invoked with empty text."}

        if not text.startswith("? "):
            return {"text": "Knowledge base queries must start with a '?'."}

        reply = {"id": self.getID(), 'text': "A reply from the KB."}

        return reply
