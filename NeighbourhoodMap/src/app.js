var express = require("express");
var request = require("request-promise-native");
var http = require("http");

var app = express();

var server = http.createServer(app);

var getYelpAPI = function(req,res) {
    var rq = request({
        uri: "https://api.yelp.com/v3/businesses/search",
        qs: req.query,
        dataType: "json",
        auth: {
            "bearer": "NMurae0tVFW6NvhG7PzrMT3VQc5DHkOUgYux-uNUPVsNwrYc6dC5Jzf9HbX98B0hOsWSLNlwo_db5FqwrCEnAZSE9dzT9rXIA_sFSTj0dG7GkPMKaHGxlKosvnFmWXYx"
        }
    });
    rq.then(function(response) {
        if(typeof(response)==="string"){
            res.status(200);
            res.json(JSON.parse(response));
        }
        else{
            res.status(200);
            res.json(response);
        }
    }, function(){
        res.status(400).send({message: "Yelp request failed"});
    });
};
app.get("/getYelpAPI", getYelpAPI);
app.use(express.static(__dirname));

server.listen(8080);
