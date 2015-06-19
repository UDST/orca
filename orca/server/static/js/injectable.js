var React = require('react');

var ViewButtonGroup = require('./buttons.js');
var funcdef = require('./funcdef.js');


var InjDefinition = React.createClass({
  componentDidMount: function() {
    var inj_name = this.props.inj_name;

    $.getJSON('/injectables/' + inj_name + '/definition')
      .done(function(data) {
        if (data.type === 'variable') {
          var component = <funcdef.LiteralDefinition text="Variable" />;
        } else if (data.type === 'function') {
          var component = <funcdef.FuncDefinition funcData={data} />;
        }

        React.render(component, document.getElementById('inj-definition'));
      });
  },
  render: function() {
    return (<div id="inj-definition"></div>);
  }
});

var InjRepr = React.createClass({
  getInitialState: function() {
    return {type: '', repr: ''};
  },
  componentDidMount: function() {
    var inj_name = this.props.inj_name;

    $.getJSON('/injectables/' + inj_name + '/repr')
      .done(function(data) {
        this.setState(data);
      }.bind(this));
  },
  render: function() {
    return (
      <div className="injRepr">
        <div>
          <p>Type</p>
          <p><code>{this.state.type}</code></p>
        </div>
        <div>
          <p>Repr</p>
          <p><code>{this.state.repr}</code></p>
        </div>
      </div>);
  }
});

var InjectableApp = React.createClass({
  viewButtons: [
    {text: 'Definition', view: 'definition'},
    {text: 'Repr', view: 'repr'}
  ],
  getInitialState: function() {
    return {view: this.viewButtons[0].view};
  },
  handleButtonClick: function(view) {
    if (view !== this.state.view) {
      this.setState({view: view});
    }
  },
  render: function() {
    var view = this.state.view;
    var inj_name = this.props.inj_name;

    if (view === 'definition') {
      var appComponent = <InjDefinition inj_name={inj_name} />;
    } else if (view === 'repr') {
      var appComponent = <InjRepr inj_name={inj_name} />;
    }

    return (
      <div className="injectableApp">
        <div className="page-header">
          <h1>{this.props.inj_name}</h1>
        </div>
        <ViewButtonGroup
            buttons={this.viewButtons}
            view={this.state.view}
            clickHandler={this.handleButtonClick} />
        {appComponent}
      </div>
    );
  }
});

module.exports = InjectableApp;
