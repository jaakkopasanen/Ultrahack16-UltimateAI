# -*- coding: utf-8 -*-

import requests


class ObpApi:
    def __init__(self, host='https://op.openbankproject.com', version='2.1.0',
                 direct_login_url='/my/logins/direct', oauth_url='/oauth',
                 oauth_callback_url='http://localhost', consumer_key='', consumer_secret=''):
        self.host = host
        self.version = version
        self.base_url = '{host}/obp/v{version}'.format(host=self.host, version=self.version)
        self.direct_login_url = '{host}{url}'.format(host=self.host, url=direct_login_url)
        self.oauth_url = '{host}{url}'.format(host=host, url=oauth_url)
        self.oauth_callback_url = oauth_callback_url

        assert consumer_key, 'No consumer key provided'
        assert consumer_secret, 'No consumer secret provided'
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.auth_method = None
        self._direct_login = ''
        self._oauth = None

    def login_direct(self, username, password):
        """Performs a direct login."""

        # Authorization header
        auth = 'DirectLogin username="{un}",password="{pw}",consumer_key="{ck}"'.format(
            un=username,
            pw=password,
            ck=self.consumer_key
        )
        headers = {'Authorization': auth}

        # Do the login request
        response = requests.get(self.direct_login_url, headers=headers)

        # Handle response
        if response.status_code == 200:
            # Login success
            token = response.json()['token']
            # Save authorization details
            self._direct_login = {'Authorization': 'DirectLogin token={token}'.format(token=token)}
            self.auth_method = 'direct'
            return True

        # Login failed
        return False

    def initiate_oauth(self):
        """Initiates the OAuth authorisation returns an API session object."""

        from requests_oauthlib import OAuth1Session

        request_token_url = '{}/initiate'.format(self.oauth_url)
        authorization_url = '{}/authorize'.format(self.oauth_url)
        access_token_url = '{}/token'.format(self.oauth_url)

        # initiate Oauth by fetching request token
        api = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret,
                            callback_uri=self.oauth_callback_url)
        api.fetch_request_token(request_token_url)

        # ask user to visit authorization URL and paste response
        authorization_url = api.authorization_url(authorization_url)
        print('Please visit this URL and authenticate/authorise:')
        print(authorization_url)
        redirect_response = input('Paste the full redirect URL here: ')

        # parse authorization response (contains callback_uri) and access token
        api.parse_authorization_response(redirect_response)
        api.fetch_access_token(access_token_url)
        self._oauth = api
        self.auth_method = 'oauth'

    def _request(self, url):
        """Creates HTTP request to API endpoint."""

        assert self.auth_method is not None, 'Authentication not done yet.'
        if self.auth_method == 'direct':
            response = requests.get(url, headers=self._direct_login)
            return response
        elif self.auth_method == 'oauth':
            response = self._oauth.get(url)
            return response
        raise ValueError('Invalid auth method: {}'.format(self.auth_method))

    def hello(self, quiet=False):
        """Tests API endpoint."""

        # HTTP GET with direct login authorization
        response = self._request(self.base_url)
        if not quiet:
            print('API response {}'.format(response.status_code))  # Print response
        if response.status_code == 200:
            return True
        else:
            return False
