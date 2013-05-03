
/**
 * Module dependencies.
 */

var express = require('express') 
, routes = require('./routes')
, device = require('./routes/device')
, host = require('./routes/host')
, group = require('./routes/group')
, user = require('./routes/user')
, http = require('http')
, path = require('path');

var app = express();
exports.db = require('mongojs').connect('localhost/overlord', ['devices', 'groups', 'hosts', 'messages'])

app.configure(function(){
    app.set('port', process.env.PORT || 3000);
    app.set('views', __dirname + '/views');
    app.set('view engine', 'jade');
    app.use(express.favicon());
    app.use(express.logger('dev'));
    app.use(express.bodyParser());
    app.use(express.methodOverride());
    app.use(express.cookieParser('your secret here'));
    app.use(express.session());
    app.use(app.router);
    app.use(express.static(path.join(__dirname, 'public')));
});

app.configure('development', function(){
  app.use(express.errorHandler());
});

app.get('/', routes.index);
app.get('/index.html', routes.index);
app.get('/devices.html', device.devices);
app.get('/view_device.html', device.view_device);
app.get('/mod_device', device.mod_device); //Submit device mod
app.get('/del_device', device.del_device); //Submit device del
//app.get('/add_device_patch', device.add_device_patch);
//app.get('/del_device_patch', device.del_device_patch);
//app.get('/mod_device_patch', device.mod_device_patch);

app.get('/hosts.html', host.hosts);
app.get('/view_host.html', host.view_host);
app.get('/mod_host', host.mod_host); //Submit host mod
app.get('/del_host', host.del_host); //Submit host del
app.get('/group_host', host.group_host);

app.get('/groups.html', group.groups);
app.get('/create_group.html', group.create_group);
app.get('/view_group.html', group.view_group);
app.get('/add_group', group.add_group);
app.get('/mod_group', group.mod_group); //Submit group mod
app.get('/del_group', group.del_group); //Submit group del
//app.get('/users', user.list);

http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});
