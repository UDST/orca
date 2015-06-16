var React = require('react');
var classNames = require('classnames');
var _ = require('lodash');
var dtopts = require('./dtopts.js');


var TableButton = React.createClass({
  clickHandler: function(event) {
    this.props.clickHandler(this.props.view);
  },
  render: function() {
    var classes = classNames({
      "btn": true,
      "btn-default": true,
      "active": this.props.active
    });

    return (
      <button
          type="button"
          className={classes}
          onClick={this.clickHandler}>
        {this.props.text}
      </button>
    );
  }
});

var TableButtons = React.createClass({
  render: function() {
    var button_els = _.map(this.props.buttons, function(b) {
      return (
        <TableButton
          text={b.text}
          view={b.view}
          key={b.view}
          active={b.view === this.props.view}
          clickHandler={this.props.clickHandler}
        />
      );
    }.bind(this));

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

var TableDefinitionDF = React.createClass({
  render: function() {
    return (<p>DataFrame</p>);
  }
});

var TableDefinitionFunc = React.createClass({
  render: function() {
    return (
      <div dangerouslySetInnerHTML={{__html: this.props.funcData.html}}>
      </div>
    );
  }
});

var TableDefinition = React.createClass({
  componentDidMount: function() {
    $.getJSON('/tables/' + this.props.table + '/definition')
      .done(function(data) {
        if (data.type === 'dataframe') {
          var component = <TableDefinitionDF />;
        } else if (data.type === 'function') {
          var component = <TableDefinitionFunc funcData={data} />;
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

var TableApp = React.createClass({
  tableButtons: [
    {text: 'Preview', view: 'preview'},
    {text: 'Definition', view: 'definition'}
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
    if (view === 'preview') {
      var tableComponent = <TablePreview table={this.props.table} />;
    } else if (view === 'definition') {
      var tableComponent = <TableDefinition table={this.props.table} />;
    }

    return (
      <div className="tableApp">
        <div className="page-header">
          <h1>{this.props.table}</h1>
        </div>
        <TableButtons
            buttons={this.tableButtons}
            view={this.state.view}
            clickHandler={this.handleButtonClick} />
        {tableComponent}
      </div>
    );
  }
});

module.exports = TableApp;
