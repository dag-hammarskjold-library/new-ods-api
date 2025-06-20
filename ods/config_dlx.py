import os
from dlx.marc import Bib, Auth
import boto3

class Config(object):
    DEBUG = False
    TESTING = False

    bucket = 'undl-files'
    
    if 'DLX_REST_TESTING' in os.environ:
        environment = 'test'
        connect_string = 'mongomock://localhost'
        TESTING = True
        LOGIN_DISABLED = True
        dbname = 'dlx'
        ssl = False
        sync_log_collection = 'sync_log'
    elif 'DLX_REST_LOCAL' in os.environ:
        environment = 'dev/local'
        connect_string = "mongodb://localhost:27017/?authSource=undlFiles"
        dbname = 'undlFiles'
        ssl = False
        sync_log_collection = 'sync_log'
        bucket = 'dev-undl-files'
    elif 'DLX_REST_DEV' in os.environ:
        environment = 'dev'
        client = boto3.client('ssm')
        secret_key = client.get_parameter(Name='metadata_cache_key')['Parameter']['Value']
        connect_string = client.get_parameter(Name='devISSU-admin-connect-string')['Parameter']['Value']
        dbname = 'dev_undlFiles'
        ssl = True
        sync_log_collection = 'sync_log'
        bucket = 'dev-undl-files'
    elif 'DLX_REST_QAT' in os.environ:
        environment = 'qat'
        client = boto3.client('ssm')
        secret_key = client.get_parameter(Name='metadata_cache_key')['Parameter']['Value']
        # Use these value when we're ready to migrate QAT to Atlas.
        connect_string = client.get_parameter(Name='uatISSU-admin-connect-string')['Parameter']['Value']
        dbname = 'undlFiles'
        ssl = True
        #connect_string = client.get_parameter(Name='qat-dlx-connect-string')['Parameter']['Value']
        #dbname = 'qat_undlFiles'
        sync_log_collection = 'sync_log'
        bucket = 'dev-undl-files'
    elif 'DLX_REST_UAT' in os.environ:
        environment = 'uat'
        client = boto3.client('ssm')
        secret_key = client.get_parameter(Name='metadata_cache_key')['Parameter']['Value']
        # Use these value when we're ready to migrate UAT to Atlas.
        connect_string = client.get_parameter(Name='uatISSU-admin-connect-string')['Parameter']['Value']
        dbname = 'undlFiles'
        ssl = True
        #connect_string = client.get_parameter(Name='uat-dlx-connect-string')['Parameter']['Value']
        #dbname = 'uat_undlFiles'
        sync_log_collection = 'sync_log'
        bucket = 'dev-undl-files'
    elif 'DLX_REST_PRODUCTION' in os.environ:
        environment = 'prod'
        client = boto3.client('ssm')
        secret_key = client.get_parameter(Name='metadata_cache_key')['Parameter']['Value']
        #connect_string = client.get_parameter(Name='dlx-prod-connect-string')['Parameter']['Value']
        # Use the following value when we're ready to migrate production to Atlas.
        connect_string = client.get_parameter(Name='prodISSU-admin-connect-string')['Parameter']['Value']
        dbname = 'undlFiles'
        ssl = False
        sync_log_collection = 'dlx_dl_log'
    else:
        raise Exception('One of the environment variables "DLX_REST_TESTING", "DLX_REST_DEV", "DLX_REST_QAT", "DLX_REST_UAT", or "DLX_REST_PRODUCTION" must return a true value in order to initialize the runtime environment')

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.urandom(24))
    BIB_COLLECTION = 'bibs'
    AUTH_COLLECTION = 'auths'
    FILE_COLLECTION = 'files'
    MAX_QUERY_TIME = 20000
    
    # force access to the production database
    # connect_string = client.get_parameter(Name='prodISSU-admin-connect-string')['Parameter']['Value']
    
    if "@" in connect_string:
        print(f'Loading {environment}: {connect_string.split("@")[-1].split("/")[0]}')
    else:
        print(f'Loading {environment}')