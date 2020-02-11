#!/usr/bin/env python3

from typing import Optional, Text

from parlai.core.agents import Agent
from parlai.mturk.core.worlds import MTurkTaskWorld
from joblib import Parallel, delayed
from datetime import datetime


def log_write_act(index: int, agent_name: Text, act) -> None:
    with open("TESTLOG.log", "a+") as file:
        time = str(datetime.now().isoformat())
        file.write(f"{time}\t{index:2}\t{agent_name}\t{act}\n")


class MTurkWOZWorld(MTurkTaskWorld):
    """
    World where two agents have a dialogue, and a third represents a knowledge base.
    """

    def __init__(
        self,
        opt,
        user_agent: Agent,
        wizard_agent: Agent,
        kb_agent: Optional[Agent] = None,
    ):
        super(MTurkWOZWorld, self).__init__(opt, None)
        self.user_agent = user_agent
        self.wizard_agent = wizard_agent
        self.kb_agent = kb_agent

        self.episodeDone = False

        self.num_turns = -1
        self.max_turns = 3

    def parley(self) -> None:
        """
        Let the user and the wizard have a turn each.
        """
        if self.num_turns < 0:
            self.setup_interface()
            return

        self.num_turns += 1

        user_message = self.user_agent.act()
        log_write_act(self.num_turns, "user", user_message)
        self.wizard_agent.observe(user_message)
        wizard_message = self.wizard_agent.act()
        log_write_act(self.num_turns, "wizard", wizard_message)
        self.user_agent.observe(wizard_message)

        if self.num_turns >= self.max_turns:
            self.episodeDone = True

    def setup_interface(self):
        for agent in [self.user_agent, self.wizard_agent]:
            action = {
                'text': "Here is a welcome message...",
                'items': {
                    "book_cnt": 2,
                    "book_val": 2,
                    "hat_cnt": 3,
                    "hat_val": 2,
                    "ball_cnt": 2,
                    "ball_val": 1,
                },
            }

            agent.observe(action)

        self.num_turns = 0

    def episode_done(self):
        return self.episodeDone

    def get_task_agent(self):
        super(MTurkWOZWorld, self).get_task_agent()

    # noinspection PyGlobalUndefined
    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """
        global shutdown_agent

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=2, backend='threading')(
            delayed(shutdown_agent)(agent)
            for agent in [self.user_agent, self.wizard_agent]
        )
