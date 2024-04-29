import boto3
from botocore.exceptions import ClientError
import json
import logging

import config


def get_dms_client():
    print('get_dms_client: profile_name=%s, region_name=%s' % (config.profile_name, config.region_name))

    p_name = None
    if (config.profile_name != ''):
        p_name = config.profile_name
    session = boto3.Session(profile_name=p_name)
    dms = session.client('dms', region_name=config.region_name)
    return dms
    
    
def start_replication_task(start_task_arn, start_task_type):
    start_task_id = ""
    
    dms = get_dms_client()
    if dms is None:
        print('start_replication_task: Failed to get dms client.')
        return start_task_id
    
    try:
        response = dms.start_replication_task(ReplicationTaskArn=start_task_arn, StartReplicationTaskType=start_task_type)
        print("[DEBUG] start_replication_task: response from start_replication_task = %s." % (response))
        
        start_task_id = response['ReplicationTaskIdentifier']
        print("[DEBUG] start_replication_task: start_task_id = %s." % (start_task_id))

    except ClientError as e:
        logging.error("start_replication_task: unexpected error: ")
        logging.exception(e)
        return start_task_id

    return start_task_id

