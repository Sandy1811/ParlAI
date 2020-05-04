#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import time
from typing import Text, List, Dict, Any, Optional, Tuple

from parlai import PROJECT_PATH
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
    SelectTopicCommand,
)
from parlai.mturk.tasks.woz.backend.suggestions import WizardSuggestion
from parlai.mturk.tasks.woz.backend.workers import (
    WorkerDatabase,
    TASK_LEVEL_SINGLE_HAPPY,
)
from parlai.mturk.tasks.woz.task_config import WIZARD_TUTORIAL_URL


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

    def __init__(self, opt: Opt, mturk_agent: Agent, worker_id: Text) -> None:
        super(WizardOnboardingWorld, self).__init__(opt, mturk_agent=mturk_agent)
        self._scenario = opt.get("scenario")
        self.opt = opt
        assert self._scenario
        self._worker_id = worker_id

    def parley(self):
        send_mturk_message(
            f"Hello {self._worker_id}. Every time you do this task you will be randomly assigned one of two roles: "
            f"an AI assistant, or a user. This time, you'll play the AI assistant. "
            f"This role is complicated, and thus you must first watch the following video tutorial: "
            f"{WIZARD_TUTORIAL_URL} . \n\n"
            f"If you have done this task before, you don't need to watch it again, of course. But you "
            f"must follow the instructions (especially the flow chart) precisely, or you will not be payed. \n\n"
            f"Once you are ready, type the name of the example user that appears in the tutorial and hit [Enter]. ",
            self.mturk_agent,
        )
        while True:
            message = self.mturk_agent.act()
            echo.log_write(f"onboarding wizard: {message}")
            if is_disconnected(message):
                self.episodeDone = True
                return
            if "marie" in message.get("text", "").strip().lower():
                break
            if "curie" in message.get("text", "").strip().lower():
                break
            else:
                send_mturk_message("That is not correct.", self.mturk_agent)

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

    def __init__(self, opt: Opt, mturk_agent: Agent, worker_id: Text) -> None:
        super(UserOnboardingWorld, self).__init__(opt, mturk_agent=mturk_agent)
        self._scenario = opt.get("scenario")
        self._worker_id = worker_id
        assert self._scenario

    def parley(self) -> None:
        setup = SetupCommand(scenario="intro", role="User")
        self.mturk_agent.observe(setup.message)
        self.mturk_agent.observe(
            GuideCommand(
                f"Hello {self._worker_id}. Every time you do this task you will be randomly assigned one of two roles: "
                f"an AI assistant, or a user. This time, you'll play the user. When you type 'ready' and "
                f"send a message, we will pair you up with another worker who plays the AI assistant. "
                f"Note, that playing the AI assistant is a very complex task, so your partner has to "
                f"watch a 15 minute video tutorial before he/she can start the task. Thus, it might take a "
                f"while before you get paired. Once you are paired, your situation and things to do will be "
                f"displayed on the left panel. If you like, you can use the time to watch the assistant's tutorial "
                f"under {WIZARD_TUTORIAL_URL}, so you are prepared for the next time you do this task. "
            ).message
        )
        wdb = WorkerDatabase()
        evaluation = wdb.get_worker_evaluation(self._worker_id)
        if evaluation:
            self.mturk_agent.observe(
                GuideCommand(f"Welcome back {self._worker_id}! {evaluation}").message
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

    def __init__(
        self,
        opt: Opt,
        scenario: Text,
        agents: List[MTurkAgent],
        observers: Optional[List[Agent]] = None,
    ) -> None:
        super(WOZWorld, self).__init__(opt, mturk_agent=None)
        self._is_sandbox = opt["is_sandbox"] or False
        self.observers = observers or []
        self.knowledgebase = None
        self.user = None
        self.wizard = None

        for agent in agents:
            assert hasattr(agent, "demo_role")
            if agent.demo_role == "User":
                self.user = agent
            elif agent.demo_role == "Wizard":
                self.wizard = agent
            elif agent.demo_role == "KnowledgeBase":
                self.knowledgebase = agent

        # ToDo: Adjust as NLU module gets better
        self._scenario = scenario
        self._current_domain = (
            "ride" if self._scenario.startswith("book_ride") else None
        )
        print(f"Start domain/scenario: {self._current_domain} / {self._scenario}")

        assert self.user
        assert self.wizard
        assert self._scenario

        self._episode_done = False
        self._stage = SETUP_STAGE
        self._received_evaluations = 0
        self.events = []
        self._suggestion_module = None

        self.num_turns = 1

        self._primary_kb_item = None
        self._secondary_kb_item = None
        self._selected_api: Optional[Text] = None  # The api of the selected tab
        self._selected_kb_item_api: Optional[Text] = None  # The api of the selected knowledge base item
        self._api_names: Optional[List[Text]] = None

        self._user_task_description = None
        self._questions_to_user = None
        self._questions_to_wizard = None
        self._answers_by_user = None
        self._answers_by_wizard = None
        self._user_linear_guide = None

        self._wizard_task_description = None
        self._wizard_capabilities = None

        self._wizard_has_used_kb = False
        self._num_wizard_utterances = 0
        self._num_user_utterances = 0
        self._user_has_ended_dialogue = False
        self._wizard_has_ended_dialogue = False

    def parley(self):
        if self._stage == SETUP_STAGE:
            setup_command = SetupCommand(scenario=self._scenario, role="Wizard")
            self._wizard_task_description = setup_command.task_description
            self._wizard_capabilities = setup_command.capabilities
            assert self._wizard_capabilities
            self._questions_to_wizard = setup_command.completion_questions
            self._api_names = setup_command.api_names
            self._selected_api = self._api_names[0]

            base_dir = os.path.join(PROJECT_PATH, "resources")
            self._suggestion_module = WizardSuggestion(
                scenario_list=self._api_names, resources_dir=base_dir
            )

            self.wizard.observe(setup_command.message)
            send_mturk_message(
                f"Your task: {setup_command.message.get('task_description')}",
                self.wizard,
            )

            if len(self._api_names) > 1:
                send_mturk_message(
                    f"This is a special task, where you (the AI assistant) have more capabilities. "
                    f"You can select different task-interfaces with the tabs on the left. "
                    f"Still try to stick to at least one of the flow charts whenever possible. ",
                    self.wizard,
                )

            setup_command = SetupCommand(scenario=self._scenario, role="User")
            self._questions_to_user = setup_command.completion_questions
            self._user_task_description = setup_command.task_description
            self._user_linear_guide = setup_command.user_linear_guide
            self.user.observe(setup_command.message)

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
            self._num_user_utterances += 1
            self.send_linear_user_guide_instruction()
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
            self._user_has_ended_dialogue = True
            self._stage = EVALUATION_STAGE
            return 1
        else:
            print_and_log(
                45,
                f"Command {type(user_command)} not allowed for User in dialogue stage: {user_command.message}",
                True,
            )

    def _parley_dialogue_wizard_and_knowledgebase(self) -> int:
        wizard_command = command_from_message(self.wizard.act(), self.wizard)
        self.store_wizard_event(wizard_command.event)

        if isinstance(wizard_command, UtterCommand):
            self.user.observe(wizard_command.message)
            self._num_wizard_utterances += 1
            return 1
        elif isinstance(wizard_command, SilentCommand):
            return 1
        elif isinstance(wizard_command, QueryCommand):
            self._wizard_has_used_kb = True
            self.knowledgebase.observe(wizard_command)
            kb_message = self.knowledgebase.act()
            self._primary_kb_item = kb_message.get("example_item")
            self._selected_kb_item_api = self._primary_kb_item.get("api_name")
            self._secondary_kb_item = None
            self.events.append(
                {
                    "Agent": "KnowledgeBase",
                    "Item": kb_message.get("example_item"),
                    "TotalItems": kb_message.get("num_items", 0),
                    "Topic": kb_message.get("api_name"),
                }
            )
            self.wizard.observe(kb_message)
            return 0
        elif isinstance(wizard_command, DialogueCompletedCommand):
            self._end_dialogue_by_wizard()
            return 1
        elif isinstance(wizard_command, SelectPrimaryCommand):
            self._primary_kb_item = wizard_command.item
            self._selected_kb_item_api = wizard_command.item.get("api_name")
            self._secondary_kb_item = None
            return 0
        elif isinstance(wizard_command, SelectSecondaryCommand):
            self._secondary_kb_item = wizard_command.item
            return 0
        elif isinstance(wizard_command, SelectTopicCommand):
            self._selected_api = self._api_names[int(wizard_command.topic)]
            return 0
        elif isinstance(wizard_command, RequestSuggestionsCommand):
            print(self._selected_api)
            # Prevent wizards from copy/pasting entire KB item
            if "\t" in wizard_command.query:
                send_mturk_message(
                    "Please do not just copy/paste the knowledge base item.",
                    self.wizard,
                )
                return 0

            api_names = [self._selected_api]
            if self._selected_kb_item_api:
                api_names.append(self._selected_kb_item_api)
            else:
                api_names.append(self._selected_api)

            # Get suggestions from Rasa NLU server
            (
                suggestions,
                possibly_wrong_item_selected,
            ) = self._suggestion_module.get_suggestions(
                wizard_utterance=wizard_command.query,
                primary_kb_item=self._primary_kb_item,
                api_names=api_names,
            )
            # Warn if response template of top-ranked intent could not be filled by selected KB item
            if possibly_wrong_item_selected:
                send_mturk_message(
                    "Some suggestions won't show. Did you select the knowledge base item(s) that you are describing?",
                    self.wizard,
                )
            # Return suggested responses to front end
            self.wizard.observe(
                SupplySuggestionsCommand(self.wizard, suggestions).message
            )
            return 0
        elif isinstance(wizard_command, PickSuggestionCommand):
            self.wizard.observe(wizard_command.message)
            self.user.observe(wizard_command.message)
            self._num_wizard_utterances += 1
            if "goodbye" in wizard_command.message.get("text", "").lower():
                self._end_dialogue_by_wizard()
            return 1
        else:
            print_and_log(
                45,
                f"Command {type(wizard_command)} not allowed for Wizard in dialogue stage: {wizard_command.message}",
                True,
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
                if agent.id == "User":
                    self._answers_by_user = command.answers
                else:
                    self._answers_by_wizard = command.answers
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
                print_and_log(
                    45,
                    f"Command {type(command)} not allowed for {agent.id} in evaluation stage: {command.message}",
                    True,
                )

    def _end_dialogue_by_wizard(self):
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
        self._wizard_has_ended_dialogue = True
        self._stage = EVALUATION_STAGE

    def send_linear_user_guide_instruction(self) -> None:
        if not self._user_linear_guide or self._num_user_utterances >= len(
            self._user_linear_guide
        ):
            return

        instruction = self._user_linear_guide[self._num_user_utterances]
        if instruction:
            self.events.append(
                {
                    "Agent": "UserGuide",
                    "Action": "instruct",
                    "Text": instruction,
                    "UnixTime": int(time.time()),
                }
            )
            self.user.observe(GuideCommand(instruction).message)

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
        if self._user_linear_guide:
            self.send_linear_user_guide_instruction()
        else:
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

        wdb = WorkerDatabase()

        if self.review_user():
            wdb.store_work(
                self.user.worker_id,
                self.user.hit_id,
                self._is_sandbox,
                "User",
                "",
                TASK_LEVEL_SINGLE_HAPPY,
                self._num_user_utterances,
            )
            print(
                f"User {self.user.worker_id}'s work was approved (HIT {self.user.hit_id})"
            )
        else:
            print(
                f"User {self.user.worker_id}'s work was rejected (HIT {self.user.hit_id})"
            )

        if self.review_wizard():
            wdb.store_work(
                self.wizard.worker_id,
                self.wizard.hit_id,
                self._is_sandbox,
                "Wizard",
                "",
                TASK_LEVEL_SINGLE_HAPPY,
                self._num_wizard_utterances,
            )
            print(
                f"Wizard {self.wizard.worker_id}'s work was approved (HIT {self.wizard.hit_id})"
            )
        else:
            print(
                f"Wizard {self.wizard.worker_id}'s work was rejected (HIT {self.wizard.hit_id})"
            )

    def review_user(self) -> bool:
        if self._num_user_utterances < 2:
            self.user.reject_work("You wrote fewer than 2 messages")
            return False

        # if (
        #     self._user_linear_guide
        #     and self._num_user_utterances < len(self._user_linear_guide)
        #     and self._user_has_ended_dialogue
        # ):
        #     self.user.reject_work(
        #         "You ended the dialogue before being instructed to do so"
        #     )
        #     return False

        self.user.approve_work()
        return True

    def review_wizard(self) -> bool:
        if self._num_wizard_utterances < 2:
            self.wizard.reject_work("You wrote fewer than 2 messages")
            return False

        if not self._wizard_has_used_kb:
            self.wizard.reject_work("You did not use the knowledge base interface")
            return False

        self.wizard.approve_work()
        return True

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the data set. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        user_questionaire_data = [
            {"Question": self._questions_to_user[i], "Answer": self._answers_by_user[i]}
            for i in range(
                min(len(self._questions_to_user), len(self._answers_by_user))
            )
        ]
        wizard_questionaire_data = [
            {
                "Question": self._questions_to_wizard[i],
                "Answer": self._answers_by_wizard[i],
            }
            for i in range(
                min(len(self._questions_to_wizard), len(self._answers_by_wizard))
            )
        ]
        return {
            "FORMAT-VERSION": 3,
            "Scenario": {
                "Domains": sorted(
                    list({c.get("Domain") for c in self._wizard_capabilities})
                ),
                "UserTask": self._user_task_description,
                "WizardTask": self._wizard_task_description,
                "WizardCapabilities": self._wizard_capabilities,
            },
            "Events": self.events,
            "WizardWorkerID": (
                self.wizard.worker_id if hasattr(self.wizard, "worker_id") else None
            ),
            "WizardHITID": (
                self.wizard.hit_id if hasattr(self.wizard, "hit_id") else None
            ),
            "WizardAssignmentID": (
                self.wizard.assignment_id
                if hasattr(self.wizard, "assignment_id")
                else None
            ),
            "UserWorkerID": (
                self.user.worker_id if hasattr(self.user, "worker_id") else None
            ),
            "UserHITID": (self.user.hit_id if hasattr(self.user, "hit_id") else None),
            "UserAssignmentID": (
                self.user.assignment_id if hasattr(self.user, "assignment_id") else None
            ),
            "UserQuestionaire": user_questionaire_data,
            "WizardQuestionaire": wizard_questionaire_data,
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
        parser.add_argument(
            "--scenario_list", type=str, default="all_scenarios", help="Scenario list",
        )


# class WOZWizardTutorialWorld(MTurkTaskWorld):
#     def __init__(
#         self,
#         opt,
#         agents,
#         observers: Optional[List[Agent]] = None,
#         qualification_on_success: Optional[Text] = None,
#     ) -> None:
#         super(WOZWizardTutorialWorld, self).__init__(opt, mturk_agent=None)
#         self.opt = opt
#         self.observers = observers or []
#         self.knowledgebase = None
#         self.tutor = None
#         self.wizard = None
#         for agent in agents:
#             if agent.demo_role == "User":
#                 self.tutor = agent
#             elif agent.demo_role == "Wizard":
#                 self.wizard = agent
#             elif agent.demo_role == "KnowledgeBase":
#                 self.knowledgebase = agent
#
#         self._scenario = opt.get("scenario")
#         self._qualification_on_success = qualification_on_success
#
#         assert self.tutor
#         assert self.wizard
#         assert self._scenario
#
#         self._episode_done = False
#         self._stage = SETUP_STAGE
#         self._received_evaluations = 0
#         self.events = []
#
#         self.num_turns = 1
#
#         self._primary_kb_item = None
#         self._secondary_kb_item = None
#
#     def parley(self):
#         if self._stage == SETUP_STAGE:
#             self.wizard.observe(
#                 SetupCommand(scenario=self._scenario, role="Wizard").message
#             )
#             self.num_turns = 0
#             self._stage = DIALOGUE_STAGE
#         elif self._stage == DIALOGUE_STAGE:
#             if self.num_turns % 2 == 0:
#                 self.num_turns += self._parley_tutor()
#             else:
#                 self.num_turns += self._parley_wizard()
#         elif self._stage == EVALUATION_STAGE:
#             if not self.tutor.worker_succeeded:
#                 self.block_loop()
#             self._stage = END_STAGE
#         elif self._stage == END_STAGE:
#             self._episode_done = True
#
#     def _parley_tutor(self) -> int:
#         tutor_command = command_from_message(self.tutor.act(), self.tutor)
#         self.store_tutor_event(tutor_command.event)
#
#         if isinstance(tutor_command, DialogueCompletedCommand):
#             self._stage = EVALUATION_STAGE
#             return 1
#         elif isinstance(tutor_command, SilentCommand):
#             return 1
#         else:
#             self.wizard.observe(tutor_command.message)
#             return 0
#
#     def _parley_wizard(self) -> int:
#         wizard_command = command_from_message(self.wizard.act(), self.wizard)
#         self.store_wizard_event(wizard_command.event)
#
#         if isinstance(wizard_command, UtterCommand):
#             return 1
#         elif isinstance(wizard_command, SilentCommand):
#             return 1
#         elif isinstance(wizard_command, QueryCommand):
#             self.knowledgebase.observe(wizard_command)
#             kb_message = self.knowledgebase.act()
#             self._primary_kb_item = kb_message.get("example_item")
#             self._secondary_kb_item = None
#             self.events.append(
#                 {
#                     "Agent": "KnowledgeBase",
#                     "Item": kb_message.get("example_item"),
#                     "TotalItems": kb_message.get("num_items", 0),
#                     "Topic": kb_message.get("api_name"),
#                 }
#             )
#             self.wizard.observe(kb_message)
#             return 1
#         elif isinstance(wizard_command, DialogueCompletedCommand):
#             send_mturk_message(
#                 "You cannot use this functionality during the tutorial.", self.wizard
#             )
#             return 0
#         elif isinstance(wizard_command, SelectPrimaryCommand):
#             self._primary_kb_item = wizard_command.item
#             self._secondary_kb_item = None
#             return 0
#         elif isinstance(wizard_command, SelectSecondaryCommand):
#             self._secondary_kb_item = wizard_command.item
#             return 0
#         elif isinstance(wizard_command, RequestSuggestionsCommand):
#             suggestions = ["message 1", "message 2"]
#             self.wizard.observe(
#                 SupplySuggestionsCommand(self.wizard, suggestions).message
#             )
#             return 0
#         elif isinstance(wizard_command, PickSuggestionCommand):
#             return 1
#         else:
#             print_and_log(
#                 45,
#                 f"Command {type(wizard_command)} not allowed for Wizard in evaluation stage: {wizard_command.message}",
#                 True,
#             )
#
#     def block_loop(self) -> None:
#         print(f"Worker {self.wizard.worker_id} failed wizard's tutorial.")
#         send_mturk_message(
#             "Sorry, you've exceeded the maximum amount of tries to take the "
#             "correct actions, and thus we "
#             "don't believe you can complete the task correctly. Please return "
#             "the HIT.",
#             self.wizard,
#         )
#         self.wizard.mturk_manager.soft_block_worker(self.wizard.worker_id)
#         message = self.wizard.act()
#         while not is_disconnected(message):
#             send_mturk_message("Please return the HIT.", self.wizard)
#             message = self.wizard.act()
#
#     def store_wizard_event(self, event):
#         _event = event
#         _event["PrimaryItem"] = self._primary_kb_item
#         _event["SecondaryItem"] = self._secondary_kb_item
#         self.tutor.observe(_event)
#         self.events.append(_event)
#
#     def store_tutor_event(self, event):
#         self.events.append(event)
#
#     def episode_done(self):
#         return self._episode_done
#
#     def shutdown(self):
#         # Parallel shutdown of agents
#         def shutdown_agent(agent):
#             try:
#                 agent.shutdown(timeout=None)
#             except Exception:
#                 agent.shutdown()  # not MTurkAgent
#
#         threads = []
#         agents = [self.tutor, self.wizard, self.knowledgebase]
#         mturk_agents = [agent for agent in agents if isinstance(agent, MTurkAgent)]
#         for agent in mturk_agents:
#             t = threading.Thread(target=shutdown_agent, args=(agent,))
#             t.start()
#             threads.append(t)
#         for t in threads:
#             t.join()
#
#     def review_work(self):
#         # Can review the work here to accept or reject it
#         # self.mturk_agent.approve_work()
#         # self.mturk_agent.reject_work()
#         # self.mturk_agent.pay_bonus(1000) # Pay $1000 as bonus
#         # self.mturk_agent.block_worker() # Block this worker from future HITs
#         if self.tutor.worker_succeeded:
#             if self._qualification_on_success:
#                 mturk_utils.give_worker_qualification(
#                     self.wizard.worker_id,
#                     self._qualification_on_success,
#                     is_sandbox=self.opt["is_sandbox"],
#                 )
#             self.wizard.approve_work()
#         else:
#             self.wizard.block_worker(reason="Failed wizard tutorial of 2020-03-20")
#
#     def get_custom_task_data(self):
#         # brings important data together for the task, to later be used for
#         # creating the dataset. If data requires pickling, put it in a field
#         # called 'needs-pickle'.
#         return {"Events": self.events, "WizardWorkerID": self.wizard.worker_id}
#
#     def get_model_agent(self):
#         return self.wizard
#
#     def get_task_agent(self):
#         return self.tutor
#
#     @staticmethod
#     def add_cmdline_args(parser):
#         pass
