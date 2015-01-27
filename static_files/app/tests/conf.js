var config = {

  // The div which contains the app (this should be changed when
  // all angular apps use the SpaView() page)
  rootElement: '.app-div',

  specs: ['admissions/student_application_spec.js',],
  
  // Spec patterns are relative to the location of the spec file. They may
  // include glob patterns.
  suites: {
      admissions: ['admissions/student_application_spec.js',],
  },
  
  capabilities: {
      'browserName': 'chrome'
  },
  
};

if (process.env.TRAVIS) {
    config.sauceUser = process.env.SAUCE_USERNAME;
    config.sauceKey = process.env.SAUCE_ACCESS_KEY;
    config.capabilities['tunnel-identifier'] = process.env.TRAVIS_JOB_NUMBER;
    config.capabilities['build'] = process.env.TRAVIS_BUILD_NUMBER;
} else {
    config.seleniumAddress = 'http://localhost:4444/wd/hub';
}

exports.config = config;

