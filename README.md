# In App Calling Notification Service Demo

<a href="http://dev.bandwidth.com">
  <img src="icon-in-app.svg" title="Product Quick Start Guide" alt="Product Quick Start Guide"/> <!--src should be image located in repo-->
</a>

# Table of Contents

* [Description](#description)
* [Pre-Requisites](#pre-requisites)
* [Environmental Variables](#environmental-variables)
* [Callback URLs](#callback-urls)
* [Firebase Configuration](#firebase-configuration)
* [Running the Application](#running-the-application)
    * [Ngrok](#ngrok)

# Description

This project is a Node.js application that manages notifications between the Bandwidth API and a client (Android/iOS/React) to facilitate notifications of incoming inbound calls.

# Pre Requisites

In order to use the Bandwidth API, users need to set up the appropriate application at the [Bandwidth Dashboard](https://dashboard.bandwidth.com/) and create an API user.

To create an application, log into the [Bandwidth Dashboard](https://dashboard.bandwidth.com/) and navigate to the `Applications` tab.  Fill out the **New Application** form; selecting the service (Voice) that the application will be used for.  All Bandwidth services require publicly accessible Callback URLs, for more information on how to set one up see [Callback URLs](#callback-urls).

For more information about API credentials see our [Account Credentials](https://dev.bandwidth.com/docs/credentials) page.

# Environmental Variables

The sample app uses the below environmental variables.

```sh
LOCAL_PORT    # The port number you wish to run the sample on
```

# Callback URLs

For a detailed introduction, check out our [Bandwidth Voice Callbacks](https://dev.bandwidth.com/docs/voice/webhooks) page.

Below are the callback paths:
* `/health`
* `/initiate`

# Firebase Configuration

This sample application utilizes firebase to assist in sending notifications to the client. 
* Follow the [Firebase Setup Guide](https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments) to instantiate the `admin-service.json` file imported at [initiate.js:line:8](https://github.com/Bandwidth-Samples/in-app-calling-notification-service-demo/blob/02cc4ac4c895e4f256c293004bc8344e195f3d3b/initiate.js#L8)
* Create a new web project and follow the straightforward instructions provided in the link [here](https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments).

# Running the Application

To install the required packages for this application, run the following command:

```bash
npm install
``` 

To run the application, run the following command:

```bash
npm start
```

To use this webhook service, make it publicly accessible. There are many ways to accomplish this - but for simplicity and ease of use we recommend [ngrok](https://ngrok.com/) to get started. 

## Ngrok

A simple way to set up a local callback URL for testing is to use the free tool [ngrok](https://ngrok.com/).  
After you have downloaded and installed `ngrok` run the following command to open a public tunnel to your port (`$LOCAL_PORT`)

```sh
ngrok http $LOCAL_PORT
```

You can view your public URL at `http://127.0.0.1:4040` after ngrok is running.  You can also view the status of the tunnel and requests/responses here. Once your public ngrok url has been created, you can set it in the voice application created in the [Pre-Requisites](#pre-requisites) section.
