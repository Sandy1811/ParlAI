#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from datetime import datetime
from typing import Text

from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
import threading


def log_write_act(index: int, agent_name: Text, act) -> None:
    with open("/Users/johannes/TESTLOG.log", "a+") as file:
        time = str(datetime.now().isoformat())
        file.write(f"{time}\t{index:2}\t{agent_name}\t{act}\n")


def log_write(message: Text) -> None:
    with open("/Users/johannes/TESTLOG.log", "a+") as file:
        time = str(datetime.now().isoformat())
        file.write(f"{time}\t{message}\n")


class WizardOnboardingWorld(MTurkOnboardWorld):
    """
    Example onboarding world.

    Sends a message from the world to the worker and then exits as complete after the
    worker uses the interface
    """

    def parley(self):
        ad = {
            'id': 'MTurk System',
            'text': f"Please wait for the user to join the conversation...",
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
        ad = {
            'id': 'System',
            'text': "Please wait for the virtual assistant to join the conversation...",
        }
        self.mturk_agent.observe(ad)
        # response = self.mturk_agent.act()
        # log_write_act(-1, self.mturk_agent.id, response)
        self.episodeDone = True


class WOZWorld(MTurkTaskWorld):
    """
    World to demonstrate workers with assymetric roles.

    This task amounts to three rounds and then an evaluation step. It is purposefully
    created as a task to demo multiple views and has no other purpose.
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
        self.questions = []
        self.answers = []

        self.num_turns = -1
        self.max_turns = 3

    def parley(self):
        """
        Let the user and the wizard have a turn each.
        """
        log_write_act(0, "None", "world started")

        if self.num_turns < 0:
            self.setup_interface()
            return

        if self.num_turns == 0:
            ad = {
                'id': 'MTurk System',
                'text': "The assistant is ready. Go ahead, say hello!",
            }
            self.user_agent.observe(ad)
            ad = {
                'id': 'MTurk System',
                'text': "A user has joined the chat. "
                "Please wait for him/her to start the conversation.",
            }
            self.wizard_agent.observe(ad)

        self.num_turns += 1

        user_message = self.user_agent.act()
        self.wizard_agent.observe(user_message)
        wizard_message = self.wizard_agent.act()

        if self.kb_agent:
            # Handle communication between the wizard and the knowledge base
            while (
                wizard_message
                and wizard_message.get("text")
                and wizard_message.get("text").startswith("?")
            ):
                self.kb_agent.observe(wizard_message)
                kb_message = self.kb_agent.act()
                self.wizard_agent.observe(kb_message)
                wizard_message = self.wizard_agent.act()

        self.user_agent.observe(wizard_message)

        if self.num_turns >= self.max_turns:
            self.episodeDone = True

    def setup_intro(self):
        for agent in [self.user_agent, self.wizard_agent]:
            action = {'text': "", 'info': f"prolog", "id": agent.id}

            agent.observe(action)

        self.num_turns = 0

    def setup_interface(self):
        for agent in [self.user_agent, self.wizard_agent]:
            action = {'text': "", 'info': f"start", "id": agent.id}

            agent.observe(action)

        self.num_turns = 0

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
        return {
            'questions': self.questions,
            'answers': self.answers,
        }
