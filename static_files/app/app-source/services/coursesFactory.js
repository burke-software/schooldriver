angular.module('gradeBookApp.services')
  .factory(
  'coursesFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + '/courses/:courseId/ ',
        {
          courseId: '@courseId'
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
