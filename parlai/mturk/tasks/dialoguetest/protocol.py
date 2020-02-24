# Communication protocol between back- and frontend
from typing import Text, Optional, Dict, Any, Tuple, List

from parlai.core.agents import Agent


COMMAND_SETUP = "setup"
COMMAND_REVIEW = "review"

MESSAGE_COMPLETE_PREFIX = "<complete>"
MESSAGE_DONE_PREFIX = "<done>"
MESSAGE_QUERY_PREFIX = "? "

WORKER_COMMAND_COMPLETE = "complete"
WORKER_COMMAND_DONE = "done"
WORKER_COMMAND_QUERY = "query"

WORKER_DISCONNECTED = "disconnect"

SYSTEM_ID = "MTurk System"
WIZARD_ID = "Assistant"
USER_ID = "User"
KNOWLEDGE_BASE_ID = "KB"


def extract_command_message(
    message: Optional[Dict[Text, Any]]
) -> Tuple[Optional[Text], Optional[Text]]:
    command = None
    parameters = None
    if message and message.get("text"):
        text = message.get("text", "")
        if text.startswith(MESSAGE_COMPLETE_PREFIX):
            command = WORKER_COMMAND_COMPLETE
            parameters = None
        elif text.startswith(MESSAGE_DONE_PREFIX):
            command = WORKER_COMMAND_DONE
            parameters = text[len(MESSAGE_DONE_PREFIX) :].strip()
        elif text.startswith(MESSAGE_QUERY_PREFIX):
            command = WORKER_COMMAND_QUERY
            parameters = text[len(MESSAGE_QUERY_PREFIX) :].strip()
        elif text == "[DISCONNECT]":
            command = WORKER_DISCONNECTED
            parameters = None

    return command, parameters


def send_mturk_message(text: Text, recipient: Agent) -> None:
    message = {"id": SYSTEM_ID, "text": text}
    recipient.observe(message)


def send_kb_message(text: Text, recipient: Agent) -> None:
    recipient.observe({"id": KNOWLEDGE_BASE_ID, "kb_item": text})


def send_setup_command(
    task_description: Text,
    completion_requirements: List[Text],
    form_description: Dict[Text, Any],
    recipient: Agent,
):
    recipient.observe(
        {
            "id": SYSTEM_ID,
            "task_description": task_description,
            "completion_requirements": completion_requirements,
            "form_description": form_description,
        }
    )
