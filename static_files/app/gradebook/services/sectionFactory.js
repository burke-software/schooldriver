angular.module('gradeBookApp.services')
  .factory(
  'sectionFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + 'sections/:sectionId/ ',
        {
          sectionId: '@sectionId'
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
