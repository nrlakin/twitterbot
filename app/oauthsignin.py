from flask import current_app, jsonify, session
from flask import url_for
from app import app, oauth, github, twitter


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def authorized_response(self):
        pass

    def get_oauth_token(self):
        pass

    def get_username(self):
        pass

    def get_user_info(self):
        pass

    def store_token(self, resp):
        pass

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GithubSignIn(OAuthSignIn):

    def __init__(self):
        super(GithubSignIn, self).__init__('github')
        self.screen_name=''

    def authorize(self):
        return github.authorize(url_for('oauth_callback', provider=self.provider_name, _external=True), _external=True)

    def authorized_response(self):
        return github.authorized_response()

    def get_user_info(self):
        return github.get('user').data

    def get_username(self):
        if self.screen_name=='':
            resp=self.get_user_info()
            self.screen_name=resp['login']
        return self.screen_name

    def store_token(self, auth_resp):
        session['oauth_token'] = (auth_resp['access_token'], '')

    @github.tokengetter
    def get_oauth_token():
        return session.get('oauth_token')

class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.screen_name=''

    def authorize(self):
        return twitter.authorize(url_for('oauth_callback', provider=self.provider_name, _external=True), _external=True)

    def authorized_response(self):
        return twitter.authorized_response()

    def get_username(self):
        if self.screen_name=='':
            resp=self.get_user_info()
            self.screen_name=resp['screen_name']
        return self.screen_name

    def get_user_info(self):
        """
        Cludgy and unnecessary, unless getting other info.
        """
        return twitter.get('users/lookup.json', data={'screen_name':self.screen_name}).data

    def store_token(self, auth_resp):
        session['oauth_token'] = (auth_resp['oauth_token'], auth_resp['oauth_token_secret'])
        self.screen_name=auth_resp['screen_name']

    @twitter.tokengetter
    def get_oauth_token():
        return session.get('oauth_token')
