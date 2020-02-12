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
        """Add command line arguments for this agent."""
        pass

    def __init__(self, opt: Opt, shared: Optional[bool] = None):
        """Initialize this agent."""
        super().__init__(opt)
        self.role = "KnowledgeBase"
        self.demo_role = "KnowledgeBase"

    def act(self) -> Dict[Text, Any]:
        """Generates a response to the last observation.

        Returns:
            Message with reply
        """
        observation = self.observation

        if observation is None:
            return {"text": "Knowledge base invoked without observation."}

        text = observation.get("text", "")

        if not text:
            return {"text": "Knowledge base invoked with empty text."}

        reply = {"id": self.getID(), "text": f"A reply from the KB to your message '{observation}'."}

        return reply


class DummyAgent(Agent):
    """Agent returns a random response."""

    @staticmethod
    def add_cmdline_args(parser) -> None:
        """Add command line arguments for this agent."""
        parser = parser.add_argument_group('DummyAgent arguments')
        parser.add_argument(
            "--dummy-responses",
            type=str,
            default=None,
            help="File of candidate responses to choose from",
        )

    def __init__(self, opt: Opt, role: Text) -> None:
        """Initialize this agent."""
        super().__init__(opt)
        self.id = "DummyAgent"
        self.role = role
        self._num_messages_sent = 0
        if opt.get("dummy_responses"):
            with open(opt.get("dummy_responses"), "r", encoding="utf-8") as file:
                self.response_candidates = file.read().split("\n")
        else:
            self.response_candidates = None

    def act(self) -> Dict[Text, Any]:
        """Generates a response to the last observation.

        Returns:
            Message with reply
        """
        if not self.response_candidates:
            return {"id": self.getID(), "text": "DUMMY: No response candidates.", "role": self.role}

        self._num_messages_sent += 1
        index = self._num_messages_sent % len(self.response_candidates)
        reply = {"id": self.getID(), "text": self.response_candidates[index], "role": self.role}

        return reply
