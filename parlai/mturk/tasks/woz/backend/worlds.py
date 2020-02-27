#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from datetime import datetime
from typing import Text, Optional, List

from parlai.core.agents import Agent
from parlai.mturk.core.agents import (
    MTURK_DISCONNECT_MESSAGE,
    RETURN_MESSAGE,
    TIMEOUT_MESSAGE,
    MTurkAgent,
)
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
import threading

import parlai.mturk.tasks.woz.echo as echo
from parlai.mturk.tasks.woz.backend.commands import (
    command_from_message,
    UtterCommand,
    DialogueCompletedCommand,
    TaskDoneCommand,
    ReviewCommand,
)
from parlai.mturk.tasks.woz.mock import DUMMY_FORM_DESCRIPTION
from parlai.mturk.tasks.woz.protocol import (
    WORKER_COMMAND_QUERY,
    WORKER_COMMAND_COMPLETE,
    COMMAND_REVIEW,
    send_mturk_message,
    WORKER_COMMAND_DONE,
    WORKER_DISCONNECTED,
    extract_command_message,
    WORKER_SELECT_1,
    WORKER_SELECT_2,
    send_setup_command,
    WORKER_REQUEST_SUGGESTIONS,
    COMMAND_SUPPLY_SUGGESTIONS,
    WORKER_PICK_SUGGESTION,
)


def is_disconnected(act):
    return 'text' in act and act['text'] in [
        MTURK_DISCONNECT_MESSAGE,
        RETURN_MESSAGE,
        TIMEOUT_MESSAGE,
    ]


class WizardOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def block_loop(self):
        print(f'Worker {self.mturk_agent.worker_id} failed onboarding.')
        send_mturk_message(
            "Sorry, you've exceeded the maximum amount of tries to get the "
            "correct actions given your persona and the setting, and thus we "
            "don't believe you can complete the task correctly. Please return "
            "the HIT.",
            self.mturk_agent,
        )
        self.mturk_agent.mturk_manager.soft_block_worker(self.mturk_agent.worker_id)
        message = self.mturk_agent.act()
        while not is_disconnected(message):
            send_mturk_message("Please return the HIT.", self.mturk_agent)
            message = self.mturk_agent.act()
        return True

    def parley(self):
        self.mturk_agent.observe({"id": "Wizard", "text": "", "command": "setup"})
        send_mturk_message(
            "Take your time to read your task description on the left. "
            "Write 'ready' when you are ready to see an example, and press [Enter].",
            self.mturk_agent,
        )
        message = {}
        while message.get("text", "").strip().lower() != "ready":
            message = self.mturk_agent.act()
            echo.log_write(f"onboarding wizard: {message}")
            if is_disconnected(message):
                self.episodeDone = True
                return

        self.mturk_agent.passed_onboarding = True
        # if message.get("text", "") != "ready":
        #     self.block_loop()
        #     self.episodeDone = True
        #     return
        send_mturk_message(
            "Please wait for the user and join the conversation...", self.mturk_agent,
        )
        # self.mturk_agent.onboarding_turns = 1
        self.episodeDone = True

    def get_model_agent(self):
        return self.mturk_agent

    def get_task_agent(self):
        return self.mturk_agent


class UserOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def parley(self):
        self.mturk_agent.observe({"id": "User", "text": "", "command": "setup"})
        send_mturk_message(
            "Take your time to read your task description on the left. "
            "Write 'ready' when you are ready and press [Enter].",
            self.mturk_agent,
        )
        message = self.mturk_agent.act()
        echo.log_write(f"onboarding user: {message}")
        self.mturk_agent.passed_onboarding = True
        send_mturk_message(
            "Please wait for the virtual assistant to join the conversation...",
            self.mturk_agent,
        )
        self.episodeDone = True

    def get_model_agent(self):
        return self.mturk_agent

    def get_task_agent(self):
        return self.mturk_agent


SETUP_STAGE = 0
DIALOGUE_STAGE = 1
EVALUATION_STAGE = 2


