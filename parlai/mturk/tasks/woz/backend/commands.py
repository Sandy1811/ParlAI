import json
import os
from typing import Text, Dict, Any, List, Optional, Union, Tuple

from parlai.core.agents import Agent
import parlai.mturk.tasks.woz.knowledgebase.api as api
from parlai.mturk.tasks.woz.mock import DUMMY_FORM_DESCRIPTION

__all_constants = None


def all_constants():
    global __all_constants
    if not __all_constants:
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "constants.json"),
            "r",
        ) as file:
            __all_constants = json.load(file)
    return __all_constants


class Command:
    def __init__(self, sender: Optional[Agent] = None) -> None:
        self._command_name = None
        self._sender = sender

    @property
    def sender(self):
        return self._sender

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(
        sender: Agent,
        text: Optional[Text] = None,
        extracted_from_text: Optional[Text] = None,
        suggestions: Optional[List[Text]] = None,
        task_description: Optional[Text] = None,
        completion_requirements: Optional[List[Text]] = None,
        completion_questions: Optional[List[Text]] = None,
        form_description: Optional[Dict[Text, Any]] = None,
        role: Optional[Text] = None,
    ) -> Optional["Command"]:
        raise NotImplementedError()

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError()


class AgentCommand(Command):
    def __init__(self, sender: Optional[Agent] = None):
        super(AgentCommand, self).__init__(sender)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        raise NotImplementedError()

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError()


class WorkerCommand(AgentCommand):
    def __init__(self, sender: Optional[Agent] = None):
        super(WorkerCommand, self).__init__(sender)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(sender: Agent, **kwargs,) -> Optional["Command"]:
        raise NotImplementedError()

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError()


class WizardCommand(WorkerCommand):
    def __init__(self, sender: Optional[Agent] = None):
        super(WizardCommand, self).__init__(sender)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(
        sender: Agent,
        text: Optional[Text] = None,
        extracted_from_text: Optional[Text] = None,
    ) -> Optional["Command"]:
        raise NotImplementedError()

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        return {
            "Agent": self._sender.id,
            "Action": self._command_name
        }


class BackendCommand(Command):
    def __init__(self):
        super(BackendCommand, self).__init__(sender=None)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        raise NotImplementedError()

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        return None


class UtterCommand(WorkerCommand):
    def __init__(self, text: Text, sender: Agent):
        super(UtterCommand, self).__init__(sender)
        self._command_name = "utter"

        self._text = text

    @property
    def message(self) -> Dict[Text, Any]:
        return {
            "id": self._sender.id,
            "text": self._text,
        }

    @staticmethod
    def from_message(
        sender: Agent, text: Optional[Text] = None, **kwargs
    ) -> Optional["Command"]:
        if text is None:
            raise ValueError("No text given")
        return UtterCommand(text=text, sender=sender)

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        return {
            "Agent": self._sender.id,
            "Action": self._command_name,
            "Text": self._text
        }


class SetupCommand(BackendCommand):
    def __init__(
        self,
        scenario: Text,
        role: Text,
    ) -> None:
        super(SetupCommand, self).__init__()
        self._command_name = all_constants()["back_to_front"]["command_setup"]

        scenario_file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "scenarios",
            scenario + ".json",
        )
        if not os.path.exists(scenario_file_name):
            raise FileNotFoundError(f"Could not find '{scenario_file_name}'.")
        with open(scenario_file_name, "r", ) as file:
            print(f"loading {scenario_file_name}")
            scenario = json.load(file)

        self._command_name = all_constants()["back_to_front"]["command_setup"]
        image_not_found_url = "https://stockpictures.io/wp-content/uploads/2020/01/image-not-found-big.png"

        try:
            form_description = {}
            for api_name in scenario["api_names"]:
                api_file_name = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "knowledgebase",
                    "apis",
                    api_name + ".json",
                )
                with open(api_file_name, "r") as file:
                    api_description = json.load(file)
                form_description[api_name] = api_description
                form_description[api_name]["schema_url"] = scenario["schema_urls"].get(api_name, image_not_found_url)

            self._task_description = scenario["instructions"][role]["task_description"]
            self._completion_requirements = scenario["instructions"][role]["completion_requirements"]
            self._form_description = form_description
            self._completion_questions = scenario["instructions"][role]["completion_questions"]
            self._role = role
        except KeyError as error:
            raise ImportError(f"Invalid scenario file '{scenario_file_name}': {error}.")

    @property
    def message(self) -> Dict[Text, Any]:
        return {
            "id": self._role,
            "text": "",
            "command": self._command_name,
            "task_description": self._task_description,
            "completion_requirements": self._completion_requirements,
            "completion_questions": self._completion_questions,
            "form_description": self._form_description,
        }

    @staticmethod
    def from_message(
        **kwargs,
    ) -> Optional["Command"]:
        raise RuntimeError("SetupCommand cannot be created from message.")


class ReviewCommand(BackendCommand):
    def __init__(self, recipient: Agent) -> None:
        super(ReviewCommand, self).__init__()
        self._command_name = all_constants()["back_to_front"]["command_review"]
        self._recipient = recipient

    @property
    def message(self) -> Dict[Text, Any]:
        return {
            # "id": self._recipient.id,
            "text": "",
            "command": self._command_name,
        }

    @staticmethod
    def from_message(sender: Agent, **kwargs,) -> Optional["Command"]:
        return ReviewCommand(recipient=sender)


