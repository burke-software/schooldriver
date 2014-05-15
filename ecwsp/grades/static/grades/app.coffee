app = angular.module 'grades.app.static', ['restangular', 'uiHandsontable']

app.controller 'AppController', ['$scope', 'Restangular', ($scope, Restangular) ->
    border = 30
    winHeight = $(window).height()
    topOffset = $("#grade_table").offset().top
    $scope.calcHeight = () ->
        height = winHeight - topOffset - 2 * border
        if height < 50
           return 50
        return height
        
    # Get the course_id - using a router might be nicer
    url = $(location).attr('href').split('/')
    url.pop()
    course_id = url.pop()
    
    students = []
    $scope.students = students
    marking_periods = []
    $scope.columns = [
        { value: 'student.student', title: 'Student', readOnly: true}
    ]

    grade_api = Restangular.all('grades')
    grade_api.getList({course: course_id}).then (grades) ->
        $scope.grades = grades
        
        # Need to rearrange the array to look like
        # Student | Grade1 | Grade etc | Final
        angular.forEach grades, (grade) ->
            new_student = true
            this_student = null
            for student in students
                if student.student_id == grade.student_id
                    new_student = false
            if new_student
                students.push({student: grade.student, student_id: grade.student_id, final: 0})
                
            new_marking_period = true
            for marking_period in marking_periods
                if marking_period.marking_period_id == grade.marking_period_id
                    new_marking_period = false
            if new_marking_period
                marking_periods.push({marking_period: grade.marking_period, marking_period_id: grade.marking_period_id})
    
        grade_columns = []
        for marking_period in marking_periods
            grade_key = 'grade' + marking_period.marking_period_id
            $scope.columns.push({value: 'student.' + grade_key + '.grade', title: marking_period.marking_period})
            for student in students
                for grade in $scope.grades
                    if grade.marking_period_id == marking_period.marking_period_id and grade.student_id == student.student_id
                        student[grade_key] = grade
        $scope.columns.push({value: 'student.final', title: 'Final'})

    recalculateGrades = (student) ->
        final = 0.0
        num_of_mp = 0
        for marking_period in marking_periods
            grade = parseFloat(student['grade' + marking_period.marking_period_id].grade)
            final += grade
            student.final = final / num_of_mp
    
    $scope.changeGrade = (changes, source) ->
        if source != 'loadData'  # whitelist might be better source == 'edit' or source == 'autofill'
            for change in changes
                id = change[0]
                attribute = change[1]
                student = $scope.students[id]
                recalculateGrades(student)
                instance = student[attribute.split('.')[0]]
                instance.save()
            
]
