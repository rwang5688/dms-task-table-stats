import argparse
import json
import logging
from pprint import pformat

import config
import dms_util


LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)


def get_event_vars(event):
    # AWS parameters
    #config.profile_name = event['profile_name']
    config.region_name = event['region']

    # DEBUG
    print("get_event_vars:")
    print("profile_name: %s" % (config.profile_name))
    print("region_name: %s" % (config.region_name))


def lambda_handler(event, context):
    # start
    print('\nStarting lambda_function.lambda_handler ...')
    LOGGER.info("%s", pformat({"Context" : context, "Request": event}))

    # get event variables
    get_event_vars(event)

    # get replication_task_arn
    replication_task_arn = ""
    resources = event['resources']
    for resource in resources:
        replication_task_arn = resource
    print("dms-replication-task-event: replication_task_arn = %s" % (replication_task_arn))
    
    # check if replication task status is now stopped
    task_status = dms_util.get_task_status(replication_task_arn)
    if task_status == 'stopped':
        print("dms-replication-task-event: Task %s is stopped. Getting table stats ..." % (replication_task_arn))
        table_stats = dms_util.get_table_stats(replication_task_arn)
        print("dms-replication-task-event: Printing table stats for task %s ..." % (replication_task_arn))
        print("===")
        print(table_stats)
        print("==")
    else:
        print("dms-replication-task-event: Task %s is %s." % (replication_task_arn, task_status))

    # end
    print('\n... Thaaat\'s all, Folks!')


if __name__ == '__main__':
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--test-event", required=True, help="Test event.")
    args = vars(ap.parse_args())
    print("dms-replication-task-event: args = %s" % (args))

    # load json file
    test_event_file_name = args['test_event']
    f = open(test_event_file_name)
    event = json.load(f)
    f.close()
    print("dms-replication-task-event: test_event = %s" % (event))

    # create test context
    context = {}

    # Execute test
    lambda_handler(event, context)

