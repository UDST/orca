var React = require('react');
var classNames = require('classnames');
var _ = require('lodash');


var ViewButton = React.createClass({
  clickHandler: function(event) {
    this.props.clickHandler(this.props.view);
  },
  render: function() {
    var classes = classNames({
      "viewButton": true,
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

var ViewButtonGroup = React.createClass({
  render: function() {
    var button_els = _.map(this.props.buttons, function(b) {
      return (
        <ViewButton
          text={b.text}
          view={b.view}
          key={b.view}
          active={b.view === this.props.view}
          clickHandler={this.props.clickHandler}
        />
      );
    }.bind(this));

    return (
      <div className="viewButtonGroup btn-group" role="group">
        {button_els}
      </div>
    );
  }
});

module.exports = ViewButtonGroup;
