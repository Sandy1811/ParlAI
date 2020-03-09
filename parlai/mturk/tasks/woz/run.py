#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
from parlai.mturk.core.mturk_manager import MTurkManager

import os

import parlai.mturk.tasks.woz.echo as echo
from parlai.mturk.tasks.woz.task_config import task_config
from parlai.mturk.tasks.woz.utils import MTurkQualificationManager
from parlai.mturk.tasks.woz.backend.worlds import (
    WizardOnboardingWorld,
    UserOnboardingWorld,
    WOZWorld,
)
from parlai.mturk.tasks.woz.backend.agents import (
    WOZKnowledgeBaseAgent,
    WOZDummyAgent,
    WOZTutorAgent,
)


def main():
    """
    Handles setting up and running a ParlAI-MTurk task by instantiating an MTurk manager
    and configuring it for the qa_data_collection task.
    """

    echo.log_write("START")

    # Get relevant arguments
    arg_parser = ParlaiParser(False, False)
    arg_parser.add_parlai_data_path()
    arg_parser.add_mturk_args()
    WOZDummyAgent.add_cmdline_args(arg_parser)
    WOZKnowledgeBaseAgent.add_cmdline_args(arg_parser)
    opt = arg_parser.parse_args()

    qualification_manager = MTurkQualificationManager()
    qualification_manager.require_min_approved_hits(10)
    # qualification_manager.require_locales(["DE", "US", "CA", "GB", "AU", "NZ"])

    # Set the task name to be the folder name
    opt["task"] = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    # Append the contents of task_config.py to the configuration
    opt.update(task_config)

    # Select an agent_id that worker agents will be assigned in their world
    if opt["dummy_user"]:
        mturk_agent_roles = ["Wizard"]
    else:
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
        echo.log_write(f"run_onboard for {worker.worker_id}")
        role = mturk_agent_roles[role_index % len(mturk_agent_roles)]
        role_index += 1
        worker.demo_role = role
        worker.passed_onboarding = False
        if role == "Wizard":
            worker.update_agent_id("Wizard")
            world = WizardOnboardingWorld(opt=opt, mturk_agent=worker)
        elif role == "User":
            worker.update_agent_id("User")
            world = UserOnboardingWorld(opt=opt, mturk_agent=worker)
        else:
            raise ValueError(f"Unknown role '{role}'")

        while not world.episode_done():
            world.parley()

        if worker.passed_onboarding:
            print(f"{worker.worker_id} passed onboarding")
            echo.log_write(f"{worker.worker_id} passed onboarding")
        else:
            print(f"{worker.worker_id} failed onboarding")
            echo.log_write(f"{worker.worker_id} failed onboarding")
            worker.demo_role = "none"

        world.shutdown()
        return world.prep_save_data([worker])

    mturk_manager.set_onboard_function(onboard_function=run_onboard)

    try:
        # Initialize run information
        mturk_manager.start_new_run()

        # Set up the sockets and threads to receive workers
        mturk_manager.ready_to_accept_workers()

        # Create the hits as specified by command line arguments
        mturk_manager.create_hits(qualifications=qualification_manager.qualifications)

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
                worker.id = worker.demo_role

        # Define the task function, which will be run with workers that are
        # as the main task.
        global run_conversation

        def run_conversation(mturk_manager, opt, workers):

            kb_agent = WOZKnowledgeBaseAgent(options=opt)
            workers += [kb_agent]

            user_tutor_agent = WOZTutorAgent(options=opt, rules=[])
            user_tutor_agent.demo_role = "UserTutor"
            user_tutor_agent.add_rule(
                WOZTutorAgent.num_turns_condition(min_num_turns=6),
                "If it makes sense at this point in the conversation, please change your mind about something.",
                max_times_triggered=1
            )
            user_tutor_agent.add_rule(
                WOZTutorAgent.kb_changed_condition(),
                "Within the next few turns, try to refer to something you've said earlier in the conversation.",
                max_times_triggered=2
            )
            workers += [user_tutor_agent]

            if opt["dummy_user"]:
                dummy_user = WOZDummyAgent(opt, "User")
                workers += [dummy_user]

            # Create the task world
            world = WOZWorld(opt=opt, agents=workers)
            # run the world to completion
            while not world.episode_done():
                world.parley()

            print("task complete")

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
