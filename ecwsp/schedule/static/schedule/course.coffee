app = angular.module 'angular_sis', ['restangular', 'ngRoute']

app.controller 'CourseController', ['$scope', '$routeParams', '$route', 'Restangular', ($scope, $routeParams, $route, Restangular) ->
    course = Restangular.one('courses', $routeParams.course_id)
]

app.factory 'CourseService', ['Restangular', (Restangular) ->
    
]