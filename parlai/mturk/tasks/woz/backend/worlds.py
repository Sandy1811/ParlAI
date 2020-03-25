#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from typing import Text, List, Dict, Any, Optional

from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.mturk.core import shared_utils, mturk_utils
from parlai.mturk.core.agents import (
    MTURK_DISCONNECT_MESSAGE,
    RETURN_MESSAGE,
    TIMEOUT_MESSAGE,
    MTurkAgent,
)
from parlai.mturk.core.shared_utils import print_and_log
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
import threading

import parlai.mturk.tasks.woz.echo as echo
from parlai.mturk.tasks.woz.backend.agents import (
    WOZKnowledgeBaseAgent,
    WOZInstructorAgent,
    WOZWizardIntroAgent,
)
from parlai.mturk.tasks.woz.backend.commands import (
    command_from_message,
    all_constants,
    UtterCommand,
    DialogueCompletedCommand,
    TaskDoneCommand,
    ReviewCommand,
    QueryCommand,
    SelectPrimaryCommand,
    SelectSecondaryCommand,
    RequestSuggestionsCommand,
    PickSuggestionCommand,
    SupplySuggestionsCommand,
    SetupCommand,
    GuideCommand,
    SilentCommand,
)


def is_disconnected(act):
    return 'text' in act and act['text'] in [
        MTURK_DISCONNECT_MESSAGE,
        RETURN_MESSAGE,
        TIMEOUT_MESSAGE,
    ]


def send_mturk_message(text: Text, recipient: Agent) -> None:
    message = {"id": all_constants()["agent_ids"]["system_id"], "text": text}
    recipient.observe(message)


def send_setup_command(
    task_description: Text,
    completion_requirements: List[Text],
    form_description: Dict[Text, Any],
    completion_questions: List[Text],
    recipient: Agent,
):
    recipient.observe(
        {
            "id": recipient.id,
            "text": "",
            "command": all_constants()["back_to_front"]["command_setup"],
            "task_description": task_description,
            "completion_requirements": completion_requirements,
            "completion_questions": completion_questions,
            "form_description": form_description,
        }
    )


class WizardOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def __init__(self, opt: Opt, mturk_agent: Agent):
        super(WizardOnboardingWorld, self).__init__(opt, mturk_agent=mturk_agent)
        self._scenario = opt.get("scenario")
        assert self._scenario

    def parley(self):
        setup = SetupCommand(scenario=self._scenario, role="Wizard")
        self.mturk_agent.observe(setup.message)
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

    def __init__(self, opt: Opt, mturk_agent: Agent):
        super(UserOnboardingWorld, self).__init__(opt, mturk_agent=mturk_agent)
        self._scenario = opt.get("scenario")
        assert self._scenario

    def parley(self):
        setup = SetupCommand(scenario=self._scenario, role="User")
        self.mturk_agent.observe(setup.message)
        self.mturk_agent.observe(
            GuideCommand(
                "Take your time to read your task description on the left. "
                "Write 'ready' when you are ready and press [Enter]."
            ).message
        )
        message = self.mturk_agent.act()
        echo.log_write(f"onboarding user: {message}")
        self.mturk_agent.passed_onboarding = True
        self.mturk_agent.observe(
            GuideCommand(
                "Please wait for the virtual assistant to join the conversation..."
            ).message
        ),
        self.episodeDone = True

    def get_model_agent(self):
        return self.mturk_agent

    def get_task_agent(self):
        return self.mturk_agent


SETUP_STAGE = 0
DIALOGUE_STAGE = 1
EVALUATION_STAGE = 2
END_STAGE = 3


