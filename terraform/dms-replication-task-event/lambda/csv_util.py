import boto3
from botocore.exceptions import ClientError
import csv
import logging

import config


def get_s3_client():
    print('get_s3_client: profile_name=%s, region_name=%s' % (config.profile_name, config.region_name))

    p_name = None
    if (config.profile_name != ''):
        p_name = config.profile_name
    session = boto3.Session(profile_name=p_name)
    s3 = session.client('s3', region_name=config.region_name)
    return s3
    
    
def write_csv_file(table_stats, dest_object_name):
    # extract field names from first entry in table stats
    field_names = list(table_stats[0].keys())
    tmp_dest_object_name = '/tmp/'+dest_object_name
    with open(tmp_dest_object_name, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(table_stats)
        csv_file.close()
        
        
def put_csv_file_as_s3_object(dest_bucket_name, dest_object_prefix, dest_object_name):
    s3 = get_s3_client()
    if s3 is None:
        print('put_csv_file_as_s3_object: Failed to get s3 resource.')
        return False
    
    tmp_dest_object_name = '/tmp/'+dest_object_name
    try:
        # upload load PNG file to S3
        dest_object_key = dest_object_prefix + dest_object_name
        response = s3.upload_file(tmp_dest_object_name, dest_bucket_name, dest_object_key)
    except ClientError as e:
        logging.error("put_csv_file_as_s3_object: unexpected error: ")
        logging.exception(e)
        return False
    
    return True
    
    