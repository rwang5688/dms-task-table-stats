import argparse
from datetime import datetime
import json
import logging
import os
from pprint import pformat

import config
import dms_util


LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)


def get_env_var(env_var_name):
    env_var = ""
    if env_var_name in os.environ:
        env_var = os.environ[env_var_name]
    else:
        print('get_env_var: Failed to get %s' % env_var_name)
    return env_var


def get_env_vars():
    config.region_name = get_env_var("REGION_NAME")
    if config.region_name == "":
        print("get_env_vars: failed to retrieve REGION_NAME.")
        return False

    config.start_task_arn = get_env_var("START_TASK_ARN")
    if config.start_task_arn == "":
        print("get_env_vars: failed to retrieve START_TASK_ARN.")
        return False
        
    config.start_task_type = get_env_var("START_TASK_TYPE")
    if config.start_task_type == "":
        print("get_env_vars: failed to retrieve START_TASK_TYPE.")
        return False
        
    # DEBUG
    print("get_env_vars:")
    print("region_name: %s" % (config.region_name))
    print("start_task_arn: %s" % (config.start_task_arn))
    print("start_task_type: %s" % (config.start_task_type))
    
    return True


def get_event_vars(event):
    # Initialize start task id
    config.start_task_id = ""
    
    # DEBUG
    print("get_event_vars:")
    print("start_task_id: %s" % (config.start_task_id))
    
    return True
    
    
def lambda_handler(event, context):
    # start
    print('\nStarting lambda_function.lambda_handler ...')
    LOGGER.info("%s", pformat({"Context" : context, "Request": event}))
    
    # get environment variables
    if get_env_vars() == False:
        print("start-dms-task: get_env_vars() failed.")
        return False
        
    # get event variables
    if get_event_vars(event) == False:
        print("start-dms-task: get_event_vars() failed.")
        return False
        
    config.start_task_id = dms_util.start_replication_task(config.start_task_arn, config.start_task_type)
    if config.start_task_id == "":
        print("start-dms-task: start_task_id is empty.  Unexpected error.")
    else:
        print("start-dms-task: start_task_id = %s has been started." % (config.start_task_id))
        
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    print("start-dms-task: Current UTC (Universal Time Coordinated) Time is: %s." % (timestamp))
    
    # end
    print('\n... Thaaat\'s all, Folks!')
    
    
if __name__ == '__main__':
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--test-event", required=True, help="Test event.")
    args = vars(ap.parse_args())
    print("start-dms-task: args = %s" % (args))

    # load json file
    test_event_file_name = args['test_event']
    f = open(test_event_file_name)
    event = json.load(f)
    f.close()
    print("start-dms-task: test_event = %s" % (event))

    # create test context
    context = {}

    # Execute test
    lambda_handler(event, context)
    
    