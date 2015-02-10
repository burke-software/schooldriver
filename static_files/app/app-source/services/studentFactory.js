angular.module('gradeBookApp.services')
  .factory(
  'studentFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log) {
      return $resource(appConfig.apiUrl + '/student/:studentId/ ',
        {
          studentId: '@studentId'
        },
        {
          update: {
            method: 'PUT'
          },
          get: {
            method: 'GET',
            interceptor: {
              responseError: function (error) {
                $log.error('GET SINGLE USER:', error);
                return {
                  id: 1,
                  firstName: 'Ashor',
                  lastName: 'Lior',
                  finalGrade: 0,
                  assignments: [
                    {
                      id: 1,
                      assignmentId:1,
                      value: 26
                    },
                    {
                      id:2,
                      assignmentId:2,
                      value: 35
                    },
                    {
                      id: 3,
                      assignmentId:3,
                      value: 57
                    }
                  ]
                }
              }
            }
          }
        }
      )
    }
  ]
);
