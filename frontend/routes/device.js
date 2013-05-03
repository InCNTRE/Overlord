
app = require('../app')

device_args = { home: { status: null, link: 'index.html' },
		groups: { status: null, link: 'groups.html' },
		devices: { status: 'active', link: 'devices.html' },
		hosts: { status: null, link: 'hosts.html' },
		title: 'Devices'
              }

exports.devices = function(req, res){
    app.db.devices.find({}, function(err, data) {
	device_args['ofdevice'] = data
	res.render('devices', device_args)
    })
}

exports.view_device = function(req, res) {
    app.db.devices.findOne({'dpid': req.query.dpid}, function(err, data) {
	device_args['ofdevice'] = data
	res.render('view_device', device_args)
    })
}

exports.mod_device = function(req, res) {
    app.db.devices.update({'dpid': req.query.dpid}, {'$set': req.query}, 'safe', function(err) {
	res.redirect('/devices.html')
    })
}

exports.del_device = function(req, res) {
    app.db.devices.remove({'dpid': req.query.dpid}, function(err) {
	res.redirect('/devices.html')
    })
}

exports.add_device_patch = function(req, res) {

}

exports.del_device_patch = function(req, res) {

}

exports.mod_device_patch = function(req, res) {

}

