#!/usr/bin/env python3

from typing import List, Text

from parlai.core.agents import Agent
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.mturk.core.mturk_manager import MTurkManager
from parlai.mturk.tasks.dialoguetest.task_config import task_config

from parlai.mturk.tasks.dialoguetest.worlds import MTurkWOZWorld
from parlai.mturk.tasks.dialoguetest.woz_agents import WOZKnowledgeBaseAgent, DummyAgent


def main(use_dummy_user: bool = True, use_dummy_wizard: bool = False) -> None:
    """
    This task consists of one agent, model or MTurk worker, talking to an MTurk worker
    to negotiate a deal.
    """
    argparser = ParlaiParser(False, False)
    argparser.add_parlai_data_path()
    argparser.add_mturk_args()
    WOZKnowledgeBaseAgent.add_cmdline_args(argparser)

    opt = argparser.parse_args()
    opt["task"] = "dialoguetest"
    opt["datatype"] = "valid"
    opt.update(task_config)

    assert not (use_dummy_user and use_dummy_wizard)

    mturk_agent_ids = []
    if use_dummy_user:
        user_id = "dummy_user"
    else:
        user_id = "mturk_user"
        mturk_agent_ids += [user_id]

    if use_dummy_wizard:
        wizard_id = "dummy_wizard"
    else:
        wizard_id = "mturk_wizard"
        mturk_agent_ids += [wizard_id]

    mturk_manager = MTurkManager(opt=opt, mturk_agent_ids=mturk_agent_ids)
    mturk_manager.setup_server()

    def create_dummy_agent(
        identification: Text, reply_file_name: Text = "demo_agent_replies.txt"
    ):
        opt["dummy_responses"] = f"../tasks/dialoguetest/{reply_file_name}"
        agent = DummyAgent(opt=opt, role="Dummy")
        agent.id = identification
        return agent

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
            print(f"{len(workers)} worker(s) ready")

            user_agent = (
                create_dummy_agent(user_id) if use_dummy_user else workers.pop()
            )
            wizard_agent = (
                create_dummy_agent(wizard_id) if use_dummy_wizard else workers.pop()
            )
            kb_agent = WOZKnowledgeBaseAgent(opt=opt)

            opt["batchindex"] = mturk_manager.started_conversations

            world = MTurkWOZWorld(
                opt=opt,
                user_agent=user_agent,
                wizard_agent=wizard_agent,
                kb_agent=kb_agent,
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
    main(use_dummy_user=True, use_dummy_wizard=False)
