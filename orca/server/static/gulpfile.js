var gulp = require('gulp');
var gutil = require('gulp-util');
var source = require('vinyl-source-stream');
var browserify = require('browserify');
var watchify = require('watchify');
var reactify = require('reactify');
var streamify = require('gulp-streamify');
var _ = require('lodash');

var config = {
  main: 'js/main.js',
  out: 'bundle.js',
  dest: 'js/dist'
};

// for files that need to be run through browserify and reactify
gulp.task('js', function() {
  var bfy_opts = {
    entries: [config.main],
    transform: [reactify],
    debug: true
  };
  _.assign(bfy_opts, watchify.args);
  var watcher = watchify(browserify(bfy_opts));

  function bundle() {
    watcher.bundle()
      .on('error', gutil.log.bind(gutil, 'Browserify Error'))
      .pipe(source(config.out))
      .pipe(gulp.dest(config.dest))
  }

  watcher.on('update', bundle);
  watcher.on('log', gutil.log);

  return bundle();
});

gulp.task('default', ['js']);
