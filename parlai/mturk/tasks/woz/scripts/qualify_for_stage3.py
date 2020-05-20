#!/usr/bin/env python3
from typing import Set

import parlai.mturk.core.mturk_utils as mturk_utils

first_class_workers = [
    # Most experience
    "A1ZE52NWZPN85P",
    "A3RHJEMZ4EGY2U",
    "AWPB724OHY99T",
    "A1UTBDKOQ2MKUD",
    "AX3N0BBAJ39GG",
    "A26LOVXF4QZZCO",
    "A1HAOXJVRYT43K",
    "A272X64FOZFYLB",
    "A3IDG9C18BCATK",
    "A6AB1O0UYB7PI",
    "A3PYB8Z6FFWSOV",
    "A3TUJHF9LW3M8N",
    "ATJVY9O4CY5EX",
    "A2ER0EVZ7E1Z8G",
    "A3D6VDP1APQF3D",
    # Longest average user utterances (but at least 10 dialogues)
    "A1WR3WTEHJEY2D",
    "A3PYB8Z6FFWSOV",
    "A3T01NM4993LZE",
    "A27861Q24LU68U",
    "ALDQRWYZ8KQ9A",
    "A3NMQ3019X6YE0",
    "A2KW17G25L25R8",
    "A302KOFOYLD89A",
    "AJQGWGESKQT4Y",
    "A2ER0EVZ7E1Z8G",
    # Workers who asked good questions or submitted good dialogues
    "A2STG331R3P3FK",  # EllieMayC (Asked for help)
    "A3AIX82WZQZB5A",  # Tom Davis (Asked for help)
    "A2HC9549CZAKNN",  # Brendon McCarthy (Happy worker)
    "A2MEZ3IXRFNT0E",  # Lorena Hernandez (Happy worker)
    "A3TUJHF9LW3M8N",  # Sarah kellner (Happy worker)
]


def grant_stage3_qualification(workers: Set, is_sandbox: bool = True) -> None:

    mturk_utils.setup_aws_credentials()
    client = mturk_utils.get_mturk_client(False)

    qualification = mturk_utils.find_or_create_qualification(
        "ReadyForAIDialoguesTutorial2",
        "If owned, the worker can enter Stage III of the AI Dialogues tasks.",
        is_sandbox
    )

    for worker in workers:
        print(f"Qualifying {worker}")

        client.associate_qualification_with_worker(
            QualificationTypeId=qualification,
            WorkerId=worker,
            IntegerValue=1,
            SendNotification=True,
        )


if __name__ == '__main__':
    print(f"{len(first_class_workers)} -- {len(set(first_class_workers))}")

    # grant_stage3_qualification({"A1I1OIUHZLZRDO"})
    grant_stage3_qualification(set(first_class_workers), is_sandbox=False)
