import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from decouple import config

# Sandbox base URL. For production, swap to https://api.safaricom.co.ke
BASE_URL = "https://sandbox.safaricom.co.ke"


def get_access_token():
    """Authenticate with Daraja and return a short-lived access token."""
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(
            config("MPESA_CONSUMER_KEY"),
            config("MPESA_CONSUMER_SECRET"),
        ),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def initiate_stk_push(phone_number, amount, account_reference="Payment"):
    """Send an STK Push prompt to the customer's phone."""
    access_token = get_access_token()
    shortcode = config("MPESA_SHORTCODE")
    passkey = config("MPESA_PASSKEY")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{shortcode}{passkey}{timestamp}".encode()
    ).decode()

    url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),          # whole numbers only, no decimals
        "PartyA": phone_number,         # customer's number, 2547XXXXXXXX
        "PartyB": shortcode,            # your shortcode receiving funds
        "PhoneNumber": phone_number,    # number to receive the prompt
        "CallBackURL": config("MPESA_CALLBACK_URL"),
        "AccountReference": account_reference,
        "TransactionDesc": "Payment via STK Push",
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()