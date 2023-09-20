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
       3. On the Credentials tab click the button “+CREATE CREDENTIALS” which will open a drop-down menu. Select “OAuth client ID”
      <img width="800" alt="to_credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/79e0da02-46bb-429d-8ff7-4bd13e238f0f">
      <img width="447" alt="credentials_dropdown" src="https://github.com/bkieselEducational/Oauth/assets/131717897/3c87c985-1266-4244-bcaa-979764c65ea1"><br>  
       4. enter the application type “Web application” and a name for your app. Additionally set the Redirect URI at the bottom of the page to your endpoint that will receive the code for exchange. In our case: http://localhost:5000/callback.
          * (Special Note) If you are initiating your OAuth flow from the frontend, you will need to alos set the "Authorized JavaScript origins"

      <img width="800" alt="client_credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/87d7e1ea-9686-48ba-8b58-06ec6f735f0f"><br>  
       5. After clicking create, save the client_id and the client_secret in a secure place (.env), which in this case, is your client_secret.json file.
      <img width="509" alt="credentials" src="https://github.com/bkieselEducational/Oauth/assets/131717897/2903d402-e50b-4bd6-a258-c43efde2c153">

2. **Your App:**
   * Create a link in your frontend that will send a request to your backend, where you will then generate the random values and hashes that you will need to send in the URL to direct the user’s browser to the Google Login page (https://accounts.google.com/o/oauth/v2/auth?redirect_uri=...&scope=...&response_type=code&state=...&code_challenge_method=S256&code_challenge=...&client_id=...&nonce=...access_type=offline&service=lso&o2v=2&flowName=GeneralOauthFlow).
