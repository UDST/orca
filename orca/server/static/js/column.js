var React = require('react');
var classNames = require('classnames');
var _ = require('lodash');

var dtopts = require('./dtopts.js');
var ViewButtonGroup = require('./buttons.js');
var funcdef = require('./funcdef.js');


var ColumnPreview = React.createClass({
  componentDidMount: function() {
    var table = this.props.table;
    var col = this.props.column;

    $.getJSON('/tables/' + table + '/columns/' + col + '/preview')
      .done(function(data) {
        $('#preview-table').DataTable(dtopts.series_opts(data));
      });
  },
  render: function() {
    return (
      <div className="tablePreview">
        <table className="display" id="preview-table">
        </table>
      </div>);
  }
});

var ColumnDefinition = React.createClass({
  componentDidMount: function() {
    var table = this.props.table;
    var col = this.props.column;

    $.getJSON('/tables/' + table + '/columns/' + col + '/definition')
      .done(function(data) {
        if (data.type === 'series') {
          var component = <funcdef.LiteralDefinition text="Series" />;
        } else if (data.type === 'local') {
          var component = <funcdef.LiteralDefinition text="Local Column" />;
        } else if (data.type === 'function') {
          var component = <funcdef.FuncDefinition funcData={data} />;
        }

        React.render(component, document.getElementById('column-definition'));
      });
  },
  render: function() {
    return (
      <div id="column-definition"></div>
    );
  }
});

var ColumnDescribe = React.createClass({
  componentDidMount: function() {
    var table = this.props.table;
    var col = this.props.column;

    $.getJSON('/tables/' + table + '/columns/' + col + '/describe')
      .done(function(data) {
        $('#describe-table').DataTable(dtopts.series_opts(data));
      });
  },
  render: function() {
    return (
      <div className="tableDescribe">
        <table className="display" id="describe-table">
        </table>
      </div>
    );
  }
});

var ColumnApp = React.createClass({
  colButtons: [
    {text: 'Preview', view: 'preview'},
    {text: 'Definition', view: 'definition'},
    {text: 'Describe', view: 'describe'}
  ],
  getInitialState: function() {
    return {view: this.colButtons[0].view};
  },
  handleButtonClick: function(view) {
    if (view !== this.state.view) {
      this.setState({view: view});
    }
  },
  render: function() {
    var view = this.state.view;
    var table = this.props.table;
    var col = this.props.column;

    if (view === 'preview') {
      var appComponent = <ColumnPreview table={table} column={col} />;
    } else if (view === 'definition') {
      var appComponent = <ColumnDefinition table={table} column={col} />;
    } else if (view === 'describe') {
      var appComponent = <ColumnDescribe table={table} column={col} />;
    }

    return (
      <div className="columnApp">
        <div className="page-header">
          <h1>{table + '.' + col}</h1>
        </div>
        <ViewButtonGroup
            buttons={this.colButtons}
            view={this.state.view}
            clickHandler={this.handleButtonClick} />
        {appComponent}
      </div>
    );
  }
});

module.exports = ColumnApp;
