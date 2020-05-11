#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import random

from parlai import PROJECT_PATH
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.mturk.core import mturk_utils
from parlai.mturk.core.agents import MTurkAgent
from parlai.mturk.core.mturk_manager import MTurkManager

import os

import parlai.mturk.tasks.woz.echo as echo
from parlai.mturk.tasks.woz.knowledgebase import api
from parlai.mturk.tasks.woz.task_config import task_config
from parlai.mturk.tasks.woz.qualify import MTurkQualificationManager
from parlai.mturk.tasks.woz.backend.worlds import (
    WizardOnboardingWorld,
    UserOnboardingWorld,
    WOZWorld,
)
from parlai.mturk.tasks.woz.backend.agents import (
    WOZKnowledgeBaseAgent,
    WOZDummyAgent,
    WOZInstructorAgent,
    WOZWizardIntroAgent,
)


def create_user_instructor(opt: Opt):
    user_tutor_agent = WOZInstructorAgent(options=opt, rules=[])
    user_tutor_agent.demo_role = "UserTutor"
    user_tutor_agent.add_rule(
        WOZInstructorAgent.num_turns_condition(min_num_turns=3),
        "Your train just arrived and you notice that there is construction work blocking some areas. A car might not be able to pick you up right at the entrance. Imagine a place nearby for a pickup point.",
        max_times_triggered=1,
        target="User",
    )
    user_tutor_agent.add_rule(
        WOZInstructorAgent.num_turns_condition(min_num_turns=5),
        "You get a message from your boss, telling you that you should skip the hotel and come directly to the office (42 Wall Street) and meet your new client.",
        max_times_triggered=1,
        target="User",
    )
    user_tutor_agent.add_rule(
        WOZInstructorAgent.num_turns_condition(min_num_turns=7),
        "It occurs to you that you should arrive in a really fancy car if you are going to meet the client right away.",
        max_times_triggered=1,
        target="User",
    )
    # user_tutor_agent.add_rule(
    #     WOZInstructorAgent.random_turn_condition(10, 11, 1),
    #     "Within the next few turns, please refer to something you've said at the beginning of the conversation.",
    #     target="User",
    # )
    user_tutor_agent.add_rule(
        WOZInstructorAgent.num_turns_condition(min_num_turns=9),
        "See if you can get a cheaper ride.",
        max_times_triggered=1,
        target="User",
    )
    return user_tutor_agent


