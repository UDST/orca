var React = require('react');


function on_repr(on) {
  if (on === null) {
    return 'None';
  }
  return "'" + on + "'";
}

function index_repr(index) {
  if (index === false) {
    return 'False'
  }
  return 'True'
}

var BroadcastApp = React.createClass({
  getInitialState: function() {
    return {
      cast: '',
      onto: '',
      cast_on: '',
      onto_on: '',
      cast_index: '',
      onto_index: ''
    };
  },
  componentDidMount: function() {
    var cast = this.props.cast;
    var onto = this.props.onto;

    $.getJSON('/broadcasts/' + cast + '/' + onto + '/definition')
      .done(function(data) {
        this.setState(data);
      }.bind(this));
  },
  render: function() {
    return (
      <div className="broadcastApp">
        <div className="page-header">
          <h1>{this.state.cast + ' -> ' + this.state.onto}</h1>
        </div>
        <div>
          <p><strong>Cast</strong></p>
          <p>{this.state.cast}</p>
        </div>
        <div>
          <p><strong>Onto</strong></p>
          <p>{this.state.onto}</p>
        </div>
        <div>
          <p><strong>With</strong></p>
          <ul>
            <li><code>{'cast_on = ' + on_repr(this.state.cast_on)}</code></li>
            <li><code>{'onto_on = ' + on_repr(this.state.onto_on)}</code></li>
            <li><code>{'cast_index = ' + index_repr(this.state.cast_index)}</code></li>
            <li><code>{'onto_index = ' + index_repr(this.state.onto_index)}</code></li>
          </ul>
        </div>
      </div>
    );
  }
});

module.exports = BroadcastApp;
