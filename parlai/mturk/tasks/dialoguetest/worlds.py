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
)
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
import threading

import parlai.mturk.tasks.dialoguetest.echo as echo
from parlai.mturk.tasks.dialoguetest.protocol import (
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
    WORKER_REQUEST_SUGGESTIONS, COMMAND_SUPPLY_SUGGESTIONS, WORKER_PICK_SUGGESTION)


def is_disconnected(act):
    return 'text' in act and act['text'] in [
        MTURK_DISCONNECT_MESSAGE,
        RETURN_MESSAGE,
        TIMEOUT_MESSAGE,
    ]


DUMMY_FORM_DESCRIPTION = [
    {
        "input": [
            {
                "Name": "Level",
                "Type": "Integer",
                "Min": 0,
                "Max": 15,
                "ReadableName": "Level",
            },
            {
                "Name": "MaxLevel",
                "Type": "Integer",
                "Min": 0,
                "Max": 15,
                "ReadableName": "Max Level",
            },
            {"Name": "HasBalcony", "Type": "Boolean", "ReadableName": "Has Balcony"},
            {
                "Name": "BalconySide",
                "Type": "Categorical",
                "Categories": ["east", "north", "south", "west"],
                "ReadableName": "Balcony Side",
            },
            {"Name": "HasElevator", "Type": "Boolean", "ReadableName": "Has Elevator"},
            {
                "Name": "NumRooms",
                "Type": "Integer",
                "Min": 1,
                "Max": 7,
                "ReadableName": "Num Rooms",
            },
            {
                "Name": "FloorSquareMeters",
                "Type": "Integer",
                "Min": 10,
                "Max": 350,
                "ReadableName": "Floor Square Meters",
            },
            {
                "Name": "NearbyPOIs",
                "Type": "CategoricalMultiple",
                "Categories": ["School", "TrainStation", "Park"],
                "ReadableName": "Nearby POIs",
            },
            {
                "Name": "Name",
                "Type": "Categorical",
                "Categories": [
                    "One on Center Apartments",
                    "Shadyside Apartments",
                    "North Hill Apartments",
                ],
                "ReadableName": "Name",
            },
        ],
        "output": [
            {
                "Name": "Level",
                "Type": "Integer",
                "Min": 0,
                "Max": 15,
                "ReadableName": "Level",
            },
            {
                "Name": "MaxLevel",
                "Type": "Integer",
                "Min": 0,
                "Max": 15,
                "ReadableName": "Max Level",
            },
            {"Name": "HasBalcony", "Type": "Boolean", "ReadableName": "Has Balcony"},
            {
                "Name": "BalconySide",
                "Type": "Categorical",
                "Categories": ["east", "north", "south", "west"],
                "ReadableName": "Balcony Side",
            },
            {"Name": "HasElevator", "Type": "Boolean", "ReadableName": "Has Elevator"},
            {
                "Name": "NumRooms",
                "Type": "Integer",
                "Min": 1,
                "Max": 7,
                "ReadableName": "Num Rooms",
            },
            {
                "Name": "FloorSquareMeters",
                "Type": "Integer",
                "Min": 10,
                "Max": 350,
                "ReadableName": "Floor Square Meters",
            },
            {
                "Name": "NearbyPOIs",
                "Type": "CategoricalMultiple",
                "Categories": ["School", "TrainStation", "Park"],
                "ReadableName": "Nearby POIs",
            },
            {
                "Name": "Name",
                "Type": "Categorical",
                "Categories": [
                    "One on Center Apartments",
                    "Shadyside Apartments",
                    "North Hill Apartments",
                ],
                "ReadableName": "Name",
            },
        ],
        "required": [],
        "db": "apartment",
        "function": "generic_sample",
        "returns_count": True,
        "schema_url": "https://upload.wikimedia.org/wikipedia/commons/6/65/Difficult_editor_-_flow_chart.png",
    },
    {
        "input": [
            {
                "Name": "id",
                "Type": "Integer",
                "Min": 1,
                "Max": 1000,
                "ReadableName": "id",
            }
        ],
        "output": [
            {
                "Name": "Price",
                "Type": "Integer",
                "Min": 5,
                "Max": 50,
                "ReadableName": "Price",
            },
            {
                "Name": "AllowsChanges",
                "Type": "Boolean",
                "ReadableName": "Allows Changes",
            },
            {
                "Name": "DurationMinutes",
                "Type": "Integer",
                "Min": 5,
                "Max": 30,
                "ReadableName": "Duration Minutes",
            },
            {
                "Name": "ServiceProvider",
                "Type": "Categorical",
                "Categories": ["Uber", "Lyft", "Taxi"],
                "ReadableName": "Service Provider",
            },
            {
                "Name": "DriverName",
                "Type": "Categorical",
                "Categories": ["Mark", "John", "Dave", "Connor", "Alex"],
                "ReadableName": "Driver Name",
            },
            {
                "Name": "CarModel",
                "Type": "Categorical",
                "Categories": ["Honda", "Toyota", "Corolla", "Tesla", "BMW", "Ford"],
                "ReadableName": "Car Model",
            },
            {
                "Name": "LicensePlate",
                "Type": "Categorical",
                "Categories": ["432 LSA", "313 EA9", "901 FSA", "019 EAS", "031 NGA"],
                "ReadableName": "License Plate",
            },
            {
                "Name": "id",
                "Type": "Integer",
                "Min": 1,
                "Max": 1000,
                "ReadableName": "id",
            },
            {
                "Name": "RideStatus",
                "Type": "ShortString",
                "ReadableName": "Ride Status",
            },
            {"Name": "RideWait", "Type": "ShortString", "ReadableName": "Ride Wait"},
        ],
        "required": ["id"],
        "db": "ride",
        "function": "ride_status",
        "returns_count": False,
        "schema_url": "http://www.texample.net/media/tikz/examples/PNG/simple-flow-chart.png",
    },
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
            "Write 'ready' when you are ready and press [Enter].",
            self.mturk_agent,
        )
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


