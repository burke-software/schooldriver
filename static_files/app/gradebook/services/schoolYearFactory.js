angular.module('gradeBookApp.services')
  .factory(
  'schoolYearFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + 'school_years/:schoolYearId/ ',
        {
          schoolYearId: '@schoolYearId'
        },
        {
          get: {
            isArray: true
          },
          create: {
            method: 'POST'
          },
          update: {
            method: 'PUT'
          }
        }
      )
    }
  ]
);
