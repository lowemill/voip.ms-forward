import os
import requests

sess = requests.Session()

VOIPMS_API_URL = "https://voip.ms/api/v1/rest.php"


class VoIPMSAPI():
    def __init__(self, api_username: str, api_password: str, api_url: str = VOIPMS_API_URL):
        self.api_username = api_username
        self.api_password = api_password
        self.api_url = api_url

        self.sess = requests.Session()

    def call(self, method, **kwargs):
        fields = {
            "api_username": self.api_username,
            "api_password": self.api_password,
            "method": method,
        }

        fields.update(kwargs)

        return self.sess.get(self.api_url, params=fields).json()
