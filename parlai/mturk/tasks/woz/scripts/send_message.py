#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import parlai.mturk.core.mturk_utils as mturk_utils


def main():

    mturk_utils.setup_aws_credentials()
    client = mturk_utils.get_mturk_client(False)

    # client.notify_workers(
    #     Subject="AI Dialogues - Stage II [v2]",
    #     MessageText="Hi! \n\nThanks for going though Stage I of the AI Dialogues tasks! We just want to let you know that the Stage II task is currently running, and you can find it under the name 'AI Dialogues - Stage II (Single Task Dialogues) [v2]'. If it doesn't have a '[v2]' in the end, then its an older version where the server broke down, so that HIT won't work. Thus, look out for the '[v2]' :) \n\nBest wishes\nJohannes",
    #     WorkerIds=["A11P1OS26E6AMO", "A1V2H0UF94ATWY", "A1WR3WTEHJEY2D", "A27861Q24LU68U", "A2HC9549CZAKNN", "A2I4A4WGWII18Z", "A2J9U65SKT4TJW", "A2JBNDG0U9IA6I","A2KW17G25L25R8", "A2N9U74YIPDQ9F", "A2VA0NCPWJ8XZG", "A2WC2NO555XU3J", "A2XK59FYAFO9EX", "A2ZA3X3DBEMBCD", "A339YQ2DS0BS8R", "A33B85TN97HQ33", "A37XJVQF62ZYC","A39MOCMDRIOSJM","A3NHJPE6326P9V", "A3QN9B9ZS1CWWM", "A3SKEW89V5S0DI", "A3TUJHF9LW3M8N", "AJQGWGESKQT4Y", "ARLGZWN6W91WD", "ATUCGR0S3K69G","AURYD2FH3FUOQ","AX3N0BBAJ39GG"]
    # )

    # workers = ["A1F1OZ54G177D8", "AWPB724OHY99T", "A2WC2NO555XU3J", "A1ZE52NWZPN85P", "A3T01NM4993LZE", "A3TUJHF9LW3M8N", "A2TZAXWOB3JMNV", "A2ER0EVZ7E1Z8G", "A3IDG9C18BCATK", "A1ZE52NWZPN85P", "A1F1OZ54G177D8", "A2TZAXWOB3JMNV", "A2VU8AC7MY3721", "A6AB1O0UYB7PI", "A2MGH3MBXMKD96", "A2TZAXWOB3JMNV", "A1171IQSWQS0K8", "A1ZE52NWZPN85P", "AJQGWGESKQT4Y", "A2MD4K1YFYBLZN", "A2Y5I2HJTRFR8H", "A2TZAXWOB3JMNV", "A1ZE52NWZPN85P", "A3TWYQENN82FJI", "A2HC9549CZAKNN", "AWPB724OHY99T", "ATJVY9O4CY5EX", "A2TZAXWOB3JMNV", "A1171IQSWQS0K8", "A1ZE52NWZPN85P", "A12DY4HHG6MYF0", "A2TZAXWOB3JMNV", "A1BZ1VD8V8VJML", "A1ZE52NWZPN85P", "A3HBMKX19GBOGR", "A1ZE52NWZPN85P", "A6AB1O0UYB7PI", "A3TUJHF9LW3M8N", "A1F1OZ54G177D8", "A6AB1O0UYB7PI", "A37XJVQF62ZYC", "A1K5ILJMG439M5", "A1ZE52NWZPN85P", "AOEO9ZV81R0I4", "A2GJK2MDTHNQ6Q", "A6AB1O0UYB7PI", "A01913642LJT7L89AFM2F", "A3I9XLIHPPWPN1", "AWPB724OHY99T", "A23EWFNNOUS10B", "A3NHJPE6326P9V", "A1ZE52NWZPN85P", "A37XJVQF62ZYC", "A6AB1O0UYB7PI", "A6AB1O0UYB7PI", "AJQGWGESKQT4Y", "A3TUJHF9LW3M8N", "A22TLF121MRXT1", "A2Y5I2HJTRFR8H", "A1ZE52NWZPN85P", "A2JBNDG0U9IA6I", "A3TUJHF9LW3M8N", "A3HBMKX19GBOGR", "A6AB1O0UYB7PI", "A2GJK2MDTHNQ6Q", "A3TUJHF9LW3M8N", "A2HC9549CZAKNN", "AOEO9ZV81R0I4", "A2KW17G25L25R8", "A6AB1O0UYB7PI", "A2TZAXWOB3JMNV", "A2LAE3OM5OQ0WF", "A1UTBDKOQ2MKUD", "A1CY7IOJ9YH136", "A2JBNDG0U9IA6I", "AMELYCC59JKB0", "A2EOOF9D135HQ1", "A2MGH3MBXMKD96", "A6AB1O0UYB7PI", "A1ZE52NWZPN85P", "A1UTBDKOQ2MKUD", "A1ZE52NWZPN85P", "A1UTBDKOQ2MKUD", "A1ZE52NWZPN85P", "A1ZE52NWZPN85P", "A6AB1O0UYB7PI", "A2ER0EVZ7E1Z8G", "AWPB724OHY99T", "A2L73JKDFWI0KJ", "A1ZE52NWZPN85P", "AWPB724OHY99T", "A37XJVQF62ZYC", "ALDQRWYZ8KQ9A", "A6AB1O0UYB7PI", "A2LAE3OM5OQ0WF", "A6AB1O0UYB7PI", "A1UTBDKOQ2MKUD", "A2TZAXWOB3JMNV", "A2TZAXWOB3JMNV", "AWPB724OHY99T", "A1BZ1VD8V8VJML", "A163J5TEJBO43B", "A2EOOF9D135HQ1", "AWPB724OHY99T", "ANBWJZYU2A68T", "A12DY4HHG6MYF0", "A3PYB8Z6FFWSOV", "A1BZ1VD8V8VJML", "A2TZAXWOB3JMNV", "A1ZE52NWZPN85P", "AWPB724OHY99T", "A22TLF121MRXT1", "A39MOCMDRIOSJM", "AOEO9ZV81R0I4", "A3IDG9C18BCATK", "AL8KOIH1DJ7D9", "A1CY7IOJ9YH136", "A6AB1O0UYB7PI", "A2MGH3MBXMKD96", "A1ZE52NWZPN85P", "A3CDG9TL8U99CO", "A1ZE52NWZPN85P", "A6AB1O0UYB7PI", "AWPB724OHY99T", "A3TWYQENN82FJI", "A39MOCMDRIOSJM", "A39MOCMDRIOSJM", "AJQGWGESKQT4Y", "A1UTBDKOQ2MKUD", "A1ZE52NWZPN85P", "A6AB1O0UYB7PI", "AWPB724OHY99T", "A6AB1O0UYB7PI", "A2GJK2MDTHNQ6Q", "A3NHJPE6326P9V", "A6AB1O0UYB7PI", "A1ZE52NWZPN85P", "A6AB1O0UYB7PI", "A2MGH3MBXMKD96", "AL8KOIH1DJ7D9", "A6AB1O0UYB7PI", "A1F1OZ54G177D8", "A33B85TN97HQ33", "A1ZE52NWZPN85P", "A1BZ1VD8V8VJML", "A33B85TN97HQ33", "A2JBNDG0U9IA6I", "A6AB1O0UYB7PI", "A3AIX82WZQZB5A", "AWPB724OHY99T", "A3CDG9TL8U99CO", "ACRTRQ23XH20E", "ATJVY9O4CY5EX", "A2TZAXWOB3JMNV", "A2EOOF9D135HQ1", "A2TZAXWOB3JMNV", "A3NHJPE6326P9V", "A2GJK2MDTHNQ6Q", "ANBWJZYU2A68T", "A2R0YYUAWNT7UD", "A2HC9549CZAKNN", "A2TZAXWOB3JMNV", "A2KW17G25L25R8", "A1ZE52NWZPN85P", "A2EOOF9D135HQ1", "AWPB724OHY99T", "A2KW17G25L25R8", "A6AB1O0UYB7PI"];
    workers = ["A272X64FOZFYLB", "A2ER0EVZ7E1Z8G", "A1HAOXJVRYT43K", "A6AB1O0UYB7PI"]
    # workers = []

    while workers:
        worker_batch = workers[:80]
        workers = workers[80:]
        print(f"Sending message to {worker_batch}")
        client.notify_workers(
            Subject="AI Dialogues - Stage IV Feedback",
            MessageText="Hello! "
                        ""
                        "Thank you for participating in the first Stage IV batch of our AI Dialogues. "
                        "We are still working out some details, but are already quite happy with the dialogues that we've seen. "
                        "However, we also noticed that nobody has done the long instruction sets (where we pay overtime bonus). "
                        "I am writing to you to get some feedback on why that might be. "
                        ""
                        "Is the risk of partner-disconnect to high? Or are long tasks generally not interesting? What can we do to improve? "
                        ""
                        "I am looking forward to hear your thoughts on this."
                        ""
                        "\n\nBest wishes\nJohannes",
            WorkerIds=worker_batch
        )


if __name__ == '__main__':
    main()
