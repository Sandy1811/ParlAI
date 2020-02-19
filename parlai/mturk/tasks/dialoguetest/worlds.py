#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from datetime import datetime
from typing import Text, Union, Dict, Any, Optional, Tuple

from parlai.core.agents import Agent
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
import threading


def log_write_act(index: int, agent_name: Text, act) -> None:
    # with open("/Users/johannes/TESTLOG.log", "a+") as file:
    #     time = str(datetime.now().isoformat())
    #     file.write(f"{time}\t{index:2}\t{agent_name}\t{act}\n")
    pass


def log_write(message: Text) -> None:
    # with open("/Users/johannes/TESTLOG.log", "a+") as file:
    #     time = str(datetime.now().isoformat())
    #     file.write(f"{time}\t{message}\n")
    pass


class WizardOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def parley(self):
        self.mturk_agent.observe(
            {"id": self.mturk_agent.id, "text": "", "command": "setup"}
        )
        ad = {
            "id": 'MTurk System',
            "text": f"Please wait for the user to join the conversation...",
        }
        self.mturk_agent.observe(ad)
        # response = self.mturk_agent.act()
        # log_write_act(-2, self.mturk_agent.id, response)
        self.episodeDone = True


class UserOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def parley(self):
        self.mturk_agent.observe(
            {"id": self.mturk_agent.id, "text": "", "command": "setup"}
        )
        ad = {
            "id": 'MTurk System',
            "text": "Please wait for the virtual assistant to join the conversation...",
        }
        self.mturk_agent.observe(ad)
        # response = self.mturk_agent.act()
        # log_write_act(-1, self.mturk_agent.id, response)
        self.episodeDone = True


COMMAND_SETUP = "setup"
COMMAND_REVIEW = "review"

MESSAGE_COMPLETE_PREFIX = "<complete>"
MESSAGE_DONE_PREFIX = "<done>"
MESSAGE_QUERY_PREFIX = "? "

WORKER_COMMAND_COMPLETE = "complete"
WORKER_COMMAND_DONE = "done"
WORKER_COMMAND_QUERY = "query"

WORKER_DISCONNECTED = "disconnect"


def send_mturk_message(text: Text, recipient: Agent) -> None:
    message = {"id": "MTurk System", "text": text}
    recipient.observe(message)


def extract_command_message(
    message: Optional[Dict[Text, Any]]
) -> Tuple[Optional[Text], Optional[Text]]:
    log_write(f"extract_command_message({message})")
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


