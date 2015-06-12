var Grapnel = require('grapnel');
var React = require('react');

var SchemaApp = require('./schema.js');

var router = new Grapnel();

router.get('', function(req) {
    React.render(<SchemaApp />, document.getElementById('content'));
});