def main():
    """
    Handles setting up and running a ParlAI-MTurk task by instantiating an MTurk manager
    and configuring it for the qa_data_collection task.
    """

    # Get relevant arguments
    arg_parser = ParlaiParser(False, False)
    arg_parser.add_parlai_data_path()
    arg_parser.add_mturk_args()
    WOZDummyAgent.add_cmdline_args(arg_parser)
    WOZKnowledgeBaseAgent.add_cmdline_args(arg_parser)
    WOZWorld.add_cmdline_args(arg_parser)
    WOZWizardIntroAgent.add_cmdline_args(arg_parser)
    opt = arg_parser.parse_args()

    # opt["dummy_user"] = True
    # opt["dummy_responses"] = "/Users/johannes/ParlAI/parlai/mturk/tasks/woz/test_user_replies.txt"
    # opt["wizard_intro"] = "/Users/johannes/ParlAI/parlai/mturk/tasks/woz/tutorial_wizard_book-ride.json"
    if opt["dummy_user"]:
        api.dbs["ride"].clear()
        item_we_probably_find = {
            "Price": 21,
            "ServiceProvider": "Uber",
            "LicensePlate": "D1AL 0G",
        }
        for i in range(300):
            api.dbs["ride"].add_item(item_we_probably_find)
        api.dbs["ride"].add_item(
            {
                "id": 1009,
                "Price": 12,
                "MinutesTillPickup": 7,
                "ServiceProvider": "Taxi",
                "LicensePlate": "MAG 1C",
            }
        )
    if opt["wizard_intro"]:
        opt["dummy_user"] = True
        api.dbs["ride"].add_item(
            {"id": 1000, "Price": 20, "ServiceProvider": "Uber", "DriverName": "Zoe",}
        )
        api.dbs["ride"].add_item(
            {
                "id": 1001,
                "Price": 21,
                "ServiceProvider": "Taxi",
                "DriverName": "Sirius",
                "CarModel": "Tesla",
                "LicensePlate": "MAG 1C",
            }
        )

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

    # has_passed_wizard_tutorial_20200320_qualification = mturk_utils.find_or_create_qualification(
    #     "WOZ-HasPassedWizardTutorial-20200320",
    #     "Workers with this qualification have passed the wizard tutorial in its state from 2020-03-20.",
    #     opt["is_sandbox"],
    # )
    #
    # has_passed_wizard_tutorial_20200324_qualification = mturk_utils.find_or_create_qualification(
    #     "WOZ-HasPassedWizardTutorial-20200324",
    #     "Workers with this qualification have passed the wizard tutorial in its state from 2020-03-24.",
    #     opt["is_sandbox"],
    # )
    #
    # has_failed_wizard_tutorial_20200320_qualification = mturk_utils.find_or_create_qualification(
    #     "WOZ-HasFailedWizardTutorial-20200320",
    #     "Workers with this qualification have failed the wizard tutorial in its state from 2020-03-20.",
    #     opt["is_sandbox"],
    # )
    #
    # has_failed_wizard_tutorial_20200324_qualification = mturk_utils.find_or_create_qualification(
    #     "WOZ-HasFailedWizardTutorial-20200324",
    #     "Workers with this qualification have failed the wizard tutorial in its state from 2020-03-24.",
    #     opt["is_sandbox"],
    # )
    has_passed_wizard_tutorial_20200406_qualification = mturk_utils.find_or_create_qualification(
        "WOZ-HasPassedWizardTutorial-20200406",
        "Workers with this qualification have passed the second wizard video tutorial (state from 2020-04-06).",
        opt["is_sandbox"],
    )

    # opt["block_qualification"] = "WOZ-HasFailedWizardTutorial-20200324"

    qualification_manager = MTurkQualificationManager()
    # if opt["wizard_intro"]:
    qualification_manager.require_locales(["US"])
    qualification_manager.require_min_approved_hits(10000)
    qualification_manager.require_min_approval_rate(98)
    #     qualification_manager.require_existence(
    #         has_passed_wizard_tutorial_20200320_qualification,
    #         exists=False,
    #     )
    # else:
    #     qualification_manager.require_existence(
    #         has_passed_wizard_tutorial_20200324_qualification,
    #         exists=True,
    #     )
    # qualification_manager.require_existence(
    #     has_failed_wizard_tutorial_20200320_qualification,
    #     exists=False
    # )
    # qualification_manager.require_existence(
    #     has_failed_wizard_tutorial_20200324_qualification,
    #     exists=False
    # )

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
        original_id = worker.worker_id
        if role == "Wizard":
            worker.update_agent_id("Wizard")
            world = WizardOnboardingWorld(opt=opt, mturk_agent=worker, worker_id=original_id)
            if worker.passed_onboarding and isinstance(worker, MTurkAgent):
                mturk_utils.give_worker_qualification(
                    original_id,
                    has_passed_wizard_tutorial_20200406_qualification,
                    is_sandbox=opt["is_sandbox"],
                )
        elif role == "User":
            worker.update_agent_id("User")
            world = UserOnboardingWorld(opt=opt, mturk_agent=worker, worker_id=original_id)
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

        # Load scenarios
        scenarios_list_fn = os.path.join(
            PROJECT_PATH,
            "parlai",
            "mturk",
            "tasks",
            "woz",
            "scenarios",
            opt.get("scenario_list") + ".txt",
        )
        scenarios_list = [e.strip() for e in open(scenarios_list_fn).readlines()]
        # random.shuffle(scenarios_list)

        # Set up the sockets and threads to receive workers
        mturk_manager.ready_to_accept_workers()

        # Create the HITs
        mturk_manager.create_hits(qualifications=qualification_manager.qualifications)
        # print("Qualification Requirements:")
        # for q in qualification_manager.qualifications:
        #     print(f"  {q}")

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
        scenario_index: int = 0

        def run_conversation(mturk_manager, opt, workers):

            kb_agent = WOZKnowledgeBaseAgent(options=opt)
            workers += [kb_agent]

            user_tutor_agent = create_user_instructor(opt)
            # workers += [user_tutor_agent]

            if opt["dummy_user"]:
                if opt["wizard_intro"]:
                    dummy_user = WOZWizardIntroAgent(opt, "User")
                else:
                    dummy_user = WOZDummyAgent(opt, "User")
                workers += [dummy_user]

            nonlocal scenario_index
            scenario = scenarios_list[scenario_index % len(scenarios_list)]
            scenario_index += 1

            # Create the task world
            # if opt["wizard_intro"]:
            # world = WOZWizardTutorialWorld(
            #     opt=opt,
            #     agents=workers,
            #     qualification_on_success=has_passed_wizard_tutorial_20200324_qualification,
            # )
            # else:
            world = WOZWorld(
                opt=opt,
                scenario=scenario,
                agents=workers,
                observers=[],  # [user_tutor_agent]
            )

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
