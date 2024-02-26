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


def get_task_status(replication_task_id):
    task_status = ""

    dms = get_dms_client()
    if dms is None:
        print('get_task_status: Failed to get dmsclient.')
        return task_status
    
    try:
        filters = []
        filter = {}
        filter['Name'] = 'replication-task-id'
        filter['Values'] = []
        filter['Values'].append(replication_task_id)
        filters.append(filter)
        print("get_task_status: Invoke describe_replication_tasks with filters = %s." % (filters))

        response = dms.describe_replication_tasks(Filters=filters)
        print("[DEBUG] get_task_status: response from describe_replication_tasks = %s." % (response))

        replication_tasks = response['ReplicationTasks']
        for task in replication_tasks:
            task_id = task['ReplicationTaskIdentifier']
            # make sure we have the correct task
            if task_id == replication_task_id:
                config.replication_task_arn = task['ReplicationTaskArn']
                print("[DEBUG] get_task_status: config.replication_task_arn = %s." % (config.replication_task_arn))
                task_status = task['Status']
                print("[DEBUG] get_task_status: task_status = %s." % (task_status))

    except ClientError as e:
        logging.error("get_task_status: unexpected error: ")
        logging.exception(e)
        return task_status
    
    return task_status


def get_table_stats(replication_task_arn):
    table_stats = []

    dms = get_dms_client()
    if dms is None:
        print('get_table_stats: Failed to get dms client.')
        return table_stats
    
    try:
        response = dms.describe_table_statistics(ReplicationTaskArn=replication_task_arn)
        print("[DEBUG] get_table_stats: response from describe_table_statsitics = %s." % (response))
        
        task_arn = response['ReplicationTaskArn']
        if task_arn == replication_task_arn:
            table_stats = response['TableStatistics']
            print("[DEBUG] get_table_stats: task_stats = %s." % (table_stats))

    except ClientError as e:
        logging.error("get_table_stats: unexpected error: ")
        logging.exception(e)
        return table_stats

    return table_stats

