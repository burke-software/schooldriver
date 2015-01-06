exports.config = {
  // The address of a running selenium server.
  seleniumAddress: 'http://localhost:4444/wd/hub',

  // The div which contains the app (this should be changed when
  // all angular apps use the SpaView() page)
  rootElement: '.app-div',

  // Spec patterns are relative to the location of the spec file. They may
  // include glob patterns.
  suites: {
    admissions: ['admissions/student_application_spec.js',],
  },
};