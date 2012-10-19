/* portlan
 * Jonathan M Stout
 */

var http = require('http')
var url = require('url')
var server = require('./server').pageIndex

var dbUrl = "127.0.0.1/overlord"
var collections = ["hosts"]
var db = require("mongojs").connect(dbUrl, collections)

http.createServer( function (req, res) {
    pathname = url.parse(req.url).pathname
    console.log('Serving: ', pathname)

    if (pathname in server) {
	server[pathname](req, res, db)
    } else {
	server['/fourZeroFour.html'](req, res, db)
    }
}).listen(8888)
