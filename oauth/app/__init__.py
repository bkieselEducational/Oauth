# Code Attribution: Vincent Stevenson @youtube
# Notes by: Brian Kiesel

import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET') # make sure this matches with what's in client_secret.json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

print("secret: ", client_secrets_file)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

# 1) We hit this endpoint when sending the initial GET request from our frontend by clicking the Login Button.
# Note that while we clicked a 'Login' Button, this is deceptive!! An oauth flow is typically initiated using an <a href="your oauth initiating endpoint"><button/></a> tag.
# The Button is there just to make things look nice. If you look at the actual code from a frontend SDK, it is ALWAYS an <a> tag!!
# We can correlate this endpoint with the FIRST arrow in our flow chart!!
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    print("AUTH URL: ", authorization_url) # I recommend that you print this value out to see what it's generating.
    # Ex: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=NICE TRY&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=A0eZyFD4WH6AfqSj7XcdypQ0cMhwr9&access_type=offline
    # It SHOULD look a lot like the URL in the SECOND or THIRD line of our flow chart!
    # Note that in the auth url above the value 'access_type' is set to 'offline'. If you do not send this, the user will NOT see the Google Login screen!!
    # Additionally, note that this URL does NOT contain the 'code_challenge_method' value NOR the 'code_challenge' that can be seen in our flow chart.
    # This package may have been created BEFORE the official Oauth2 consortium began recommending PKCE even for back channel flows...
    # While implementation details are completely obscured by the method .authorization_url() let's note 2 things here.
    # 1) We ARE generating a random value for the 'state' variable. We save it to the session on the line below to compare later.
    # 2) The authorization URL
    #print("STATE: ", state)
    session["state"] = state
    return redirect(authorization_url) # This line technically will enact the SECOND and THIRD lines of our flow chart.


# After a successful login by our user, Google will send a verification code to the endpoint below.
# Using the verification code, we can request an authorization token from Google as long as we do it before it expires. I think 5 minutes...
# This endpoint is being hit by the 5th line in our flow chart.
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url) # This method is sending the request depicted on line 6 of our flow chart! The response is depicted on line 7 of our flow chart.
    # I find it odd that the author of this code is verifying the 'state' AFTER requesting a token, but to each their own!!

    # This is our CSRF protection for the Oauth Flow!
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    # The method call below will go through the tedious work of verifying the JWT signature sent back with the object from OpenID Connect
    # Although I cannot verify, hopefully it is also testing the values for "sub", "aud", "iat", and "exp" sent back in the CLAIMS section of the JWT
    # Additionally note, that the oauth initializing URL generated in the previous endpoint DID NOT send a random nonce value. (As depicted in our flow chart)
    # If it had, the server would return the nonce in the JWT claims to be used for further verification tests!
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # Now we generate a new session for the newly authenticated user!!
    # Note that depending on the way your app behaves, you may be creating a new user at this point...
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")

    return redirect("/protected_area") # This will send the final redirect to our user's browser. As depicted in Line 8 of the flow chart!


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"

# This is the endpoint that our final redirect is sending the GET request to.
@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
