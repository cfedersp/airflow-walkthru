import json
import boto3
from botocore.exceptions import ClientError

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

import argparse

parser = argparse.ArgumentParser(prog='query-google-analytics-data');
parser.add_argument('profileName');
args = parser.parse_args();


def loadFile(filePath):
	with open(filePath, 'r') as fileContents:
            return fileContents

def get_aws_secrets(profile_name, region, secret_names=[]):

    # secret_name = "epsilon/demos/google/auth/sa/credentials" # "geekDotDev/google/propertyId"
    # region_name = "us-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session(profile_name="AdministratorAccess-339713066603")
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    secretValues = []
    try:
        for current_secret_name in secret_names:
            get_secret_value_response = client.get_secret_value(SecretId=current_secret_name)
            secretValues.append(get_secret_value_response['SecretString'])
        return secretValues
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    

def sample_run_report():
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    
    # credentialFile = "/Users/cfederspiel/Downloads/cs-poc-hrelbwtnrlslbichktzsoyr-0829f93bedf9.json"
    # credContents=loadFile(credentialFile);
    # jsonCredentials = json.load(credContents)
    (property_id, credContents) = get_aws_secrets(args.profileName, "us-west-1", ["geekDotDev/google/propertyId", "epsilon/demos/google/auth/sa/credentials"])
    print(property_id);
    jsonCredentials = json.loads(credContents)
    loadedCredentials=service_account.Credentials.from_service_account_info(jsonCredentials) # , scopes=['https://www.googleapis.com/auth/cloud-platform'])
    client = BetaAnalyticsDataClient(credentials=loadedCredentials)

    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    )
    response = client.run_report(request)

    print("Report result:")
    for row in response.rows:
        print(row.dimension_values[0].value, row.metric_values[0].value)

sample_run_report(); # 501382223 "Geek.dev")
