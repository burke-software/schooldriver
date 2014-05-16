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
        { width: 160, value: 'student.student', title: 'Student', fixed: true, readOnly: true}
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
                final = {grade: 0}
                students.push({student: grade.student, student_id: grade.student_id, final: final})
                
            new_marking_period = true
            for marking_period in marking_periods
                if marking_period.marking_period_id == grade.marking_period_id
                    new_marking_period = false
            if new_marking_period and grade.marking_period != null
                marking_periods.push({marking_period: grade.marking_period, marking_period_id: grade.marking_period_id})
    
        grade_columns = []
        for marking_period in marking_periods
            marking_period.grade_key = 'grade' + marking_period.marking_period_id
            $scope.columns.push({width: 70, value: 'student.' + marking_period.grade_key + '.grade', title: marking_period.marking_period})
            for student in students
                for grade in $scope.grades
                    if grade.student_id == student.student_id
                        if grade.marking_period_id == marking_period.marking_period_id
                            student[marking_period.grade_key] = grade
                        else if grade.override_final == true
                            student.final = grade
        $scope.columns.push({width: 70, value: 'student.final.grade', title: 'Final'})
        for student in students
            recalculateGrades(student)

    recalculateGrades = (student) ->
        final = 0.0
        num_of_mp = 0
        for marking_period in marking_periods
            grade = student['grade' + marking_period.marking_period_id].grade
            gradeFloat = parseFloat(grade)
            if grade != null
                if isNaN(gradeFloat)
                    gradeLower = grade.toLowerCase()
                    if gradeLower == "i"
                        return "I"
                    else if gradeLower in ["p", "lp", "hp"]
                        final += 100
                        num_of_mp += 1
                    else if gradeLower in ["f", "m"]
                        num_of_mp += 1
                else
                    final += gradeFloat
                    num_of_mp += 1
        final_grade = (final / num_of_mp).toFixed(2)
        if isNaN(final_grade)
            student.final.grade = ''
        else
            student.final.grade = final_grade
    
    comment_ids = []
    $scope.comment_button_text = "Don't click here"
    $scope.showComments = () ->
        if comment_ids.length == 0
            $scope.comment_button_text = "I don't blame you"
            for marking_period in marking_periods
                for column, key in $scope.columns
                    if column.value == 'student.' + marking_period.grade_key + '.grade'
                        $scope.columns.splice(key+1, 0, ({width: 160, value: 'student.' + marking_period.grade_key + '.comment', title: marking_period.marking_period + ' Comments'}))
                        comment_ids.push(key+1)
                        break
        else
            deleted = 0
            for comment_id in comment_ids
                $scope.columns.splice(comment_id - deleted, 1)
                deleted += 1
            comment_ids = []
            $scope.comment_button_text = "Show comments"
    
    $scope.changeGrade = (changes, source) ->
        if source != 'loadData'  # whitelist might be better source == 'edit' or source == 'autofill'
            for change in changes
                id = change[0]
                student = $scope.students[id]
                attribute = change[1]
                if attribute == "final.grade"
                    if student.final.grade in ["", null, "None"]
                        if student.final.id
                            # This exists on the server. Kill it.
                            student.final.remove()
                            student['final'] = {grade: 0}
                        recalculateGrades(student)
                    else
                        if student.final.id
                            # Exists - update it
                            student.final.save()
                        else  # A new override
                            new_grade = {
                                student_id: student.student_id
                                course: course_id
                                grade: student.final.grade
                                override_final: true
                            }
                            grade_api.post(new_grade)
                else
                    if not student.final.id
                        recalculateGrades(student)
                    instance = student[attribute.split('.')[0]]
                    instance.save()

]
