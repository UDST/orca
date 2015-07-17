// Display information about Orca steps
var React = require('react');

var funcdef = require('./funcdef.js');

var StepApp = React.createClass({
  componentDidMount: function() {
    $.getJSON('/steps/' + this.props.step + '/definition')
      .done(function(data) {
        React.render(
          <funcdef.FuncDefinition funcData={data} />,
          document.getElementById('step-definition'));
      });
  },
  render: function() {
    return (
      <div className="stepApp">
        <div className="page-header">
          <h1>{this.props.step}</h1>
        </div>
        <div id="step-definition"></div>
      </div>
    );
  }
});

module.exports = StepApp;
