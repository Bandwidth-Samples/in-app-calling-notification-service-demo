const express = require("express")
const { handle } = require('./initiate');

var port = process.env.LOCAL_PORT || 3000;

var app = express()
app.use(express.json())

app.get("/health", function (request, response) {
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

app.listen(port, function () {
    console.log("Started application on port %d", port)
});
