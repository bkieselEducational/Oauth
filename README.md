# Oauth Walkthrough

# NOTE: This code is meant as an introductory reference ONLY!! (It's a simple demo. Follow the instructions at the bottom of this README to incorporate a Google Oauth flow into your project.)

# OAuth2 Authorization Code Flow with PKCE using Google OAuth

## Overview:

1. **Google Cloud Console:**
   * Create an account.
   * Create a Project.
   <img width="800" alt="oauth_landing" src="https://github.com/bkieselEducational/Oauth/assets/131717897/267da4eb-d2cc-4c0a-8d57-54b5d02defc0">

   * Register your app.
       1. Click on APIs & Services ->
       2. Click on OAuth consent screen ->
          * For User Type select “External” and click Create.
          * On the following screen, enter your App name, User support email (probably the same as your GCP email. Under Development contact information enter your email again)
      <img width="800" alt="consent" src="https://github.com/bkieselEducational/Oauth/assets/131717897/44e51676-cf0d-46bf-bdd9-9e5f40c4ea6d"><br>  
          * Under the settings for Oauth consent screen, Add a Test User. Click the button “+ ADD USERS” and then enter the email that you are using for your GCP account. <img width="800" alt="oauth_consent" src="https://github.com/bkieselEducational/Oauth/assets/131717897/8c5a9bba-dedb-4d50-b8f0-ab41a5ca16d6"><br>  
       3. On the Credentials tab click the button “+CREATE CREDENTIALS” which will open a drop-down menu. Select “OAuth client ID” ->
          <img width="800" alt="to_credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/79e0da02-46bb-429d-8ff7-4bd13e238f0f">
          <img width="447" alt="credentials_dropdown" src="https://github.com/bkieselEducational/Oauth/assets/131717897/3c87c985-1266-4244-bcaa-979764c65ea1"><br>  
          * Enter the application type “Web application” and a name for your app. Additionally set the Redirect URI at the bottom of the page to your endpoint that will receive the code for exchange. In our case: http://localhost:5000/callback.
          * (Special Note) If you are initiating your OAuth flow from the frontend, you will need to alos set the "Authorized JavaScript origins"

          &nbsp;&nbsp;<img width="800" alt="client_credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/87d7e1ea-9686-48ba-8b58-06ec6f735f0f"><br>  
          * After clicking create, save the client_id and the client_secret in a secure place (.env).
          <img width="509" alt="credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/2903d402-e50b-4bd6-a258-c43efde2c153">

