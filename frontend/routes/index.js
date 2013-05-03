
/*
 * GET home page.
 */

db = require('../app').db

exports.index = function(req, res){
  args = { home: { status: 'active', link: '#' },
           groups: { status: null, link: 'groups.html' },
           devices: { status: null, link: 'devices.html' },
           hosts: { status: null, link: 'hosts.html' },
           title: 'Home'
         }
  res.render('index', args);
};
