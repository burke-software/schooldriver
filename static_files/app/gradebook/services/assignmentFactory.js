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
)
    .factory(
    'assignmentTypeFactory',
    [
        'appConfig',
        '$resource',
        function (appConfig, $resource) {
          return $resource(
              appConfig.apiUrl + 'assignment_types/:typeId',
              {
                typeId: '@typeId'
              },
              {
                get: {
                  isArray: true
                }
              }
          )
        }
    ]
)
    .factory(
    'assignmentCategoryFactory',
    [
      'appConfig',
      '$resource',
      '$log',
      function (appConfig, $resource, $log) {
        return $resource(appConfig.apiUrl + 'assignment_categorys/:categoryId ',
            {
              categoryId: '@categoryId'
            },
            {
              get: {
                isArray: true
              }
            }
        )
      }
    ]
)
    .factory(
    'benchmarkFactory',
    [
      'appConfig',
      '$resource',
      '$log',
      function (appConfig, $resource, $log) {
        return $resource(appConfig.apiUrl + 'benchmarks/:benchmarkId ',
            {
              benchmarkId: '@benchmarkId'
            },
            {
              get: {
                isArray: true
              }
            }
        )
      }
    ]
)

;
