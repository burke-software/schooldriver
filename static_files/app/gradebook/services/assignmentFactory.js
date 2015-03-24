angular.module('gradeBookApp.services')
  .factory(
  'assignmentFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + 'assignments/:assignmentId/ ',
        {
          assignmentId: '@assignmentId'
        },
        {
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
