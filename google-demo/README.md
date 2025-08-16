Google setup:
Create an account in Google Ads and a Project in Google Cloud. 
Link the Ads account to the Google Cloud project. 
I think at this point, you name the Ads DataStream as a "Property" and recieve a numerical "Property Id" we'll use to refer to GA4 metrics from this Ads account.
Under APIs & Services, enable Google Analytics Data
Create a service account in Google Cloud project. Create a key and upload to AWS Secrets Manager.Add the service account email to the Ads account list of accessors.
Google Analytics Data doesn't have any IAM roles, but you can add Analytics Hub Viewer.

python3 -m venv dev
source dev/bin/activate
pip install google-analytics-data
pip install boto3
aws configure sso
aws configure list-profiles
python demo.py aws-sso-profile-name