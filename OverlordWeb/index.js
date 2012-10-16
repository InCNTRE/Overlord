/* portlan
 * Jonathan M Stout
 */

var http = require('http')
var url = require('url')
var server = require('./server').pageIndex

var dbUrl = "192.168.1.144/portlan"
var collections = ["devices"]
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
