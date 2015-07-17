// Stuff related to displaying function definitions
var React = require('react');


var LiteralDefinition = React.createClass({
  render: function() {
    return (<p className="literalDefinition">{this.props.text}</p>);
  }
});

var FuncDefinition = React.createClass({
  render: function() {
    var f = this.props.funcData;
    return (
      <div className="funcDefinition">
        <h3>Source</h3>
        <p><code>{f.filename} @ line: {f.lineno}</code></p>
        <div dangerouslySetInnerHTML={{__html: this.props.funcData.html}}>
        </div>
      </div>
    );
  }
});

exports.LiteralDefinition = LiteralDefinition;
exports.FuncDefinition = FuncDefinition;
