
app = require('../app')

group_args = { home: { status: null, link: 'index.html' },
	       groups: { status: 'active', link: 'groups.html' },
	       devices: { status: null, link: 'devices.html' },
	       hosts: { status: null, link: 'hosts.html' },
	       title: 'Groups'
             }

exports.groups = function(req, res) {
    app.db.groups.find().sort({'group_no': 1}, function(err, data) {
	app.db.hosts.find({}, function(err, hosts) {
	    for (var i = 0; i < data.length; i++) {
		data[i]['hosts'] = []
		for (var j = 0; j < hosts.length; j++) {
		    if (data[i].group_no == hosts[j].group_no) {
			data[i]['hosts'].push(hosts[j])
		    }
		}
	    }
	    group_args['group'] = data
	    res.render('groups', group_args)
	})
    })
}

exports.create_group = function(req, res) {
    res.render('create_group', group_args)
}

exports.view_group = function(req, res) {
    app.db.groups.findOne({'group_no': req.query.group_no}, function(err, data) {
	group_args['group'] = data
	res.render('view_group', group_args)
    })
}

exports.add_group = function(req, res) {
    app.db.groups.find().sort({'group_no':-1}, function(err, data) {
	if (data.length > 0) {
	    next_group = (parseInt(data[0].group_no) + 1).toString()
	    req.query['group_no'] = next_group
	    app.db.groups.save(req.query, function(err, saved) {
		res.redirect('/groups.html')
	    })
	}
    })
}

exports.mod_group = function(req, res) {
    app.db.groups.update({'group_no': req.query.group_no}, {'$set': req.query}, 'safe', function(err) {
	res.redirect('/groups.html')
    })
}

exports.del_group = function(req, res) {
    app.db.groups.remove({'group_no': req.query.group_no}, function(err) {
	data_update = {'group_no': "-1"}
	app.db.hosts.update({'group_no': req.query.group_no}, {'$set': data_update}, 'safe', function(err) {
	    res.redirect('/groups.html')
	})
    })
}
