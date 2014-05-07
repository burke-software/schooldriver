app = angular.module 'grades.app.static', ['ngResource']


app.controller 'AppController', ['$scope', 'Grade', ($scope, Grade) ->
    $scope.grades = Grade.query()
    $scope.changeGrade = (grade) ->
       grade.comment = "foo time"
       grade.$update()
]


app.factory 'Grade', ['$resource', ($resource) ->
    $resource '/api/grades/:id', id: '@id',
    {
        'update': { method:'PUT' }
    }
]