class QueryCommand(WizardCommand):

    command_name = "query"

    def __init__(self, query: Text, sender: Agent) -> None:
        super(QueryCommand, self).__init__(sender)
        self._command_name = self.command_name

        self._query = query
        self._constraints, self._api_name = self._parse(self._query)

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": "", "query": self._query}

    @staticmethod
    def from_message(
        sender: Agent, extracted_from_text: Optional[Text] = None, **kwargs
    ) -> Optional["Command"]:
        if extracted_from_text is None:
            raise ValueError("Nothing extracted from text for knowledge base")
        return QueryCommand(query=extracted_from_text, sender=sender)

    @property
    def constraints(self) -> List[Dict[Text, Any]]:
        return self._constraints

    @property
    def api_name(self) -> Text:
        return self._api_name

    def _parse(self, text: Text) -> Tuple[List[Dict[Text, Any]], Text]:
        data = eval(text)
        assert isinstance(data, dict)
        assert "constraints" in data
        assert "db" in data

        constraints = [
            {name: eval(expr)}
            for constraint in data["constraints"]
            for name, expr in constraint.items()
        ]

        return constraints, data["db"]

    @property
    def event(self) -> Optional[Dict[Text, Any]]:
        return {
            "Agent": self._sender.id,
            "Action": self._command_name,
            "Constraints": self._constraints,
            "API": self._api_name
        }


class DialogueCompletedCommand(WorkerCommand):
    def __init__(self, sender: Agent) -> None:
        super(DialogueCompletedCommand, self).__init__(sender)
        self._command_name = "complete"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return DialogueCompletedCommand(sender=sender)

    def event(self) -> Optional[Dict[Text, Any]]:
        return {
            "Agent": self._sender.id,
            "Action": self._command_name,
        }


class TaskDoneCommand(WorkerCommand):
    def __init__(self, sender: Agent) -> None:
        super(TaskDoneCommand, self).__init__(sender)
        self._command_name = "done"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return TaskDoneCommand(sender=sender)


class SelectPrimaryCommand(WizardCommand):
    def __init__(self, sender: Agent) -> None:
        super(SelectPrimaryCommand, self).__init__(sender)
        self._command_name = "select_primary"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return SelectPrimaryCommand(sender=sender)


class SelectSecondaryCommand(WizardCommand):
    def __init__(self, sender: Agent) -> None:
        super(SelectSecondaryCommand, self).__init__(sender)
        self._command_name = "select_secondary"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return SelectSecondaryCommand(sender=sender)


class RequestSuggestionsCommand(WizardCommand):
    def __init__(self, sender: Agent, query_text: Text) -> None:
        super(RequestSuggestionsCommand, self).__init__(sender)
        self._command_name = "request_suggestions"
        self._query = query_text

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": self._query}

    @staticmethod
    def from_message(sender: Agent, text: Optional[Text] = None, **kwargs) -> Optional["Command"]:
        return RequestSuggestionsCommand(sender=sender, query_text=(text or ""))

    @property
    def query(self) -> Text:
        return self._query


class SupplySuggestionsCommand(BackendCommand):
    def __init__(self, recipient: Agent, suggestions: List[Text]) -> None:
        super(SupplySuggestionsCommand, self).__init__()
        self._command_name = all_constants()["back_to_front"]["command_supply_suggestions"]
        self._recipient = recipient
        self._suggestions = suggestions

    @property
    def message(self) -> Dict[Text, Any]:
        return {
            "id": self._recipient.id,
            "text": "",
            "command": self._command_name + str(self._suggestions),
        }

    @staticmethod
    def from_message(sender: Agent, suggestions: Optional[List[Text]] = None, **kwargs,) -> Optional["Command"]:
        return SupplySuggestionsCommand(recipient=sender, suggestions=suggestions)


class PickSuggestionCommand(WizardCommand):
    def __init__(self, sender: Agent, chosen_text: Text) -> None:
        super(PickSuggestionCommand, self).__init__(sender)
        self._command_name = "pick_suggestion"
        self._text = chosen_text

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": self._text}

    @staticmethod
    def from_message(sender: Agent, extracted_from_text: Optional[Text] = None, **kwargs) -> Optional["Command"]:
        if not extracted_from_text:
            raise ValueError(f"Chosen message is empty")
        return PickSuggestionCommand(sender=sender, chosen_text=extracted_from_text)


def command_from_message(
    message: Optional[Dict[Text, Any]], sender: Optional[Agent]
) -> Optional[Command]:
    if message is None:
        return None

    text = message.get("text", "")

    constants = all_constants()
    prefixes = {
        constants["front_to_back"]["query_prefix"]: QueryCommand,
        constants["front_to_back"]["complete_prefix"]: DialogueCompletedCommand,
        constants["front_to_back"]["done_prefix"]: TaskDoneCommand,
        constants["front_to_back"]["select_kb_entry_prefix"]: SelectPrimaryCommand,
        constants["front_to_back"][
            "select_reference_kb_entry_prefix"
        ]: SelectSecondaryCommand,
        constants["front_to_back"]["request_suggestions_prefix"]: RequestSuggestionsCommand,
        constants["front_to_back"]["pick_suggestion_prefix"]: PickSuggestionCommand,
        constants["front_to_back"]["query_prefix"]: QueryCommand,
    }

    # Add information extracted from the `text` property (magic strings)
    command = UtterCommand
    _message = message
    for _prefix, _command in prefixes.items():
        if text.startswith(_prefix):
            command = _command
            _message["extracted_from_text"] = text[len(_prefix) :]
            break

    return command.from_message(sender, **_message)
