app = angular.module 'grades.app.static', []


# Controllers
app.controller 'AppController', ['$scope', '$http', ($scope, $http) ->
    $scope.grades = []
    $http.get('/api/grades').then (result) ->
        angular.forEach result.data, (item) ->
            $scope.grades.push item
]


# Services
app = angular.module 'grades.api', ['ngResource']

app.factory 'Grade', ['$resource', ($resource) ->
    $resource '/api/grades/:id', id: '@id'
]

