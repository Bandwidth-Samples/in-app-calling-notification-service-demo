const bodyparser = require('body-parser');
const { handle } = require('./lambda');
const express = require("express")
var app = express()
app.use(bodyparser.json())

app.get("/", function (request, response) {
    response.send("Hello World!")
})


app.post('/initiate', async (req, res) => {
    if (req != undefined) {
        var response = await handle(req);
        if (response['statusCode'] == 200) {
            res.send(response);
        } else {
            res.status(404);
        }
    } else {
        res.status(400).send({ "message": "Bad request" });
    }
})

app.listen(10000, function () {
    console.log("Started application on port %d", 10000)
});