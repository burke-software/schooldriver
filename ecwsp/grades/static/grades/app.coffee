app = angular.module 'grades.app.static', ['ngResource', 'uiHandsontable']

app.controller 'AppController', ['$scope', 'Grade', ($scope, Grade) ->
    border = 30
    winHeight = $(window).height()
    console.log(winHeight);
    topOffset = $("#grade_table").offset().top
    $scope.calcHeight = () ->
        height = winHeight - topOffset - 2 * border
        if height < 50
           return 50
        return height
        

    url = $(location).attr('href').split('/')
    url.pop()
    course_id = url.pop()

    $scope.grades = Grade.query(course: course_id)
    $scope.changeGrade = (grade) ->
       grade.comment = "foo time"
       grade.$update()
]


app.factory 'Grade', ['$resource', ($resource) ->
    $resource '/api/grades/:id/', id: '@id',
    {
        'update': { method:'PUT' }
    }
]


