import random
from typing import List, Dict, Text, Any, Union, Tuple, Callable, Optional
import os
import json

from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.mturk.core.shared_utils import AssignState
from parlai.mturk.tasks.woz.knowledgebase import api
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

    def __init__(self, options: Opt):
        super().__init__(options)
        self.role = "KnowledgeBase"
        self.demo_role = "KnowledgeBase"
        self._messages = []

    def observe(self, message: Union[Dict[Text, Any], QueryCommand]) -> None:
        if isinstance(message, QueryCommand):
            self.observation = message
        else:
            super(WOZKnowledgeBaseAgent, self).observe(message)

    def act(self) -> Dict[Text, Any]:
        """Generates a response to the last observation.

        Returns:
            Message with reply
        """

        if self.observation is None:
            return {"text": "Knowledge base invoked without observation."}

        try:
            constraints = self.observation.constraints
            api_name = self.observation.api_name

            items, count = api.call_api(api_name, constraints=constraints)
            reply = {
                "id": "KnowledgeBase",
                "text": f"Found {count} items in {api_name}. Example: {json.dumps(items)}.",
            }
        except Exception as e:
            reply = {
                "id": "KnowledgeBase",
                "text": f"Could not interpret your query: {e}",
            }

        self._messages.append(reply)

        return reply


class WOZDummyAgent(NonMTurkAgent):
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
        parser.add_argument(
            "--dummy-user", action="store_true", help="Use a dummy user",
        )

    def __init__(self, opt: Opt, role: Text) -> None:
        """Initialize this agent."""
        super().__init__(opt)
        self.id = "DummyAgent"
        self.role = role
        self.demo_role = role
        self._num_messages_sent = 0
        self._messages = []
        if opt.get("dummy_responses"):
            try:
                with open(opt.get("dummy_responses"), "r", encoding="utf-8") as file:
                    self.response_candidates = file.read().split("\n")
            except FileNotFoundError:
                self.response_candidates = [
                    f"I am a dummy agent that didn't find "
                    f"replies in '{os.path.abspath(opt.get('dummy_responses'))}'."
                ]
        else:
            self.response_candidates = None

    def act(self) -> Dict[Text, Any]:
        """Generates a response to the last observation.

        Returns:
            Message with reply
        """
        if not self.response_candidates:
            return {
                "id": self.getID(),
                "text": "DUMMY: No response candidates.",
                "role": self.role,
            }

        self._num_messages_sent += 1
        index = self._num_messages_sent % len(self.response_candidates)
        reply = {
            "id": self.getID(),
            "text": self.response_candidates[index],
            "role": self.role,
        }

        self._messages.append(reply)

        return reply


class WOZTutorAgent(NonMTurkAgent):
    @staticmethod
    def add_cmdline_args(parser) -> None:
        """Adds command line arguments for this agent."""
        pass

    def __init__(self, options: Opt, rules: List[Dict[Text, Any]]) -> None:
        """Initialize this agent."""
        super().__init__(options)
        self.id = "Tutor"
        self.demo_role = None
        self._num_messages_sent = 0
        self._messages = []

        self._rules = rules  # Conditions on dialogue history + responses that should be uttered if those conditions are satisfied
        self._event_history = None  # Entire dialogue history (to be observed)

    def observe(self, observation):
        self._event_history = observation

    def act(self) -> Dict[Text, Any]:
        for rule in self._rules:
            if rule.get("triggers_left", 1) > 0 and rule.get(
                "condition", self.constant_condition(False)
            )(self._event_history):
                if rule.get("probability", 1.0) < 1.0 and random.uniform(
                    0.0, 1.0
                ) > rule.get("probability", 1.0):
                    continue
                if "triggers_left" in rule:
                    rule["triggers_left"] -= 1
                return rule["message"]

        return {}

    def add_rule(
        self,
        condition: Callable,
        text: Text,
        max_times_triggered: Optional[int] = None,
        probability: float = 1.0,
    ) -> None:
        if max_times_triggered:
            self._rules.append(
                {
                    "condition": condition,
                    "message": {"text": text},
                    "triggers_left": max_times_triggered,
                    "probability": probability,
                }
            )
        else:
            self._rules.append(
                {"condition": condition, "message": {"text": "<guide>" + text},}
            )

    @staticmethod
    def num_turns_condition(
        min_num_turns: Optional[int], max_num_turns: Optional[int] = None
    ) -> Callable:
        _min_num_turns = min_num_turns or 0
        if max_num_turns is not None:
            return lambda history: (_min_num_turns <= num_turns(history) <= max_num_turns)
        else:
            return lambda history: (_min_num_turns <= num_turns(history))

    @staticmethod
    def random_turn_condition(min_num_turns: Optional[int], max_num_turns: int) -> Callable:
        assert max_num_turns > (min_num_turns or 0)
        n = random.randint(min_num_turns or 0, max_num_turns)
        return lambda history: num_turns(history) == n

    @staticmethod
    def kb_changed_condition(
        previous_api_name: Optional[Text] = None, new_api_name: Optional[Text] = None
    ) -> Callable:
        def wizard_changed_kb(history):
            if not history:
                return False
            api_name_stack = []
            for event in history[:-1]:
                if event.get("Action") == QueryCommand.command_name:
                    api_name_stack.append(event.get("API"))
                if event.get("Agent") == "User":
                    if api_name_stack:
                        api_name_stack = [api_name_stack[-1]]
            if len(api_name_stack) <= 1:
                return False
            elif previous_api_name and new_api_name:
                return (api_name_stack[-2] == previous_api_name) and (
                    api_name_stack[-1] == new_api_name
                )
            elif previous_api_name:
                return (api_name_stack[-2] == previous_api_name) and (
                    api_name_stack[-1] != previous_api_name
                )
            elif new_api_name:
                return (api_name_stack[-2] != new_api_name) and (
                    api_name_stack[-1] == new_api_name
                )
            else:
                return api_name_stack[-2] != api_name_stack[-1]

        return wizard_changed_kb

    @staticmethod
    def constant_condition(const: bool) -> Callable:
        return lambda _: const


def num_turns(history: List[Dict[Text, Any]]) -> int:
    result = 0
    for event in history:
        if event.get("Agent") == "User":
            result += 1
    return result