class WOZWorld(MTurkTaskWorld):
    """
    Wizard-of-Oz world.
    """

    collector_agent_id = 'Moderator'

    def __init__(self, opt, agents):
        super(WOZWorld, self).__init__(opt, mturk_agent=None)
        self.knowledgebase = None
        for agent in agents:
            if agent.demo_role == 'User':
                self.user = agent
            elif agent.demo_role == 'Wizard':
                self.wizard = agent
            else:
                self.knowledgebase = agent

        self._episode_done = False
        self._stage = SETUP_STAGE
        self.events = []

        self.num_turns = -1
        self.max_turns = 300
        self.min_turns = 5

    def parley(self):
        if self._stage == SETUP_STAGE:
            self.setup_interface()
            self.tell_workers_to_start()
            self.num_turns = 0
            self._stage = DIALOGUE_STAGE
        elif self._stage == DIALOGUE_STAGE:
            self.num_turns += 1
            if self.num_turns % 2 == 1:
                self._parley_dialogue_user()
            else:
                self._parley_dialogue_wizard_and_knowledgebase()
        elif self._stage == EVALUATION_STAGE:
            self._parley_evaluation(self.user)
            self._parley_evaluation(self.wizard)
            self._episode_done = True

    def _parley_dialogue_user(self) -> None:
        user_command = command_from_message(self.user.act(), self.user)
        if isinstance(user_command, UtterCommand):
            self.wizard.observe(user_command.message)
        elif isinstance(user_command, DialogueCompletedCommand):
            self.wizard.observe(ReviewCommand().message)
            self.user.observe(ReviewCommand().message)
            send_mturk_message(
                "Thank you for chatting. Now please review your conversation.",
                self.user,
            )
            send_mturk_message(
                "The user thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the user.",
                self.wizard,
            )
            self._stage = EVALUATION_STAGE
        else:
            raise RuntimeError(
                f"User command not allowed in dialogue stage: {user_command.message}"
            )

    def _parley_dialogue_wizard_and_knowledgebase(self) -> bool:
        wizard_message, command, parameters = self.get_new_wizard_message()
        # Handle communication between the wizard and the knowledge base
        while command in [
            WORKER_COMMAND_QUERY,
            WORKER_SELECT_1,
            WORKER_SELECT_2,
            WORKER_REQUEST_SUGGESTIONS,
        ]:
            if command == WORKER_COMMAND_QUERY:
                self.knowledgebase.observe({"query": parameters})
                kb_message, _, _ = self.get_new_knowledgebase_message()
                self.wizard.observe(kb_message)
            elif command == WORKER_REQUEST_SUGGESTIONS:
                self.send_suggestions(["1", "2", "3"], self.wizard)
            wizard_message, command, parameters = self.get_new_wizard_message()

        if command and command == WORKER_PICK_SUGGESTION:
            wizard_message = {
                "id": self.wizard.id,
                "text": parameters,
            }
            self.wizard.observe(wizard_message)

        self.deal_with_wizard_command(command, parameters)

        self.user.observe(wizard_message)
        return False

    def _parley_evaluation(self, agent) -> None:
        user_command = command_from_message(agent.act(blocking=False), agent)
        if isinstance(user_command, TaskDoneCommand):
            send_mturk_message(
                "Thank you for evaluating! Goodbye.", agent,
            )
        elif isinstance(user_command, UtterCommand):
            send_mturk_message(
                "Thank you for your feedback! Please also complete the form on the left.",
                agent,
            )
        else:
            raise RuntimeError(
                f"Command not allowed for {agent.id} in evaluation stage: {user_command.message}"
            )

    @echo.echo_out(output=echo.log_write, prefix="get_new_user_message() = ")
    def get_new_user_message(self):
        message = self.user.act()
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

    @echo.echo_out(output=echo.log_write, prefix="get_new_wizard_message() = ")
    def get_new_wizard_message(self):
        message = self.wizard.act()
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

    @echo.echo_out(output=echo.log_write, prefix="get_new_knowledgebase_message() = ")
    def get_new_knowledgebase_message(self):
        message = self.knowledgebase.act()
        self.events.append(
            {"type": "KnowledgeBaseMessage", "message": message,}
        )
        return message, None, None

    def deal_with_wizard_command(
        self, command: Optional[Text], parameters: Optional[Text]
    ) -> None:
        if command is None:
            return
        elif command == WORKER_COMMAND_COMPLETE:
            self.send_command(COMMAND_REVIEW, self.wizard)
            self.send_command(COMMAND_REVIEW, self.user)
            send_mturk_message(
                "Thank you for chatting. Now please review your conversation.",
                self.wizard,
            )
            send_mturk_message(
                "The assistant thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the assistant.",
                self.user,
            )
        elif command == WORKER_COMMAND_DONE:
            send_mturk_message(
                "Thank you for evaluating! Please wait for the user to agree...",
                self.wizard,
            )
            self._episode_done = True
        elif command == WORKER_DISCONNECTED:
            send_mturk_message("Sorry, the assistant disconnected...", self.user)
            self._episode_done = True

    def deal_with_user_command(
        self, command: Optional[Text], parameters: Optional[Text]
    ) -> None:
        if command is None:
            return
        elif command == WORKER_COMMAND_COMPLETE:
            self.send_command(COMMAND_REVIEW, self.wizard)
            self.send_command(COMMAND_REVIEW, self.user)
            send_mturk_message(
                "Thank you for chatting. Now please review your conversation.",
                self.user,
            )
            send_mturk_message(
                "The user thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the user.",
                self.wizard,
            )
        elif command == WORKER_COMMAND_DONE:
            send_mturk_message(
                "Thank you for evaluating! Please wait for the assistant to agree...",
                self.user,
            )
            self._episode_done = True
        elif command == WORKER_DISCONNECTED:
            send_mturk_message("Sorry, the user disconnected...", self.user)
            self._episode_done = True

    @echo.echo_in(
        output=echo.log_write, prolog={"command": None, "recipient": (lambda a: a.id)}
    )
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
        for agent in [self.user, self.wizard]:
            send_setup_command(
                task_description=f"Dummy task description for {agent.id}",
                completion_requirements=[
                    f"Dummy requirement 1 for {agent.id}",
                    f"Dummy requirement 2 for {agent.id}",
                ],
                completion_questions=[
                    f"Dummy QA 1 for {agent.id}",
                    f"Dummy QA 2 for {agent.id}",
                ],
                form_description=DUMMY_FORM_DESCRIPTION,
                recipient=agent,
            )

    def tell_workers_to_start(self):
        send_mturk_message(
            "The assistant is ready. Go ahead, say hello!", self.user,
        )
        send_mturk_message(
            "A user has joined the chat. Please wait for him/her to start the conversation.",
            self.wizard,
        )

    def episode_done(self):
        return self._episode_done

    def shutdown(self):
        # Parallel shutdown of agents
        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        threads = []
        agents = [self.user, self.wizard, self.knowledgebase]
        mturk_agents = [agent for agent in agents if isinstance(agent, MTurkAgent)]
        for agent in mturk_agents:
            t = threading.Thread(target=shutdown_agent, args=(agent,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def review_work(self):
        # Can review the work here to accept or reject it
        # self.mturk_agent.approve_work()
        # self.mturk_agent.reject_work()
        # self.mturk_agent.pay_bonus(1000) # Pay $1000 as bonus
        # self.mturk_agent.block_worker() # Block this worker from future HITs
        pass

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {"events": self.events}

    def get_model_agent(self):
        return self.wizard  # ToDo: Don't know if this is correct

    def get_task_agent(self):
        return self.user

    def send_suggestions(self, suggestions: List[Text], wizard_agent):
        self.send_command(COMMAND_SUPPLY_SUGGESTIONS + str(suggestions), wizard_agent)