class WOZWorld(MTurkTaskWorld):
    """
    Wizard-of-Oz world.
    """

    collector_agent_id = 'Moderator'

    def __init__(self, opt, agents):
        self.mturk_agents = agents
        self.kb_agent = None
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
            self.setup_interface()
            self.tell_workers_to_start()
            self.num_turns = 0
            return

        self.num_turns += 1

        user_message, command, parameters = self.get_new_user_message()
        self.deal_with_user_command(command, parameters)

        if not self.evaluating:
            self.wizard_agent.observe(user_message)

        wizard_message, command, parameters = self.get_new_wizard_message()
        # Handle communication between the wizard and the knowledge base
        while command in [
            WORKER_COMMAND_QUERY,
            WORKER_SELECT_1,
            WORKER_SELECT_2,
            WORKER_REQUEST_SUGGESTIONS,
        ]:
            if command == WORKER_COMMAND_QUERY:
                self.kb_agent.observe({"query": parameters})
                kb_message, _, _ = self.get_new_knowledgebase_message()
                self.wizard_agent.observe(kb_message)
            elif command == WORKER_REQUEST_SUGGESTIONS:
                self.send_suggestions(["1", "2", "3"], self.wizard_agent)
            wizard_message, command, parameters = self.get_new_wizard_message()

        if command and command == WORKER_PICK_SUGGESTION:
            wizard_message = {
                "id": self.wizard_agent.id,
                "text": parameters,
            }
            self.wizard_agent.observe(wizard_message)

        self.deal_with_wizard_command(command, parameters)

        if not self.evaluating:
            self.user_agent.observe(wizard_message)

        if self.num_turns >= self.max_turns:
            self.episodeDone = True

    @echo.echo_out(output=echo.log_write, prefix="get_new_user_message() = ")
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

    @echo.echo_out(output=echo.log_write, prefix="get_new_wizard_message() = ")
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

    @echo.echo_out(output=echo.log_write, prefix="get_new_knowledgebase_message() = ")
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
        elif command == WORKER_COMMAND_COMPLETE:
            self.send_command(COMMAND_REVIEW, self.wizard_agent)
            self.send_command(COMMAND_REVIEW, self.user_agent)
            self.evaluating = True
            send_mturk_message(
                "Thank you for chatting. Now please review your conversation.",
                self.wizard_agent,
            )
            send_mturk_message(
                "The assistant thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the assistant.",
                self.user_agent,
            )
        elif command == WORKER_COMMAND_DONE:
            send_mturk_message(
                "Thank you for evaluating! Please wait for the user to agree...",
                self.wizard_agent,
            )
            self.episodeDone = True
        elif command == WORKER_DISCONNECTED:
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
            send_mturk_message(
                "Thank you for chatting. Now please review your conversation.",
                self.user_agent,
            )
            send_mturk_message(
                "The user thinks that the task is complete. Please review your conversation, click on 'confirm', and wait for the user.",
                self.wizard_agent,
            )
        elif command == WORKER_COMMAND_DONE:
            send_mturk_message(
                "Thank you for evaluating! Please wait for the assistant to agree...",
                self.user_agent,
            )
            self.episodeDone = True
        elif command == WORKER_DISCONNECTED:
            send_mturk_message("Sorry, the user disconnected...", self.user_agent)
            self.episodeDone = True

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
        for agent in [self.user_agent, self.wizard_agent]:
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
        return self.wizard_agent  # ToDo: Don't know if this is correct

    def get_task_agent(self):
        return self.user_agent

    def send_suggestions(self, suggestions: List[Text], wizard_agent):
        self.send_command(COMMAND_SUPPLY_SUGGESTIONS + str(suggestions), wizard_agent)
