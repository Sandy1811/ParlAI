#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
from parlai.mturk.core import mturk_utils
from parlai.mturk.core.mturk_manager import MTurkManager
from parlai.mturk.tasks.woz.qualify import MTurkQualificationManager
from parlai.mturk.tasks.woz_tutorial_advanced.task_config import task_config
import os

from parlai.mturk.tasks.woz_tutorial_advanced.worlds import TutorialWorld1


def main():
    """
    Handles setting up and running a ParlAI-MTurk task by instantiating an MTurk manager
    and configuring it for the qa_data_collection task.
    """
    # Get relevant arguments
    argparser = ParlaiParser(False, False)
    argparser.add_parlai_data_path()
    argparser.add_mturk_args()
    opt = argparser.parse_args()

    # Set the task name to be the folder name
    opt['task'] = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    # append the contents of task_config.py to the configuration
    opt.update(task_config)

    # Select an agent_id that worker agents will be assigned in their world
    mturk_agent_id = 'Worker'

    # Instantiate an MTurkManager with the given options and a maximum number
    # of agents per world of 1 (based on the length of mturk_agent_ids)
    mturk_manager = MTurkManager(opt=opt, mturk_agent_ids=[mturk_agent_id], use_db=True)
    mturk_manager.setup_server()

    # If we want to use the above onboard function, we can replace the below
    # with set_onboard_function(onboard_function=run_onboard)
    mturk_manager.set_onboard_function(onboard_function=None)

    required_qualification_id = mturk_utils.find_or_create_qualification(
        "ReadyForAIDialoguesTutorial2",
        "If owned, the worker can enter Stage III of the AI Dialogues tasks.",
        opt['is_sandbox']
    )
    qualification_id = mturk_utils.find_or_create_qualification(
        "PassedAIDialoguesTutorial2",
        "If owned, the worker has passed the AI Dialogues Tutorial 2. The value corresponds to the number of hints that the worker used.",
        opt['is_sandbox']
    )
    qualification_manager = MTurkQualificationManager()
    qualification_manager.require_existence(required_qualification_id)

    try:
        # Initialize run information
        mturk_manager.start_new_run()

        # Set up the sockets and threads to recieve workers
        mturk_manager.ready_to_accept_workers()

        # Create the hits as specified by command line arguments
        mturk_manager.create_hits(qualifications=qualification_manager.qualifications)

        # Check workers eligiblity acts as a filter, and should return
        # the list of all workers currently eligible to work on the task
        def check_workers_eligibility(workers):
            return workers

        eligibility_function = {'func': check_workers_eligibility, 'multiple': True}

        # Assign worker roles is used to determine what the role each worker
        # in the given worker list will play. Setting `id` to None will return
        # the worker to the pool rather than putting them in a given task,
        # which is useful for having tasks with different possible worker
        # counts.
        def assign_worker_roles(workers):
            workers[0].id = mturk_agent_id

        # Define the task function, which will be run with workers that are
        # as the main task.
        global run_conversation

        def run_conversation(mturk_manager, opt, workers):
            # Create the task world
            world = TutorialWorld1(opt=opt, mturk_agent=workers[0], qualification_id=qualification_id)
            # run the world to completion
            while not world.episode_done():
                world.parley()

            print(f"{workers[0]} is done")

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