class WOZWorld(MTurkTaskWorld):
    """
    Wizard-of-Oz world.
    """

    def __init__(self, opt, agents, observers: Optional[List[Agent]] = None):
        super(WOZWorld, self).__init__(opt, mturk_agent=None)
        self.observers = observers or []
        self.knowledgebase = None
        self.user = None
        self.wizard = None
        for agent in agents:
            if agent.demo_role == "User":
                self.user = agent
            elif agent.demo_role == "Wizard":
                self.wizard = agent
            elif agent.demo_role == "KnowledgeBase":
                self.knowledgebase = agent

        self._scenario = opt.get("scenario")

        assert self.user
        assert self.wizard
        assert self._scenario

        self._episode_done = False
        self._stage = SETUP_STAGE
        self._received_evaluations = 0
        self.events = []

        self.num_turns = 1

        self._primary_kb_item = None
        self._secondary_kb_item = None

    def parley(self):
        if self._stage == SETUP_STAGE:
            self.wizard.observe(
                SetupCommand(scenario=self._scenario, role="Wizard").message
            )
            self.user.observe(
                SetupCommand(scenario=self._scenario, role="User").message
            )
            self.tell_workers_to_start()
            self.num_turns = 0
            self._stage = DIALOGUE_STAGE
        elif self._stage == DIALOGUE_STAGE:
            self._parley_observers()
            if self.num_turns % 2 == 0:
                self.num_turns += self._parley_dialogue_user()
            else:
                self.num_turns += self._parley_dialogue_wizard_and_knowledgebase()
        elif self._stage == EVALUATION_STAGE:
            self._parley_evaluation(self.user)
            self._parley_evaluation(self.wizard)
            self._stage = END_STAGE
        elif self._stage == END_STAGE:
            if self._received_evaluations >= 2:
                self._episode_done = True

    def _parley_observers(self) -> None:
        for observer in self.observers:
            observer.observe(self.events)
            message_to_user, message_to_wizard = observer.act()
            if message_to_user:
                self.user.observe(message_to_user)
            if message_to_wizard:
                self.wizard.observe(message_to_wizard)

    def _parley_dialogue_user(self) -> int:
        user_command = command_from_message(self.user.act(), self.user)
        self.events.append(user_command.event)
        if isinstance(user_command, UtterCommand):
            self.wizard.observe(user_command.message)
            return 1
        elif isinstance(user_command, SilentCommand):
            return 1
        elif isinstance(user_command, DialogueCompletedCommand):
            self.wizard.observe(ReviewCommand(self.wizard).message)
            self.user.observe(ReviewCommand(self.user).message)
            self.user.observe(
                GuideCommand(
                    "Thank you for chatting. Now please review your conversation."
                ).message
            )
            self.wizard.observe(
                GuideCommand(
                    "The user thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the user."
                ).message
            )
            self._stage = EVALUATION_STAGE
            return 1
        else:
            raise RuntimeError(
                f"User command not allowed in dialogue stage: {user_command.message}"
            )

    def _parley_dialogue_wizard_and_knowledgebase(self) -> int:
        wizard_command = command_from_message(self.wizard.act(), self.wizard)
        self.store_wizard_event(wizard_command.event)

        if isinstance(wizard_command, UtterCommand):
            self.user.observe(wizard_command.message)
            return 1
        elif isinstance(wizard_command, SilentCommand):
            return 1
        elif isinstance(wizard_command, QueryCommand):
            self.knowledgebase.observe(wizard_command)
            kb_message = self.knowledgebase.act()
            self._primary_kb_item = kb_message.get("example_item")
            self._secondary_kb_item = None
            # self.events.append(kb_message.event)
            self.wizard.observe(kb_message)
            return 0
        elif isinstance(wizard_command, DialogueCompletedCommand):
            self.wizard.observe(ReviewCommand(self.wizard).message)
            self.user.observe(ReviewCommand(self.user).message)
            self.wizard.observe(
                GuideCommand(
                    "Thank you for chatting. Now please review your conversation."
                ).message
            )
            self.user.observe(
                GuideCommand(
                    "The assistant thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the assistant."
                ).message
            )
            self._stage = EVALUATION_STAGE
            return 1
        elif isinstance(wizard_command, SelectPrimaryCommand):
            self._primary_kb_item = wizard_command.item
            self._secondary_kb_item = None
            return 0
        elif isinstance(wizard_command, SelectSecondaryCommand):
            self._secondary_kb_item = wizard_command.item
            return 0
        elif isinstance(wizard_command, RequestSuggestionsCommand):
            suggestions = ["message 1", "message 2"]
            self.wizard.observe(
                SupplySuggestionsCommand(self.wizard, suggestions).message
            )
            return 0
        elif isinstance(wizard_command, PickSuggestionCommand):
            self.wizard.observe(wizard_command.message)
            self.user.observe(wizard_command.message)
            return 1
        else:
            print_and_log(
                45,
                f"Wizard command not allowed in dialogue stage: {wizard_command.message}",
                True,
            )
            raise RuntimeError(
                f"Wizard command not allowed in dialogue stage: {wizard_command.message}"
            )

    def _parley_evaluation(self, agent) -> None:

        if not isinstance(agent, MTurkAgent):
            self._received_evaluations += 1
            return

        while True:
            command = command_from_message(agent.act(blocking=False), agent)

            if isinstance(command, UtterCommand):
                agent.observe(
                    GuideCommand(
                        "Thank you for your feedback! Please also complete the form on the left."
                    ).message
                )
            elif isinstance(command, TaskDoneCommand):
                agent.observe(
                    GuideCommand(
                        "Thank you for evaluating! Goodbye. (You may have to wait for your partner to confirm.)"
                    ).message
                )
                self._received_evaluations += 1
                return
            elif command is None:
                # Happens when `agent.act()` returns `None` (can happen since `blocking=False`)
                time.sleep(shared_utils.THREAD_SHORT_SLEEP)
            else:
                raise RuntimeError(
                    f"Command {type(command)} not allowed for {agent.id} in evaluation stage: {command.message}"
                )

    def store_wizard_event(self, event):
        _event = event
        _event["PrimaryItem"] = self._primary_kb_item
        _event["SecondaryItem"] = self._secondary_kb_item
        self.events.append(_event)

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

    def tell_workers_to_start(self):
        self.user.observe(
            GuideCommand("The assistant is ready. Go ahead, say hello!").message
        )
        self.wizard.observe(
            GuideCommand(
                "A user has joined the chat. Please wait for him/her to start the conversation."
            ).message
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
        return {
            "Events": self.events,
            "WizardWorkerID": self.wizard.worker_id,
            "UserWorkerID": self.user.worker_id if hasattr(self.user, "worker_id") else None,
        }

    def get_model_agent(self):
        return self.wizard  # ToDo: Don't know if this is correct

    def get_task_agent(self):
        return self.user

    def send_suggestions(self, suggestions: List[Text], wizard_agent):
        self.send_command(
            all_constants()["back_to_front"]["command_supply_suggestions"]
            + str(suggestions),
            wizard_agent,
        )

    @staticmethod
    def add_cmdline_args(parser):
        parser = parser.add_argument_group('WOZWorld arguments')
        parser.add_argument(
            "--scenario", type=str, default="book_ride_tutorial", help="Scenario name",
        )


class WOZWizardTutorialWorld(MTurkTaskWorld):
    def __init__(
        self,
        opt,
        agents,
        observers: Optional[List[Agent]] = None,
        qualification_on_success: Optional[Text] = None,
    ) -> None:
        super(WOZWizardTutorialWorld, self).__init__(opt, mturk_agent=None)
        self.opt = opt
        self.observers = observers or []
        self.knowledgebase = None
        self.tutor = None
        self.wizard = None
        for agent in agents:
            if agent.demo_role == "User":
                self.tutor = agent
            elif agent.demo_role == "Wizard":
                self.wizard = agent
            elif agent.demo_role == "KnowledgeBase":
                self.knowledgebase = agent

        self._scenario = opt.get("scenario")
        self._qualification_on_success = qualification_on_success

        assert self.tutor
        assert self.wizard
        assert self._scenario

        self._episode_done = False
        self._stage = SETUP_STAGE
        self._received_evaluations = 0
        self.events = []

        self.num_turns = 1

        self._primary_kb_item = None
        self._secondary_kb_item = None

    def parley(self):
        if self._stage == SETUP_STAGE:
            self.wizard.observe(
                SetupCommand(scenario=self._scenario, role="Wizard").message
            )
            self.num_turns = 0
            self._stage = DIALOGUE_STAGE
        elif self._stage == DIALOGUE_STAGE:
            if self.num_turns % 2 == 0:
                self.num_turns += self._parley_tutor()
            else:
                self.num_turns += self._parley_wizard()
        elif self._stage == EVALUATION_STAGE:
            if not self.tutor.worker_succeeded:
                self.block_loop()
            self._stage = END_STAGE
        elif self._stage == END_STAGE:
            self._episode_done = True

    def _parley_tutor(self) -> int:
        tutor_command = command_from_message(self.tutor.act(), self.tutor)
        self.store_tutor_event(tutor_command.event)

        if isinstance(tutor_command, DialogueCompletedCommand):
            self._stage = EVALUATION_STAGE
            return 1
        elif isinstance(tutor_command, SilentCommand):
            return 1
        else:
            self.wizard.observe(tutor_command.message)
            return 0

    def _parley_wizard(self) -> int:
        wizard_command = command_from_message(self.wizard.act(), self.wizard)
        self.store_wizard_event(wizard_command.event)

        if isinstance(wizard_command, UtterCommand):
            return 1
        elif isinstance(wizard_command, SilentCommand):
            return 1
        elif isinstance(wizard_command, QueryCommand):
            self.knowledgebase.observe(wizard_command)
            kb_message = self.knowledgebase.act()
            self._primary_kb_item = kb_message.get("example_item")
            self._secondary_kb_item = None
            # self.events.append(kb_message.event)
            self.wizard.observe(kb_message)
            return 1
        elif isinstance(wizard_command, DialogueCompletedCommand):
            send_mturk_message(
                "You cannot use this functionality during the tutorial.", self.wizard
            )
            return 0
        elif isinstance(wizard_command, SelectPrimaryCommand):
            self._primary_kb_item = wizard_command.item
            self._secondary_kb_item = None
            return 0
        elif isinstance(wizard_command, SelectSecondaryCommand):
            self._secondary_kb_item = wizard_command.item
            return 0
        elif isinstance(wizard_command, RequestSuggestionsCommand):
            suggestions = ["message 1", "message 2"]
            self.wizard.observe(
                SupplySuggestionsCommand(self.wizard, suggestions).message
            )
            return 0
        elif isinstance(wizard_command, PickSuggestionCommand):
            return 1
        else:
            print_and_log(
                45,
                f"Wizard command not allowed in dialogue stage: {wizard_command.message}",
                True,
            )
            raise RuntimeError(
                f"Wizard command not allowed in dialogue stage: {wizard_command.message}"
            )

    def block_loop(self) -> None:
        print(f"Worker {self.wizard.worker_id} failed wizard's tutorial.")
        send_mturk_message(
            "Sorry, you've exceeded the maximum amount of tries to take the "
            "correct actions, and thus we "
            "don't believe you can complete the task correctly. Please return "
            "the HIT.",
            self.wizard,
        )
        self.wizard.mturk_manager.soft_block_worker(self.wizard.worker_id)
        message = self.wizard.act()
        while not is_disconnected(message):
            send_mturk_message("Please return the HIT.", self.wizard)
            message = self.wizard.act()

    def store_wizard_event(self, event):
        _event = event
        _event["PrimaryItem"] = self._primary_kb_item
        _event["SecondaryItem"] = self._secondary_kb_item
        self.tutor.observe(_event)
        self.events.append(_event)

    def store_tutor_event(self, event):
        self.events.append(event)

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
        agents = [self.tutor, self.wizard, self.knowledgebase]
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
        if self.tutor.worker_succeeded:
            if self._qualification_on_success:
                mturk_utils.give_worker_qualification(
                    self.wizard.worker_id,
                    self._qualification_on_success,
                    is_sandbox=self.opt["is_sandbox"],
                )
            self.wizard.approve_work()
        else:
            self.wizard.block_worker(reason="Failed wizard tutorial of 2020-03-20")

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {"Events": self.events, "WizardWorkerID": self.wizard.worker_id}

    def get_model_agent(self):
        return self.wizard

    def get_task_agent(self):
        return self.tutor

    @staticmethod
    def add_cmdline_args(parser):
        pass
