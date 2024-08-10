from dotenv import load_dotenv
import os

def load_config():
    load_dotenv()
    return {
        'LOGIN_URL': os.getenv('LOGIN_URL'),
        'LOGIN_EMAIL': os.getenv('LOGIN_EMAIL'),
        'LOGIN_PASSWORD': os.getenv('LOGIN_PASSWORD'),
    }
