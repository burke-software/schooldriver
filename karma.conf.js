// Karma configuration
// Generated on Mon Feb 16 2015 20:53:37 GMT-0500 (EST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'components/bower_components/jquery/dist/jquery.min.js',
      'components/bower_components/angular/angular.min.js',
      'components/bower_components/angular-mocks/angular-mocks.js',
      'components/bower_components/underscore/underscore.js',
      'components/bower_components/restangular/dist/restangular.min.js',
      'components/bower_components/angular-resource/angular-resource.min.js',
      'components/bower_components/angular-cookies/angular-cookies.min.js',
      'components/bower_components/angular-route/angular-route.min.js',
      'components/bower_components/angular-bootstrap/ui-bootstrap-tpls.min.js',
      'components/bower_components/bootstrap-hover-dropdown/bootstrap-hover-dropdown.min.js',
      'components/bower_components/handsontable/dist/handsontable.full.min.js',
      'components/bower_components/nghandsontable/dist/ngHandsontable.min.js',
      'static_files/app/gradebook/dist/app/gradebook.js',
      'static_files/app/common/restfulModel.js',
      'static_files/app/angular_sis.js',
      'static_files/app/grades/grades.js',
      'static_files/app/grades/course.js',
      'static_files/app/**/*test.js'
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
