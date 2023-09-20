# Oauth Walkthrough

# NOTE: This code is meant as an introductory reference ONLY!!

## Here's the Google Doc: https://docs.google.com/document/d/1SN5xTVa2iktNiTLO4-jcX1wCTCvtHu-O5vPdE4NQ_6o/edit

![Oauth Flow - Backend](https://github.com/bkieselEducational/Oauth/assets/131717897/7346727c-59c3-4545-9638-f743db37d4d2)

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

      <img width="800" alt="client_credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/87d7e1ea-9686-48ba-8b58-06ec6f735f0f"><br>  
          * After clicking create, save the client_id and the client_secret in a secure place (.env), which in this case, is your client_secret.json file.
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


