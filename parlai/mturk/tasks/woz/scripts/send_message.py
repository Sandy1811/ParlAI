#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import parlai.mturk.core.mturk_utils as mturk_utils


def main():

    mturk_utils.setup_aws_credentials()
    client = mturk_utils.get_mturk_client(False)

    client.notify_workers(Subject="AI Dialogues - Stage II [v2]", MessageText="Hi! \n\nThanks for going though Stage I of the AI Dialogues tasks! We just want to let you know that the Stage II task is currently running, and you can find it under the name 'AI Dialogues - Stage II (Single Task Dialogues) [v2]'. If it doesn't have a '[v2]' in the end, then its an older version where the server broke down, so that HIT won't work. Thus, look out for the '[v2]' :) \n\nBest wishes\nJohannes", WorkerIds=["A11P1OS26E6AMO", "A1V2H0UF94ATWY", "A1WR3WTEHJEY2D", "A27861Q24LU68U", "A2HC9549CZAKNN", "A2I4A4WGWII18Z", "A2J9U65SKT4TJW", "A2JBNDG0U9IA6I","A2KW17G25L25R8", "A2N9U74YIPDQ9F", "A2VA0NCPWJ8XZG", "A2WC2NO555XU3J", "A2XK59FYAFO9EX", "A2ZA3X3DBEMBCD", "A339YQ2DS0BS8R", "A33B85TN97HQ33", "A37XJVQF62ZYC","A39MOCMDRIOSJM","A3NHJPE6326P9V", "A3QN9B9ZS1CWWM", "A3SKEW89V5S0DI", "A3TUJHF9LW3M8N", "AJQGWGESKQT4Y", "ARLGZWN6W91WD", "ATUCGR0S3K69G","AURYD2FH3FUOQ","AX3N0BBAJ39GG"])


if __name__ == '__main__':
    main()
