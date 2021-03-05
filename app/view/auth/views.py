from flask import redirect, render_template, url_for, request, session
from app import log, app
from . import auth
import json
from authlib.flask.client import OAuth

oauth = OAuth(app)
smartschool = oauth.register('smartschool')


@auth.route('/', methods=['GET', 'POST'])
def login():
    if 'app_uri' in request.args:
        session['app_uri'] = request.args['app_uri']
        # Step 1 : go to smartschool so that the user can log in with smartschool credentials
        redirect_uri = app.config['REDIRECT_URI']
        return oauth.smartschool.authorize_redirect(redirect_uri)

    if 'code' in request.args:  # received a request with a OAUTH code
        # Step 2 : with the code from smartschool, fetch the access_token from smartschool
        token = oauth.smartschool.authorize_access_token()
        return redirect(url_for('auth.smartschool_profile', token=json.dumps(token)))

# OAUTH specific
@auth.route('/smartschool_profile/<string:token>', methods=['GET', 'POST'])
def smartschool_profile(token):
    # Step 3 : with the access_code, get the userinfo from SS
    resp = oauth.smartschool.get('fulluserinfo', token=json.loads(token))
    profile = resp.json()

    if 'app_uri' in session:
        app_uri = session['app_uri']
        profile = json.dumps(profile)
        version = app.config['version']
        uri = f'{app_uri}?profile={profile}&version={version}'
        log.info(f'retrieved profile for {uri}')
        return redirect(uri)

    log.error('no app_uri found in session')

