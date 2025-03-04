## Webhook service for inbound calls

This project is a Node.js webhook that manages communication between the Bandwidth API and the client (Android/iOS/React) to facilitate inbound calls

### Installation

To use this webhook service, you need to host it on a global access point. Follow the steps below to set it up:

##### **Clone the repository:**
    git clone https://github.com/Bandwidth-Samples/in-app-calling-inbound-demo.git
    cd in-app-calling-inbound-demo
##### **Install dependencies:**
    npm install
##### **Deploy the service:** Ensure that your deployment environment allows global access. You can use platforms like Heroku, AWS, or any other cloud service provider.
    npm start

##### **Usage**: Once above steps completd you are able to use the webhook in programmable voice callback url
    https://serverurl.com/initiate
    