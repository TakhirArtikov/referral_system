import requests

from config import settings


class HunterClient:
    def __init__(self):
        self.api_key = settings.HUNTER_API_KEY
        self.base_url = settings.HUNTER_API_URL

    def verify_email(self, email: str) -> bool:
        params = {
            'api_key': self.api_key,
            'email': email
        }
        r = requests.get(f'{self.base_url}/email-verifier/', params=params).json()
        print('RESPONSE', r)
        data = r['data']
        return data['status'] == 'valid'


hunter_client = HunterClient()
