import argparse
from datetime import date
from datetime import datetime
import json
import logging
import os
from pprint import pformat

import config
import csv_util
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
    config.dest_bucket_name = get_env_var("DEST_BUCKET_NAME")
    if config.dest_bucket_name == "":
        print("get_env_vars: failed to retrieve DEST_BUCKET_NAME.")
        return False
        
    config.region_name = get_env_var("REGION_NAME")
    if config.region_name == "":
        print("get_env_vars: failed to retrieve REGION_NAME.")
        return False
        
    # DEBUG
    print("get_env_vars:")
    print("dest_bucket_name: %s" % (config.dest_bucket_name))
    print("region_name: %s" % (config.region_name))
    
    return True


def get_event_vars(event):
    # DMS erplication task id
    config.replication_task_id = ""
    dms_event_message_str = event['Records'][0]['Sns']['Message']
    print("[DEBUG] get_event_vars: DMS event message string = %s" % dms_event_message_str)
    dms_event_message = json.loads(dms_event_message_str)
    print("[DEBUG] get_event_vars: DMS event message = %s" % dms_event_message)
    config.replication_task_id = dms_event_message['SourceId']
    
    # initialize DMS replication task ARN
    config.replication_task_arn = ""
    
    # DEBUG
    print("get_event_vars:")
    print("replication_task_id: %s" % (config.replication_task_id))
    print("replication_task_arn: %s" % (config.replication_task_arn))
    
    return True
    
    
def prepend_column(column_header, column_value, data):
    for i, d in enumerate(data):
        data[i] = {column_header: column_value, **d}
        
    return data


def lambda_handler(event, context):
    # start
    print('\nStarting lambda_function.lambda_handler ...')
    LOGGER.info("%s", pformat({"Context" : context, "Request": event}))
    
    # get environment variables
    if get_env_vars() == False:
        print("dms-task-table-stats: get_env_vars() failed.")
        return False
        
    # get event variables
    if get_event_vars(event) == False:
        print("dms-task-table-stats: get_event_vars() failed.")
        return False
        
    # check if replication task status is now stopped
    task_status = dms_util.get_task_status(config.replication_task_id)
    if task_status == 'stopped':
        # get table stats
        print("dms-task-table-stats: Task %s is stopped. Getting table stats ..." % (config.replication_task_arn))
        table_stats = dms_util.get_table_stats(config.replication_task_arn)
        print("dms-task-table-stats: Printing table stats for task %s ..." % (config.replication_task_arn))
        print("==")
        print("table_stats")
        print("==")
        print(table_stats)
        print("==")
    
        # prepend task_id to table_stats table
        task_id = config.replication_task_id
        table_stats_ext = prepend_column("TaskId", task_id, table_stats)
        #table_stats_ext = prepend_column("TableOwner", "db", table_stats_ext)
        #table_stats_ext = prepend_column("Table", "dms_task_table_stats", table_stats_ext)
        #table_stats_ext = prepend_column("Operation", "INSERT", table_stats_ext)
        print("==")
        print("table_stats_ext")
        print("==")
        print(table_stats_ext)
        print("==")
        
        # set dest_object_prefix and dest_object_name
        #today = date.today()
        #dest_object_prefix = "date="+str(today)+"/"
        #dest_object_prefix = "db/dms_task_table_stats/cdc/"
        dest_object_prefix = "db/dms_task_table_stats/"
        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        dest_object_name = timestamp+".csv"
        
        print("dms-task-table-stats: Writing and uploading table stats as:")
        print("dest_bucket_name: %s" % (config.dest_bucket_name))
        print("dest_object_prefix: %s" % (dest_object_prefix))
        print("dest_object_name: %s" % (dest_object_name))
        
        # write csv file
        csv_util.write_csv_file(table_stats, dest_object_name, write_header=False)
        
        # upload csv file to dest bucket
        csv_util.put_csv_file_as_s3_object(config.dest_bucket_name, dest_object_prefix, dest_object_name)
    else:
        print("dms-task-table-stats: Task %s is %s." % (config.replication_task_arn, task_status))

    # end
    print('\n... Thaaat\'s all, Folks!')


if __name__ == '__main__':
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--test-event", required=True, help="Test event.")
    args = vars(ap.parse_args())
    print("dms-task-table-stats: args = %s" % (args))

    # load json file
    test_event_file_name = args['test_event']
    f = open(test_event_file_name)
    event = json.load(f)
    f.close()
    print("dms-task-table-stats: test_event = %s" % (event))

    # create test context
    context = {}

    # Execute test
    lambda_handler(event, context)

