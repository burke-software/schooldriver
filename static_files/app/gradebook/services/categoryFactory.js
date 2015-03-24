angular.module('gradeBookApp.services')
  .factory(
  'categoryFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log) {
      return $resource(appConfig.apiUrl + '/categories/ ',
        {
        },
        {
         get: {
           method: 'GET',
           isArray: true,
           interceptor: {
             responseError: function (error) {
               $log.error('GET CATEGORY LIST');
               return [
                 {
                   id: 1,
                   name: 'Category 1'
                 },
                 {
                   id: 2,
                   name: 'Category 2'
                 },
                 {
                   id: 3,
                   name: 'Category 3'
                 }
               ];
             }
           }
         }
        }
      )
    }
  ]
);
