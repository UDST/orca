var React = require('react');
var classNames = require('classnames');
var _ = require('lodash');
var dtopts = require('./dtopts.js');

var ColumnApp = React.createClass({
  render: function() {
    return (
      <div className="columnApp">
        <div className="page-header">
          <h1>{this.props.table + '.' + this.props.column}</h1>
        </div>
      </div>
    );
  }
});

module.exports = ColumnApp;
