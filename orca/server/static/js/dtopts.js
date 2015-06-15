var _ = require('lodash');

// Make an object of DataTable options from JSON data of a DataFrame
// in "split" format.
function dtopts(data) {
  var opts = {paging: false};

  // Column heading values, including one for the index values
  opts['columns'] = _.map(data.columns, function(c) {
    return {title: c};
  });
  opts['columns'].unshift({title: 'Index'});

  // Data, including add the index at the front of each row
  opts['data'] = _.map(data.data, function(row, i) {
    return [data.index[i]].concat(row);
  });

  return opts;
}

module.exports = dtopts;
