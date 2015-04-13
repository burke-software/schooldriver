'use strict';

angular.module('gradeBookApp', [
  'ngRoute',
  'ngResource',
  'ngCookies',
  'ui.bootstrap',
  'ngHandsontable',
  'gradeBookApp.controllers',
  'gradeBookApp.services',
  'gradeBookApp.templates'
])
  .config(
  [
    '$provide',
    '$routeProvider',
    function ($provide, $routeProvider) {
      $provide.factory('appConfig', function () {
        return {
          apiUrl: '/api/'
        }
      });

      $routeProvider.
        when('/gradebook/',{
          controller: 'gradeBookCtrl',
          templateUrl: staticURL('app/gradebook/modules/gradebook/gradebook.html')
        })
        .when('/gradebook/sections/:sectionId',{
          controller: 'singleSectionCtrl',
          templateUrl: staticURL('app/gradebook/modules/singleSection/singleSection.html')
        });

    }
  ]
).run(
  [
    '$http',
    '$cookies',
    function ($http,$cookies){
      $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
    }
  ]
);
angular.module('gradeBookApp.services', []);
angular.module('gradeBookApp.controllers',[]);
