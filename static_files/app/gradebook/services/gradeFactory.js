/**
 * Created by jkl on 05.01.15.
 */
angular.module('gradeBookApp.services')
  .factory(
  'gradeFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + 'grades/:gradeId/ ',
        {
          gradeId: '@gradeId'
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
