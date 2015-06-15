var React = require('react');
var _ = require('lodash');
var dtopts = require('./dtopts.js');


var TableButtons = React.createClass({
  render: function() {
    var buttons = [['Preview', 'preview']];
    var button_els = _.map(buttons, function(b, i) {
        var classes = "btn btn-default";
        if (i === 0) {
          classes += " active";
        }
      return (
        <button type="button" className={classes} key={b[1]}>
          {b[0]}
        </button>
      );
    });

    return (
      <div className="tableButtons btn-group" role="group">
        {button_els}
      </div>
    );
  }
});

var TablePreview = React.createClass({
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/preview')
      .done(function(data) {
        $('#preview-table').DataTable(dtopts(data));
      });
  },
  render: function() {
    return (
      <div>
        <table className="display" id="preview-table">
        </table>
      </div>);
  }
});

var TableApp = React.createClass({
  render: function() {
    return (
      <div className="tableApp">
        <div className="page-header">
          <h1>{this.props.table}</h1>
        </div>
        <TableButtons />
        <TablePreview table={this.props.table} />
      </div>
    );
  }
});

module.exports = TableApp;
