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

all_workers_with_at_least_10_wizard_HITs = [
    "A1ZE52NWZPN85P",
    "A3RHJEMZ4EGY2U",
    "AWPB724OHY99T",
    "A1UTBDKOQ2MKUD",
    "A1HAOXJVRYT43K",
    "AX3N0BBAJ39GG",
    "A272X64FOZFYLB",
    "A26LOVXF4QZZCO",
    "A3IDG9C18BCATK",
    "A2ER0EVZ7E1Z8G",
    "A6AB1O0UYB7PI",
    "A3PYB8Z6FFWSOV",
    "A3TUJHF9LW3M8N",
    "ATJVY9O4CY5EX",
    "A2HC9549CZAKNN",
    "A3D6VDP1APQF3D",
    "A17TKHT8FEVH0R",
    "AOMFEAWQHU3D8",
    "A2959L16M8OES7",
    "A2F2DDH12YU4AK",
    "A39MOCMDRIOSJM",
    "A2GJK2MDTHNQ6Q",
    "A2JBNDG0U9IA6I",
    "A1RHBKSDCWZTUC",
    "A2KW17G25L25R8",
    "AJQGWGESKQT4Y",
    "A302KOFOYLD89A",
    "A1171IQSWQS0K8",
    "A3CDG9TL8U99CO",
    "A1CY7IOJ9YH136",
    "A1WR3WTEHJEY2D",
    "A9HQ3E0F2AGVO",
    "A2MEZ3IXRFNT0E",
    "A12DY4HHG6MYF0",
    "A37XJVQF62ZYC",
    "A2LAE3OM5OQ0WF",
    "A1A1ZXUVSV4YR8",
    "A2JJ3531QBNT5K",
    "A2L73JKDFWI0KJ",
    "A2MGH3MBXMKD96",
    "AJACXA5FC5BYZ",
    "A16184N1RO5OJV",
    "AHIJACUG7ZL9B",
    "A3HBMKX19GBOGR",
    "AXY0D2AMLKE2A",
    "A3HTLXAPOBCVVO",
    "ALDQRWYZ8KQ9A",
    "A1F1OZ54G177D8",
    "A2ONILC0LZKG6Y",
    "A2Y5I2HJTRFR8H",
    "A3PAM3UNU3OK89",
    "A2VU8AC7MY3721",
    "ANBWJZYU2A68T",
    "A2TZAXWOB3JMNV",
    "A3AIX82WZQZB5A",
    "ARLGZWN6W91WD",
    "A3NMQ3019X6YE0",
    "A2STG331R3P3FK",
    "AKZL9O3LVHYCH",
    "A1BZ1VD8V8VJML",
    "A2EOOF9D135HQ1",
    "A27861Q24LU68U",
    "A3T01NM4993LZE",
    "A1S1K7134S2VUC",
    "A2WC2NO555XU3J",
    "A163J5TEJBO43B",
    "A33B85TN97HQ33",
    "A3NHJPE6326P9V",
    "A3HL2LL0LEPZT8",
    "A2MD4K1YFYBLZN",
    "ACRTRQ23XH20E",
    "AIC8CB12DQC0K",
    "A01913642LJT7L89AFM2F",
]


def grant_stage3_qualification(workers: Set, is_sandbox: bool = True) -> None:

    mturk_utils.setup_aws_credentials()
    client = mturk_utils.get_mturk_client(False)

    qualification = mturk_utils.find_or_create_qualification(
        "ReadyForAIDialoguesTutorial2",
        "If owned, the worker can enter Stage III of the AI Dialogues tasks.",
        is_sandbox,
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
    # grant_stage3_qualification(set(first_class_workers), is_sandbox=False)
    grant_stage3_qualification(set(all_workers_with_at_least_10_wizard_HITs), is_sandbox=False)
