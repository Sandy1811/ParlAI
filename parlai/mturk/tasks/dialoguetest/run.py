#!/usr/bin/env python3

import os
from typing import List, Dict, Text, Any

from parlai.agents.random_candidate.random_candidate import RandomCandidateAgent
from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.mturk.core.mturk_manager import MTurkManager
from parlai.mturk.tasks.dialoguetest.task_config import task_config

from parlai.mturk.tasks.dialoguetest.worlds import MTurkWOZWorld


def main() -> None:
    """
    This task consists of one agent, model or MTurk worker, talking to an MTurk worker
    to negotiate a deal.
    """
    argparser = ParlaiParser(False, False)
    argparser.add_parlai_data_path()
    argparser.add_mturk_args()

    opt = argparser.parse_args()
    opt["task"] = "dialoguetest"
    opt["datatype"] = "valid"
    opt.update(task_config)

    wizard_id = "dummy_wizard"
    user_id = "user"
    mturk_agent_ids = [user_id]
    # if opt['two_mturk_agents']:
    #     mturk_agent_ids.append('mturk_agent_2')

    mturk_manager = MTurkManager(opt=opt, mturk_agent_ids=[user_id])
    mturk_manager.setup_server()

    try:
        mturk_manager.start_new_run()

        mturk_manager.set_onboard_function(onboard_function=None)
        mturk_manager.ready_to_accept_workers()
        mturk_manager.create_hits()

        def check_worker_eligibility(worker: Agent) -> bool:
            return True

        def assign_worker_roles(workers: List[Agent]) -> None:
            for index, worker in enumerate(workers):
                worker.id = mturk_agent_ids[index % len(mturk_agent_ids)]

        def run_conversation(
            mturk_manager: MTurkManager, opt: Opt, workers: List[Agent]
        ) -> None:
            user_agent = workers[0]

            # Create a local agent
            opt[
                "label_candidates_file"
            ] = "../tasks/dialoguetest/demo_agent_replies.txt"
            wizard_agent = RandomCandidateAgent(opt=opt)
            wizard_agent.id = wizard_id

            opt["batchindex"] = mturk_manager.started_conversations

            world = MTurkWOZWorld(
                opt=opt, user_agent=user_agent, wizard_agent=wizard_agent
            )

            while not world.episode_done():
                world.parley()

            world.shutdown()

        mturk_manager.start_task(
            eligibility_function=check_worker_eligibility,
            assign_role_function=assign_worker_roles,
            task_function=run_conversation,
        )

    except BaseException:
        raise
    finally:
        mturk_manager.expire_all_unassigned_hits()
        mturk_manager.shutdown()


if __name__ == '__main__':
    main()
