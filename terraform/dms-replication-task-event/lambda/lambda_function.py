import argparse
import json
import logging
import os
from pprint import pformat

import config
import dms_util


LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)


def get_event_vars(event):
    # AWS parameters
    #config.profile_name = ""
    #config.profile_name = event['profile_name']
    config.region_name = ""
    config.region_name = event['region']
    
    # DMS replication task ARN
    config.replication_task_arn = ""
    resources = event['resources']
    for resource in resources:
        if "arn:aws:dms" in resource and "task" in resource:
            config.replication_task_arn = resource
    
    # DEBUG
    print("get_event_vars:")
    print("profile_name: %s" % (config.profile_name))
    print("region_name: %s" % (config.region_name))
    print("replication_task_arn: %s" % (config.replication_task_arn))
    
    
def get_env_var(env_var_name):
    env_var = ""
    if env_var_name in os.environ:
        env_var = os.environ[env_var_name]
    else:
        print('get_env_var: Failed to get %s' % env_var_name)
    return env_var


def get_env_vars():
    if config.replication_task_arn == "":
        # WORKAROUND: get_event_vars() has failed to set config.replication_task_arn
        print("[WORKAROUND] get_env_vars: retrieving REPLICATION_TASK_ARN.")
        config.replication_task_arn = get_env_var('REPLICATION_TASK_ARN')
        if config.replication_task_arn == "":
            print("get_env_vars: failed to retrieve REPLICATION_TASK_ARN.")
            return False
        
    # DEBUG
    print("get_env_vars:")
    print("replication_task_arn: %s" % (config.replication_task_arn))
    
    return True
    

def lambda_handler(event, context):
    # start
    print('\nStarting lambda_function.lambda_handler ...')
    LOGGER.info("%s", pformat({"Context" : context, "Request": event}))

    # get event variables
    get_event_vars(event)
    
    # get environment variables
    if get_env_vars() == False:
        print("dms-replication-task-event: get_env_vars() failed.")
        return False
        
    # check if replication task status is now stopped
    task_status = dms_util.get_task_status(config.replication_task_arn)
    if task_status == 'stopped':
        print("dms-replication-task-event: Task %s is stopped. Getting table stats ..." % (config.replication_task_arn))
        table_stats = dms_util.get_table_stats(config.replication_task_arn)
        print("dms-replication-task-event: Printing table stats for task %s ..." % (config.replication_task_arn))
        print("===")
        print(table_stats)
        print("==")
    else:
        print("dms-replication-task-event: Task %s is %s." % (config.replication_task_arn, task_status))

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

