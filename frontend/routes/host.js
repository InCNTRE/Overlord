
app = require('../app')

host_args = { home: { status: null, link: 'index.html' },
	      groups: { status: null, link: 'groups.html' },
	      devices: { status: null, link: 'devices.html' },
	      hosts: { status: 'active', link: 'hosts.html' },
	      title: 'Hosts'
            }

exports.hosts = function(req, res) {
    app.db.hosts.find({}, function(err, data) {
	host_args['host'] = data
	res.render('hosts', host_args)
    })
}

exports.view_host = function(req, res) {
    app.db.hosts.findOne({'mac': req.query.mac}, function(err, data) {
	host_args['host'] = data
	res.render('view_host', host_args)
    })
}

exports.mod_host = function(req, res) {
    app.db.hosts.update({'mac': req.query.mac}, {'$set': req.query}, 'safe', function(err) {
	res.redirect('/hosts.html')
    })
}

exports.del_host = function(req, res) {
    app.db.hosts.remove({'mac': req.query.mac}, function(err) {
	res.redirect('/hosts.html')
    })
}

exports.group_host = function(req, res) {
    data_update = {'group_no': req.query.group_no}
    app.db.hosts.update({'mac': req.query.mac}, {'$set': data_update}, 'safe', function(err) {
	msg = {'message': 'group', 'group_no': req.query.group_no, 'mac': req.query.mac}
	app.db.messages.save(msg, function(err, data) {
	    res.send(200)
	})
    })
}
