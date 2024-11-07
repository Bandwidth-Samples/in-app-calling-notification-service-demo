/**Helper for firebase initiation and operations */
const firebase = require('firebase-admin');
const serviceAccount = require('./admin-service.json');
firebase.initializeApp({ credential: firebase.credential.cert(serviceAccount) });
export { firebase };