class WOZWorld(MTurkTaskWorld):
    """
    Wizard-of-Oz world.
    """

    collector_agent_id = 'Moderator'

    def __init__(self, opt, agents):
        self.mturk_agents = agents
        self.kb_agent = None
        log_write(f"Initializing world with agents: {agents}")
        for agent in agents:
            if agent.demo_role == 'User':
                self.user_agent = agent
            elif agent.demo_role == 'Wizard':
                self.wizard_agent = agent
            else:  # Knowledge Base
                self.kb_agent = agent
        self.episodeDone = False
        self.turns = 0
        self.evaluating = False
        self.events = []

        self.num_turns = -1
        self.max_turns = 300
        self.min_turns = 5

    def parley(self):
        """
        Let the user and the wizard have a turn each.
        """

        if self.num_turns < 0:
            log_write_act(0, "None", "world started")
            self.setup_interface()
            self.tell_workers_to_start()
            self.num_turns = 0
            return

        self.num_turns += 1

        user_message, command, parameters = self.get_new_user_message()
        log_write_act(self.num_turns, "User", user_message)
        self.deal_with_user_command(command, parameters)

        if not self.evaluating:
            self.wizard_agent.observe(user_message)

        wizard_message, command, parameters = self.get_new_wizard_message()
        log_write_act(self.num_turns, "Wizard", wizard_message)
        self.deal_with_wizard_command(command, parameters)

        if not self.evaluating:
            self.user_agent.observe(wizard_message)

        if self.num_turns >= self.max_turns:
            self.episodeDone = True

    def get_new_user_message(self):
        message = self.user_agent.act()
        command, parameters = extract_command_message(message)
        self.events.append(
            {
                "type": "UserMessage",
                "message": message,
                "command": command,
                "parameters": parameters,
            }
        )
        return message, command, parameters

    def get_new_wizard_message(self):
        message = self.wizard_agent.act()
        command, parameters = extract_command_message(message)
        self.events.append(
            {
                "type": "WizardMessage",
                "message": message,
                "command": command,
                "parameters": parameters,
            }
        )
        return message, command, parameters

    def get_new_knowledgebase_message(self):
        message = self.kb_agent.act()
        self.events.append(
            {"type": "KnowledgeBaseMessage", "message": message,}
        )
        return message, None, None

    def deal_with_wizard_command(
        self, command: Optional[Text], parameters: Optional[Text]
    ) -> None:
        if command is None:
            return
        elif command == WORKER_COMMAND_QUERY and self.kb_agent:
            # Handle communication between the wizard and the knowledge base
            while command and command == WORKER_COMMAND_QUERY:
                self.kb_agent.observe({"query": parameters})
                kb_message, _, _ = self.get_new_knowledgebase_message()
                self.wizard_agent.observe(kb_message)
                wizard_message, command, parameters = self.get_new_wizard_message()
        elif command == WORKER_COMMAND_COMPLETE:
            self.send_command(COMMAND_REVIEW, self.wizard_agent)
            self.send_command(COMMAND_REVIEW, self.user_agent)
            self.evaluating = True
            send_mturk_message("Thank you for chatting. Now please review your conversation.", self.wizard_agent)
            send_mturk_message("The assistant thinks that the task is complete. Please review your conversation.", self.user_agent)
        elif command == WORKER_COMMAND_DONE:
            log_write("Wizard is DONE")
            send_mturk_message("Thank you for evaluating! Please wait for the user to agree...", self.wizard_agent)
            self.episodeDone = True
        elif command == WORKER_DISCONNECTED:
            log_write("Wizard DISCONNECTED")
            send_mturk_message("Sorry, the assistant disconnected...", self.user_agent)
            self.episodeDone = True

    def deal_with_user_command(
        self, command: Optional[Text], parameters: Optional[Text]
    ) -> None:
        if command is None:
            return
        elif command == WORKER_COMMAND_COMPLETE:
            self.send_command(COMMAND_REVIEW, self.wizard_agent)
            self.send_command(COMMAND_REVIEW, self.user_agent)
            send_mturk_message("Thank you for chatting. Now please review your conversation.", self.user_agent)
            send_mturk_message("The user thinks that the task is complete. Please review your conversation.",
                               self.wizard_agent)
        elif command == WORKER_COMMAND_DONE:
            log_write("User is DONE")
            send_mturk_message("Thank you for evaluating! Please wait for the assistant to agree...", self.user_agent)
            self.episodeDone = True
        elif command == WORKER_DISCONNECTED:
            log_write("User is DISCONNECTED")
            send_mturk_message("Sorry, the user disconnected...", self.user_agent)
            self.episodeDone = True

    def send_command(self, command: Text, recipient: Agent) -> None:
        self.events.append(
            {"type": "WorldCommand", "command": command, "recipient": recipient.id,}
        )
        message = {
            "id": recipient.id,
            "text": "",
            "command": command,
        }
        recipient.observe(message)

    def setup_interface(self):
        for agent in [self.user_agent, self.wizard_agent]:
            self.send_command(COMMAND_SETUP, agent)

    def tell_workers_to_start(self):
        send_mturk_message(
            "The assistant is ready. Go ahead, say hello!", self.user_agent,
        )
        send_mturk_message(
            "A user has joined the chat. Please wait for him/her to start the conversation.",
            self.wizard_agent,
        )

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        # Parallel shutdown of agents
        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        threads = []
        for agent in self.mturk_agents:
            t = threading.Thread(target=shutdown_agent, args=(agent,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def review_work(self):
        # Can review the work here to accept or reject it
        pass

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {"events": self.events}
