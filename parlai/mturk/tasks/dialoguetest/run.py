#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
from parlai.mturk.core.mturk_manager import MTurkManager

import os

from parlai.mturk.tasks.dialoguetest.task_config import task_config
from parlai.mturk.tasks.dialoguetest.worlds import WizardOnboardingWorld, UserOnboardingWorld, WOZWorld, log_write
from parlai.mturk.tasks.dialoguetest.woz_agents import WOZKnowledgeBaseAgent


def main():
    """
    Handles setting up and running a ParlAI-MTurk task by instantiating an MTurk manager
    and configuring it for the qa_data_collection task.
    """

    log_write("NEW RUN")

    # Get relevant arguments
    argparser = ParlaiParser(False, False)
    argparser.add_parlai_data_path()
    argparser.add_mturk_args()
    WOZKnowledgeBaseAgent.add_cmdline_args(argparser)
    opt = argparser.parse_args()

    # Set the task name to be the folder name
    opt["task"] = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    # append the contents of task_config.py to the configuration
    opt.update(task_config)

    # Select an agent_id that worker agents will be assigned in their world
    mturk_agent_roles = ["Wizard", "User"]

    # Instantiate an MTurkManager with the given options and a maximum number
    # of agents per world of 1 (based on the length of mturk_agent_ids)
    mturk_manager = MTurkManager(
        opt=opt, mturk_agent_ids=mturk_agent_roles, use_db=True
    )

    mturk_manager.setup_server(
        task_directory_path=os.path.dirname(os.path.abspath(__file__))
    )

    role_index = 0

    # Create an onboard_function, which will be run for workers who have
    # accepted your task and must be completed before they are put in the
    # queue for a task world.
    def run_onboard(worker):
        nonlocal role_index
        role = mturk_agent_roles[role_index % 2]
        role_index += 1
        worker.update_agent_id(f"Onboarding {role}")
        worker.demo_role = role
        log_write(f"Onboarding {role}")
        if role == "Wizard":
            world = WizardOnboardingWorld(opt=opt, mturk_agent=worker)
        elif role == "User":
            world = UserOnboardingWorld(opt=opt, mturk_agent=worker)
        else:
            raise ValueError(f"Unknown role '{role}'")

        while not world.episode_done():
            log_write(f"BEFORE episode_done == {world.episode_done()} for role {role_index}")
            world.parley()
            log_write(f"AFTER  episode_done == {world.episode_done()} for role {role_index}")

        world.shutdown()
        return world.prep_save_data([worker])

    mturk_manager.set_onboard_function(onboard_function=run_onboard)

    try:
        # Initialize run information
        mturk_manager.start_new_run()

        # Set up the sockets and threads to receive workers
        mturk_manager.ready_to_accept_workers()

        # Create the hits as specified by command line arguments
        mturk_manager.create_hits()

        # Check workers eligiblity acts as a filter, and should return
        # the list of all workers currently eligible to work on the task
        # Can be used to pair workers that meet certain criterea
        def check_workers_eligibility(workers):
            filled_roles = []
            use_workers = []
            for worker in workers:
                if worker.demo_role not in filled_roles:
                    use_workers.append(worker)
                    filled_roles.append(worker.demo_role)
            return use_workers

        eligibility_function = {"func": check_workers_eligibility, "multiple": True}

        # Assign worker roles is used to determine what the role each worker
        # in the given worker list will play. Setting `id` to None will return
        # the worker to the pool rather than putting them in a given task,
        # which is useful for having tasks with different possible worker
        # counts.
        def assign_worker_roles(workers):
            for worker in workers:
                log_write(f"Assigning {worker.demo_role}")
                worker.id = worker.demo_role

        # Define the task function, which will be run with workers that are
        # as the main task.
        global run_conversation

        def run_conversation(mturk_manager, opt, workers):

            kb_agent = WOZKnowledgeBaseAgent(opt=opt)
            workers += [kb_agent]

            # Create the task world
            world = WOZWorld(opt=opt, agents=workers)
            # run the world to completion
            while not world.episode_done():
                world.parley()

            # shutdown and review the work
            world.shutdown()
            world.review_work()

            # Return the contents for saving
            return world.prep_save_data(workers)

        # Begin the task, allowing mturk_manager to start running the task
        # world on any workers who connect
        mturk_manager.start_task(
            eligibility_function=eligibility_function,
            assign_role_function=assign_worker_roles,
            task_function=run_conversation,
        )
    except BaseException:
        raise
    finally:
        # Any hits that aren't claimed or completed have to be shut down. Must
        # keep the world running until that point.
        mturk_manager.expire_all_unassigned_hits()
        # Shutdown the manager and free all related resources
        mturk_manager.shutdown()


if __name__ == '__main__':
    main()
