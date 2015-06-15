var React = require('react');
var _ = require('lodash');

var TableList = React.createClass({
  render: function() {
    var table_els = _.map(this.props.tables, function(table) {
      return (
        <a href={"#tables/" + table} className="list-group-item" key={table}>
          {table}
        </a>
      );
    });

    return (
      <section>
        <h2>Tables</h2>
        <div className="tableList panel panel-default">
          <div className="list-group">
            {table_els}
          </div>
        </div>
      </section>
    );
  }
});

var StepList = React.createClass({
  render: function() {
    var step_els = _.map(this.props.steps, function(step) {
      return (
        <a href={"#steps/" + step} className="list-group-item" key={step}>
          {step}
        </a>
      );
    });

    return (
      <section>
        <h2>Steps</h2>
        <div className="stepList panel panel-default">
          <div className="list-group">
            {step_els}
          </div>
        </div>
      </section>
    );
  }
});

var InjectableList = React.createClass({
  render: function() {
    var inj_els = _.map(this.props.injectables, function(i) {
      return (
        <a href={"#injectables/" + i} className="list-group-item" key={i}>
          {i}
        </a>
      );
    });

    return (
      <section>
        <h2>Injectables</h2>
        <div className="injectableList panel panel-default">
          <div className="list-group">
            {inj_els}
          </div>
        </div>
      </section>
    );
  }
});

var BroadcastList = React.createClass({
  render: function() {
    var broad_els = _.map(this.props.broadcasts, function(b) {
      return (
        <a href={"#broadcasts/" + b.join("/")} className="list-group-item" key={b}>
          {b[0]} &ndash;&gt; {b[1]}
        </a>
      );
    });

    return (
      <section>
        <h2>Broadcasts</h2>
        <div className="broadcastList panel panel-default">
          <div className="list-group">
            {broad_els}
          </div>
        </div>
      </section>
    );
  }
});

var SchemaApp = React.createClass({
  getInitialState: function() {
    return {
      tables: [],
      cols: {},
      steps: [],
      injectables: [],
      broadcasts: []
    };
  },
  componentDidMount: function() {
    $.getJSON('/schema')
      .done(function (data) {
        this.setState(data);
      }.bind(this));
  },
  render: function() {
    return (
      <div className="schemaApp">
        <div className="page-header">
          <h1>Orca Schema</h1>
        </div>
        <div>
          <TableList tables={this.state.tables} />
          <StepList steps={this.state.steps} />
          <InjectableList injectables={this.state.injectables} />
          <BroadcastList broadcasts={this.state.broadcasts} />
        </div>
      </div>
    );
  }
});

module.exports = SchemaApp;
