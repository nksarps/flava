from pydantic import EmailStr

from decouple import config as env
from trycourier import Courier

client = Courier(auth_token=env('COURIER_API_KEY'))

def send_verification_email(email: EmailStr, username:str, token:str):
    verification_link = f"{env('VERIFICATION_LINK')}?token={token}"

    client.send_message(
        message={
            "to": {
            "email": email,
            },
            "template": env('VERIFICATION_MAIL_TEMPLATE_ID'),
            "data": {
            "appName": "Flava",
            "firstName": username,
            "link": verification_link,
            },
        }
    )

def send_password_reset_email(email: EmailStr, username:str, token:str):
    password_reset_link = f"{env('PASSWORD_RESET_LINK')}?token={token}"

    client.send_message(
        message={
            "to": {
            "email": email,
            },
            "template": env('PASSWORD_RESET_MAIL_TEMPLATE_ID'),
            "data": {
            "appName": "Flava",
            "firstName": username,
            "link": password_reset_link,
            },
        }
    )