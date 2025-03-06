const bodyparser = require('body-parser');
const firebase = require('firebase-admin');
const serviceAccount = require('./admin-service.json');
const axios = require('axios');
const bxml = require('bandwidth-sdk');
firebase.initializeApp({ credential: firebase.credential.cert(serviceAccount) });

/**Handler for lamda functions */
exports.handle = async (event, context, callback) => {
    console.log(JSON.stringify(event.body));
    if (typeof event.body === 'string') {
        console.log("Body is string:", event.body);
        var body = JSON.parse(event.body);
    } else {
        var body = event.body;
    }
    try {
        var response = await initiate(body);
        console.log(response);
        return response;
    } catch (error) {
        console.error(error);
    }
}

/**if unique combination of from and to number avaiable for an user id
 * this means call has already been initiated we need to bridge the calls
 * else
 * create the unique combination of from and to number and assign to `to` user id
 * send notification to `to` user's FCM token
 */
async function initiate(body) {
    const db = firebase.firestore();
    const agentsRef = db.collection("agents");

    const preCallAgents = await agentsRef.where('in-app-call-id', '==', `${body.from}-${body.to}`).get();
    if (preCallAgents.size > 0) {
        var fromCallUser = preCallAgents.docs[0].data();
        var pvCallId = fromCallUser['pv-call-id'];
        await db.collection("agents")
            .doc(preCallAgents.docs[0].id)
            .set({
                'in-app-call-id': null,
                'pv-call-id': null
            },
                { merge: true });
        return speakSentenceXMLBridge(pvCallId);
    } else {
        const userTo = await db.collection("agents").doc(body.to).get();
        const toUserToken = userTo.data().token;

        if (toUserToken != undefined) {
            const sampleData = {
                "accountId": body.accountId,
                "applicationId": body.applicationId,
                "fromNo": body.from,
                "toNo": body.to,
            };

            const message = {
                notification: {
                    title: ("Call from: " + sampleData['fromNo']),
                    body: ("You are getting a call from: " + sampleData['fromNo'] + " please go back to the tab and answer it")
                },
                data: sampleData,
                tokens: [toUserToken],
            }

            firebase.messaging().sendEachForMulticast(message)
                .then(response => {
                    console.log("FCM Sent: ", JSON.stringify(response));
                })
                .catch(error => {
                    console.error("FCM Failed: ", error);
                });

            var docRef = db.collection("agents").doc(body.to);
            await docRef.set(
                {
                    "callInBackground": sampleData,
                },
                { merge: true });
            var docRef1 = db.collection("agents").doc(body.from);
            await docRef1.set(
                {
                    "pv-call-id": body.callId,
                    "in-app-call-id": `${body.to}-${body.from}`
                },
                { merge: true });
        }
        return speakSentenceXML();
    }
}

/**Response BXML for briding the call */
function speakSentenceXMLBridge(secondCallId) {
    //return `<?xml version="1.0" encoding="UTF-8"?><Response><Pause duration='5'/><SpeakSentence>Agent connected successfully</SpeakSentence><Bridge>${secondCallId}</Bridge></Response>`;
    const response = new bxml.Bxml.Response();
    response.addVerbs(new bxml.Bxml.Pause(5));
    response.addVerbs(new bxml.Bxml.SpeakSentence('Agent connected successfully'));
    response.addVerbs(new bxml.Bxml.Bridge(secondCallId));
    return response.toBxml();
}

/**Response BXML for iniating the call  */
function speakSentenceXML() {
    //return `<?xml version="1.0" encoding="UTF-8"?><Response><SpeakSentence>Please wait while we are connecting your call</SpeakSentence><Pause duration="60"/></Response>`;
    const response = new bxml.Bxml.Response();
    response.addVerbs(new bxml.Bxml.SpeakSentence(`Please wait while we are connecting your call`));
    response.addVerbs(new bxml.Bxml.Pause(60));
    return response.toBxml();
}