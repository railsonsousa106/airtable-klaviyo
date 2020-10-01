from airtable import Airtable
from klaviyo import Klaviyo
import json
import os

def get_email_and_phone_number_from_airtable(app_id, secret_key, record_id):
    try:
        print('##### Getting email and phone number from airtable started #####')
        # initialize airtable tables
        tbl_uploads = Airtable(app_id, 'Uploads', secret_key)

        upload = tbl_uploads.get(record_id)
        
        if 'Customer Email ID' in upload['fields']:
            email = upload['fields']['Customer Email ID']
        else:
            print('Customer doesn\'t have email.')
            raise ValueError('Customer doesn\'t have email.')
        
        if 'Phone Number' in upload['fields']:
            phone_number = upload['fields']['Phone Number']
        else:
            phone_number = None
        
        print('##### Getting email and phone number from airtable finished #####')
        print('email:', email, 'phone_number:', phone_number)
        return email, phone_number
    except Exception as e:
        print('Error getting customer information from Airtable: ' + str(e))
        raise ValueError('Error getting customer information from Airtable: ' + str(e))

def subscribe_to_klaviyo_list(public_token, private_token, list_id, email, phone_number):
    try:
        print('##### Subscribing to Klaviyo List started #####')
        client = Klaviyo(public_token=public_token, private_token=private_token)
        
        profile = {
            'email': email,
            'sms_consent': True,
        }
        if phone_number:
            profile['phone_number'] = phone_number
        
        client.Lists.add_members_to_list(list_id, [profile])
        client.Lists.add_subscribers_to_list(list_id, [profile])
        print('##### Subscribing to Klaviyo List finished #####')
    except Exception as e:
        print('Error subscribing to the Klaviyo List: ' + str(e))
        raise ValueError('Error subscribing to the Klaviyo List: ' + str(e))


def single_customer(event, context):
    print("Request Body: ")
    print(event["body"])
    
    try:
        body = json.loads(event["body"])
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Error occured",
                "message": str(e)
            })
        }

    try:
        email, phone_number = get_email_and_phone_number_from_airtable(os.getenv('AIRTABLE_APP_ID'), os.getenv('AIRTABLE_SECRET_KEY'), body['recordId'])
        subscribe_to_klaviyo_list(os.getenv('KLAVIYO_PUBLIC_TOKEN'), os.getenv('KLAVIYO_PRIVATE_TOKEN'), os.getenv('KLAVIYO_LIST'), email, phone_number)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "New Airtable customer is subscribed to Klaviyo list.",
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Error occured",
                "message": str(e)
            })
        }
