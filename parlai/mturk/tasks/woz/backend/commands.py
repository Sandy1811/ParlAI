import json
import os
from typing import Text, Dict, Any, List, Optional, Union

from parlai.core.agents import Agent
import parlai.mturk.tasks.woz.api as api

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
        task_description: Optional[Text] = None,
        completion_requirements: Optional[List[Text]] = None,
        completion_questions: Optional[List[Text]] = None,
        form_description: Optional[Dict[Text, Any]] = None,
        role: Optional[Text] = None,
    ) -> Optional["Command"]:
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


class WorkerCommand(AgentCommand):
    def __init__(self, sender: Optional[Agent] = None):
        super(WorkerCommand, self).__init__(sender)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(sender: Agent, **kwargs,) -> Optional["Command"]:
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


class BackendCommand(Command):
    def __init__(self):
        super(BackendCommand, self).__init__(sender=None)

    @property
    def message(self) -> Dict[Text, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        raise NotImplementedError()


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


class SetupCommand(BackendCommand):
    def __init__(
        self,
        task_description: Text,
        completion_requirements: List[Text],
        form_description: Dict[Text, Any],
        completion_questions: List[Text],
        role: Text,
    ) -> None:
        super(SetupCommand, self).__init__()
        self._command_name = all_constants()["back_to_front"]["command_setup"]

        self._task_description = task_description
        self._completion_requirements = completion_requirements
        self._form_description = form_description
        self._completion_questions = completion_questions
        self._role = role

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
        sender: Agent,
        task_description: Optional[Text] = None,
        completion_requirements: Optional[List[Text]] = None,
        completion_questions: Optional[List[Text]] = None,
        form_description: Optional[Dict[Text, Any]] = None,
        role: Optional[Text] = None,
        **kwargs,
    ) -> Optional["Command"]:
        return SetupCommand(
            task_description=task_description,
            completion_requirements=completion_requirements,
            completion_questions=completion_questions,
            form_description=form_description,
            role=role,
        )


class ReviewCommand(BackendCommand):
    def __init__(self) -> None:
        super(ReviewCommand, self).__init__()
        self._command_name = all_constants()["back_to_front"]["command_review"]

    @property
    def message(self) -> Dict[Text, Any]:
        return {
            "id": recipient.id,
            "text": "",
            "command": self._command_name,
        }

    @staticmethod
    def from_message(sender: Agent, **kwargs,) -> Optional["Command"]:
        return ReviewCommand()


class QueryCommand(WizardCommand):
    def __init__(self, query: Text, sender: Agent) -> None:
        super(QueryCommand, self).__init__(sender)
        self._command_name = "query"

        self._query = query

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
        return self._parse(self._query)

    @property
    def topic(self) -> Text:
        return "Apartments"  # ToDo: Implement topic property

    def _parse_old(
        self, text: Text
    ) -> List[Dict[Text, Any]]:  # ToDo: remove when front end sends json
        return eval(text)

    def _parse_new(self, text: Text) -> List[Dict[Text, Any]]:
        constraints = eval(text)
        result = [
            {name: eval(expr)}
            for constraint in constraints
            for name, expr in constraint.items()
        ]
        if result:
            return result
        else:
            return [{}]

    def _parse_json(self, constraints: List[Dict[Text, Text]]) -> List[Dict[Text, Any]]:
        result = [
            {name: eval(expr)}
            for constraint in constraints
            for name, expr in constraint.items()
        ]
        return result

    def _parse(self, text: Union[Text, List]) -> List[Dict[Text, Any]]:
        if isinstance(text, list):
            return self._parse_json(text)
        else:
            if text.startswith("["):
                return self._parse_new(text)
            else:
                return self._parse_old(text)


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


class TaskDoneCommand(WorkerCommand):
    def __init__(self, sender: Agent) -> None:
        super(TaskDoneCommand, self).__init__(sender)
        self._command_name = "complete"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return TaskDoneCommand(sender=sender)


class SelectPrimaryCommand(WizardCommand):
    def __init__(self, sender: Agent) -> None:
        super(SelectPrimaryCommand, self).__init__(sender)
        self._command_name = "complete"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return SelectPrimaryCommand(sender=sender)


class SelectSecondaryCommand(WizardCommand):
    def __init__(self, sender: Agent) -> None:
        super(SelectSecondaryCommand, self).__init__(sender)
        self._command_name = "complete"

    @property
    def message(self) -> Dict[Text, Any]:
        return {"id": self._sender.id, "text": ""}

    @staticmethod
    def from_message(sender: Agent, **kwargs) -> Optional["Command"]:
        return SelectSecondaryCommand(sender=sender)


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