2. **Your App:**
   * Create a link in your frontend that will send a request to your backend, where you will then generate the random values and hashes that you will need to send in the URL to direct the user’s browser to the Google Login page. An example of what your backend will generate: (https://accounts.google.com/o/oauth/v2/auth?redirect_uri=...&scope=...&response_type=code&state=...&code_challenge_method=S256&code_challenge=...&client_id=...&nonce=...access_type=offline&service=lso&o2v=2&flowName=GeneralOauthFlow).
   * Any values that you will be using to validate the response(s) should be saved for comparison later (state, nonce). If using an SDK, this should be handled for you. NOTE on the ‘state’ variable. Traditionally, this value was sent from the frontend in the URL, to be used as the final REDIRECT URL that brings the user back to the desired page in the app once authorization is complete. We can accomplish the same thing by grabbing the ‘Referer’ header out of the request on the backend and saving THAT as the final address to return the user to after the flow. If using the Referer header for this purpose, the state variable can be ANYTHING! Otherwise, it should be a URL on the frontend. In our case, we are just returning a raw HTML string after authorization, so we don’t really need the URL.
   * During the Oauth flow, the user will login at this point and Google will then send a redirect to your ‘redirect_uri’.
   * Inside of the endpoint you’ve created for the Redirect_URI, first check to see that it is a valid request by matching the value of the ‘state’ variable sent in the request against what you generated and stored for the flow. If things look good, we must generate a new url (https://oauth2.googleapis.com/token?client_id=...&client_secret=...&code=...&redirect_uri=needs to match what you've been using&grant_type=authorization_code&code_verifier=...) beginning with the google Oauth token endpoint (https://oauth2.googleapis.com/token) with the values: 
      1. code: the value you just received from the Oauth server.
      2. client_id: Your id that Google generated for you.
      3. client_secret: The secret that Google generated for you.
      4. redirect_uri: Should be the same value we’ve been using.
      5. grant_type: Should be set to ‘authorization_code’
      6. code_verifier: The base64URL encoded value that we saved after generating it as the “seed” for our code_challenge hash!
   * In the event that Google is able to verify the code_challenge (that we sent in initial request) by using the code_verifier AND the code that we are sending to the token endpoint IS valid, Google will send a response that contains our Authorization Token (and an ID Token, if requested).
   * If you DID NOT request an ID Token, you can simply Login the user, and redirect them back to your app and use the Authorization Token to handle the session! (This user will NOT have an account created but can have access to certain features of your site. If you want to the user to have an account, and you probably should, then you’ll need to perform this as an additional step.) If you DID request an ID Token (which is in JWT format), you will need to perform some additional steps to validate it (SDK should handle this):
      a. First you’ll need to validate the signature of the JWT by getting the keys from Google. Send a GET request to this Google endpoint to retrieve the keys: https://www.googleapis.com/oauth2/v3/certs
      b. Note that once you have the keys, you’ll need to use the correct one to verify the JWT. There are usually 2. You can identify the correct one by matching it’s “kid” to the “kid” sent in the claims of the JWT. Use a package to validate the signature!
      c. After validating the signature, we must still check a few more values. First we’ll verify the “iss” (Issuer) value in the claims to see that it in fact matches “https://accounts.google.com”
      d. Next we will verify that the “aud” (Audience) value in the claim matches our client_id
      e. Then we will get the current Epoch time and verify that it falls between the bounds listed in the claims as “iat” (Issued At Time) and the “exp” (Expiration)
      f. Lastly, we will verify that the “nonce” value that Google has sent back in our claims matches the one that we originally sent to initialize the flow.
   * Now that the Oauth process is complete, you must check to see if such a user exists in your db. If not, you’ll Sign Up that new user and Log them in, else just Log them in! NOTE: One of the nice Features of Oauth clients is that you DO NOT need to save a password for them in your db!! As I don’t allow NULL passwords, I just give such users the string “Oauth” as a password. This satisfies the condition that users must have a password, while ensuring that such users will not be affected by a data breach. The string “Oauth” will NOT hash to the string “Oauth”, so it CANNOT be used to login! Feel free to allow NULLABLE passwords in your app if that makes more sense to you.

## Gotchas:
1. Managing a website that uses more than one authentication method, in itself, can be tricky and complex. Don’t muddle the matter further by using different authorization schemes! What I mean by this is, if you allow regular users to login using an email password combination and then manage that session using a SESSION COOKIE, it would be advisable to ALSO set the Oauth access token in a SESSION COOKIE to handle those sessions. If you attempt to handle regular logins using a SESSION COOKIE and then setup validations for Oauth users using a different method, such as using the ‘Authorization: Bearer <Your Token Here>’ Header or a custom header of your design, you will end up with a VERY complicated session management setup on your backend and frontend alike. If this appeals to you, there isn’t any reason why you can’t do it, but it will require a lot of juggling, so BEWARE!!
2. When refreshing a token, make sure to check and see if the response from the server contains a NEW refresh token! If so, make sure to save the new one with the user’s session!
3. When testing ANY Oauth functionality locally make sure to use ‘http://localhost:PORT_NUMBER’ and NOT ‘http://127.0.0.1:PORT_NUMBER’ when typing the URL into your browser. If you don’t use ‘localhost’ it will break the Oauth functionality. Regretfully, I don’t know all of the science behind this issue , but it DOES have something to do with DNS. When you use the alias ‘localhost’, the browser will have to do a DNS resolution. With 127.0.0.1 it does not!! And it causes a problem to NOT do it. So do it!

## Resources:
1. Google Oauth Authorization Code Flow (with PKCE) Diagram
   ![Oauth Flow - Backend](https://github.com/bkieselEducational/Oauth/assets/131717897/7346727c-59c3-4545-9638-f743db37d4d2)
2. Terms
  * PKCE: Proof Key for Code Exchange.
  * Front-Channel: The Browser’s URL bar. An insecure method of sending requests.
  * Back-Channel: The secure way to send requests (as they never touch the Browser). A Javascript example would be to send a request using the fetch() method! (to be truly secure, we need HTTPS)
  * Nonce: Short for “Number used ONCE”. Commonly associated with cryptography, a nonce value is typically a random or semi-random number generated for one time use.
  * SDK: Software Development Kit. A set of software tools and programs provided by hardware and software vendors that developers can use to build applications for specific platforms. SDKs help developers easily integrate their apps with a vendor’s services.
3. Python Oauth SDK README.md link: https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md
4. Base64 URL Encode/Decode in Javascript: https://thewoods.blog/base64url/
5. Base64 URL Encode Python: https://www.base64encoder.io/python/
6. Sha256 Hashing in Python: https://docs.python.org/3/library/hashlib.html

## Additional Notes:
1. An interesting thing to consider about Oauth is that it is provided by an established organization. A name that people trust and are familiar with. It’s possible that you are working for a small startup and users may feel a little trepidation about pouring their personal information into your new app. Seeing that they are being authenticated by Google, Apple, Facebook, etc. may instill confidence in new users to an app!
2. To add on to the note above, another nice benefit is that you can potentially only use ONE account to access all of your apps, instead of generating new credentials for each app you use, which is tedious and clunky!
3. Note that if you REALLY want to explore the Oauth flow by writing your logic from scratch, there are some things you should be aware of. 1) If you want to use an established Oauth endpoint for your local testing, you will HAVE TO use Google!! Other vendors require you to register your application by providing a registered domain name amongst other requirements. The OTHER option, which I have not dabbled in, as of yet, would be to read through the official Oauth2 documents for creating your OWN Oauth API for YOUR app and test THAT out! If this second option interests you, my hat is off to you!!
4. When using the recommended PKCE in an Oauth flow, this will require the generation of 2 random values and the setting of additional parameters in your requests.
5. Keep in mind, that during your time at App Academy, we did not go in depth into security best practices. An obvious omission would be a lack of validating a user’s email. As you continue to develop as a web dev and continue to build your own projects, these practices are something you’ll want to explore further and implement yourself. To that end, note that Oauth validation ALSO takes care of validating the user’s email address!

## Using OAuth in Production:
1. To use OAuth in production, you'll need to add your production URL + callback endpoint path to your Google Credentials under the Redirect_URIs table. Ex: 'https://my_awesome_capstone.onrender.com/api/auth/oauth_callback'.
2. Additionally, you'll want to refactor all of the concerned URLs in your code to use an ENV VARIABLE to resolve the BASE_URL instead of hardcoding these values.

## Incorporating Google Oauth into your Flask Application
### After creating a project in the Google Cloud Platform Console and generating your credentials, follow these remaining steps:
1. Replace your current 'requirements.txt' with the one provided in the repo. File name: new_requirements.txt OR simply copy and paste the additional packages listed at the bottom of that file into your current requirements.txt
2. Choose a file that you will put the necessary Ouath endpoints into. If you are going to use your 'auth_routes.py', this is a completely acceptable decision! Either way, you must ensure that you have the required imports at the top of that file. These imports:
```
import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from tempfile import NamedTemporaryFile
import json
```
3. Now we must configure our 'flow' object to initialize the Oauth flow:
```
# Note: As the flow object requires a file path to load the configuration from AND
	we want to keep our credentials safe (out of our github repo!!).
	We will create a temporary file to hold our values as json.
	Some of these values will come from our .env file.
	
# Import our credentials from the .env file
CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')

client_secrets = {
  "web": {
    "client_id": CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": CLIENT_SECRET,
    "redirect_uris": [
      "http://localhost:5000/callback"
    ]
  }
}

# Here we are generating a temporary file as the google oauth package requires a file for configuration!
secrets = NamedTemporaryFile()
# Note that the property '.name' is the file PATH to our temporary file!
# The command below will write our dictionary to the temp file AS json!
with open(secrets.name, "w") as output:
    json.dump(client_secrets, output)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

flow = Flow.from_client_secrets_file(
    client_secrets_file=secrets.name,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)

secrets.close() # This method call deletes our temporary file from the /tmp folder! We no longer need it as our flow object has been configured!
```



