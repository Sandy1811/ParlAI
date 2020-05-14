
import parlai.mturk.core.mturk_utils as mturk_utils


def main():

    mturk_utils.setup_aws_credentials()
    client = mturk_utils.get_mturk_client(False)

    assignment_id = input("Assignment ID: ")
    reason = input("Reason: ")

    response = client.approve_assignment(AssignmentId=assignment_id, RequesterFeedback=reason, OverrideRejection=True)

    print(response)


if __name__ == '__main__':
    main()
