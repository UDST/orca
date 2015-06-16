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
          onClick={this.clickHandler}
          data-view={this.props.view}>
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
          text={b[0]}
          view={b[1]}
          key={b[1]}
          active={b[1] === this.props.view ? true : false}
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

var TableDefinition = React.createClass({
  render: function() {
    return (
      <div><p>{this.props.table}</p></div>
    );
  }
});

var TableApp = React.createClass({
  tableButtons: [['Preview', 'preview'], ['Definition', 'definition']],
  getInitialState: function() {
    return {view: this.tableButtons[0][1]};
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
