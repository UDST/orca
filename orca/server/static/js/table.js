var React = require('react');
var _ = require('lodash');

var dtopts = require('./dtopts.js');
var ViewButtonGroup = require('./buttons.js');
var funcdef = require('./funcdef.js');


var TableInfo = React.createClass({
  getInitialState: function() {
    return {info: ''};
  },
  componentDidMount: function() {
    $.get('/tables/' + this.props.table + '/info')
      .done(function(data) {
        this.setState({info: data});
      }.bind(this));
  },
  render: function() {
    return (
      <div className="tableInfo">
        <pre>{this.state.info}</pre>
      </div>
    );
  }
});

var TablePreview = React.createClass({
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/preview')
      .done(function(data) {
        $('#preview-table').DataTable(dtopts.table_opts(data));
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

var TableDefinition = React.createClass({
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/definition')
      .done(function(data) {
        if (data.type === 'dataframe') {
          var component = <funcdef.LiteralDefinition text="DataFrame" />;
        } else if (data.type === 'function') {
          var component = <funcdef.FuncDefinition funcData={data} />;
        }

        React.render(component, document.getElementById('table-definition'));
      });
  },
  render: function() {
    return (
      <div id="table-definition"></div>
    );
  }
});

var TableDescribe = React.createClass({
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/describe')
      .done(function(data) {
        $('#describe-table').DataTable(dtopts.table_opts(data));
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

var TableColumns = React.createClass({
  getInitialState: function() {
    return {columns: []};
  },
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/columns')
      .done(function(data) {
        this.setState(data);
      }.bind(this));
  },
  render: function() {
    var col_els = _.map(this.state.columns, function(col) {
      return (
        <a
            href={'#tables/' + this.props.table + '/columns/' + col}
            className="list-group-item"
            key={this.props.table + '.' + col}>
          {col}
        </a>
      );
    }.bind(this));

    return (
      <div className="tableColumns list-group">
        {col_els}
      </div>
    );
  }
});

var TableApp = React.createClass({
  tableButtons: [
    {text: 'Info', view: 'info'},
    {text: 'Preview', view: 'preview'},
    {text: 'Definition', view: 'definition'},
    {text: 'Describe', view: 'describe'},
    {text: 'Columns', view: 'columns'}
  ],
  getInitialState: function() {
    return {view: this.tableButtons[0].view};
  },
  handleButtonClick: function(view) {
    if (view !== this.state.view) {
      this.setState({view: view});
    }
  },
  render: function() {
    var view = this.state.view;
    var table = this.props.table;

    if (view === 'info') {
      var tableComponent = <TableInfo table={table} />;
    } else if (view === 'preview') {
      var tableComponent = <TablePreview table={table} />;
    } else if (view === 'definition') {
      var tableComponent = <TableDefinition table={table} />;
    } else if (view === 'describe') {
      var tableComponent = <TableDescribe table={table} />;
    } else if (view === 'columns') {
      var tableComponent = <TableColumns table={table} />;
    }

    return (
      <div className="tableApp">
        <div className="page-header">
          <h1>{this.props.table}</h1>
        </div>
        <ViewButtonGroup
            buttons={this.tableButtons}
            view={this.state.view}
            clickHandler={this.handleButtonClick} />
        {tableComponent}
      </div>
    );
  }
});

module.exports = TableApp;
