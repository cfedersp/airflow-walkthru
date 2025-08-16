python3 -m venv dev
source dev/bin/activate
pip install google-analytics-data
pip install boto3
aws configure sso
aws configure list-profiles
python demo.py aws-sso-profile-name