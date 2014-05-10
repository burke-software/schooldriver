app = angular.module 'grades.app.static', ['ngResource', 'uiHandsontable']

app.controller 'AppController', ['$scope', 'Grade', ($scope, Grade) ->
    ###
    border = 30
    winHeight = $(window).height()
    console.log(winHeight);
    topOffset = $("#grade_table").offset().top
    $scope.calcHeight = () ->
        height = winHeight - topOffset - 2 * border
        if height < 50
           return 50
        return height
    ###

    url = $(location).attr('href').split('/')
    url.pop()
    course_id = url.pop()

    ###
    $scope.grades = Grade.query(course: course_id)
    $scope.changeGrade = (grade) ->
       grade.comment = "foo time"
       grade.$update()
    ###
    

    grades = Grade.query course: course_id, () ->
        $('#example1').handsontable('render')

    container = $('#example1')
    container.handsontable
        data: grades
        dataType: "json"
        columns: [
            {data: "student", readOnly: true}
            {data: "grade"}
            {data: "comment"}
        ]
        minRows: 10
        minCols: 3
        colHeaders: ["Student", "Grade", "Comments"]
        afterChange: (changes, source) ->
            if source != 'loadData'
                for change in changes
                    id = change[0]
                    attribute = change[1]
                    instance = grades[id]
                    if attribute == 'grade'
                        instance.grade = change[3]
                    if attribute == 'comment'
                        instance.comment = change[3]
                    instance.$update()

]


app.factory 'Grade', ['$resource', ($resource) ->
    $resource '/api/grades/:id/', id: '@id',
    {
        'update': { method:'PUT' }
    }
]


