/* portlan
 * Jonathan M. Stout
 * serve.js
 *
 * Returns result of requested url from index.js
 * It might be good to push these down into more
 * files to keep things more readable.
 */
var url = require('url')
var bind = require('bind')
var ObjectId = require('mongojs').ObjectId

var indexHtml = function(req, res, db) {
    console.log('Starting index.html')
    db.hosts.find({}, {"group_no": true}, function(err, groups) {
	// Populates group select
	bind.toFile("./index.html", {"portlan_groups": groups}, function callback(data) {
	    res.writeHead(200, {"Content-Type": "text/html"})
	    res.write(data)
	    res.end()
	})})
}

var index = function(req, res, db) {
    query = url.parse(req.url, true).query
    if (query.group_no == "all") {
	query = {}
    }
    db.hosts.find(query, function(err, hosts) {
	if (err || !hosts) {
	    console.log("No hosts found for group_no ", group)
	    res.writeHeader(404)
	    res.write("Failure")
	    res.end()
	} else {
	    var result = ""
	    for (var i = 0; i < hosts.length; i++) {
		result += "<p>" + hosts[i].active + " | "
        result += hosts[i]._parent + " | "
		result += hosts[i]._name + " | "
		result += hosts[i].make + " | "
		result += hosts[i].model + " | "
		result += hosts[i].firmware + " | "
		result += hosts[i].group_no + " | "
        result += hosts[i].vlan + " | "
        result += hosts[i].port_no + " | "
        result += hosts[i].ip + " | "
		result += hosts[i].mac + " | "
		result += hosts[i]._type + " | "
		
		result += '<a href="update_device.html?name=' + hosts[i]._name + '">edit</a>' + "</p>"
	    }
	    
	    res.writeHead(200, {"Content-Type": "text/html"})
	    if (result != "") {
		res.write(result)
	    } else {
		res.write("No hosts found.")
	    }
	    res.end()
	}
    })
}

var addDeviceHtml = function(req, res, db) {
    console.log('Starting add_device.html')
    bind.toFile("./add_device.html", {}, function callback(data) {
	res.writeHead(200, {"Content-Type": "text/html"})
	res.write(data)
	res.end()
    })
}

var addDevice = function(req, res, db) {
    query = url.parse(req.url, true).query
    // If manually added, no reason to expect device
    // is added.
    query.active = false

    db.hosts.save(query)
    res.writeHead(302, {"Location": "http://127.0.0.1:8888/"})
    res.end()
}

var updateDeviceHtml = function(req, res, db) {
    query = url.parse(req.url, true).query

    db.hosts.findOne(query, function(err, device) {
	if (err || !device) {
	    console.log("No hosts found.")
	    console.log(err)
	    res.writeHeader(200)
	    res.write("Failure")
	    res.end()
	} else {
	    device._id = device._id.toString()
	    bind.toFile("./update_device.html", device, function callback(data) {
		res.writeHead(200, {"Content-Type": "text/html"})
		res.write(data)
		res.end()
	    })
	}		
    })
}

var updateDevice = function(req, res, db) {
    query = url.parse(req.url, true).query

    deviceId = {"_id": ObjectId(query._id)}
    delete query._id
    db.hosts.update(deviceId, query, 'safe', function callback(err, count) {
	if (!err) {
	    res.writeHead(302, {"Location": "http://127.0.0.1:8888/"})
	    res.end()
	}
    })
}

// TODO: Make a little nicer. Maybe a html page.
var fourZeroFour = function(req, res, db) {
    console.log('Serving 404')
    res.writeHead(404, {"Content-Type": "text/plain"});
    res.write("404 Not found");
    res.end();
    return true
}

var pageIndex = {}
pageIndex['/'] = indexHtml
pageIndex['/index.html'] = indexHtml
pageIndex['/index'] = index
pageIndex['/add_device.html'] = addDeviceHtml
pageIndex['/add_device'] = addDevice
pageIndex['/update_device.html'] = updateDeviceHtml
pageIndex['/update_device'] = updateDevice
pageIndex['/fourZeroFour.html'] = fourZeroFour

exports.pageIndex = pageIndex
