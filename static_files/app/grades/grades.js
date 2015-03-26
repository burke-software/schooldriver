app.controller(
    'CourseGradesController',
    ['$scope', '$routeParams', '$filter', '$q', 'saveGradeService', 'Courses', 'Grades', 'FinalGrades',
    function($scope, $routeParams, $filter, $q, saveGradeService, Courses, Grades, FinalGrades) {
  var course_section_id = $routeParams.course_section_id;
  var course;
  var grades;
  $scope.gridData = {};
  $scope.gridData.columns = [{
    title: 'Student',
    readOnly: true,
    data: 'name',
    width: 100}];
  $scope.gridData.rows = [];
  $scope.htSettings = {};
  $scope.htSettings.afterChange = function(changes, source) {
    if (source !== 'loadData') {

      var hot = this;

      for (var i = 0, len = changes.length; i < len; i++) {
        var change = changes[i];
        var cell = hot.getCell(change[0], hot.propToCol(change[1]));
        var row = $scope.gridData.rows[change[0]];
        //saveGradeService.saveGrade(course_section_id, row.id, change[1], change[3]);
        saveGradeService.saveGrade(course_section_id, row.id, change, cell);
      }

      //angular.forEach(changes, function(change) {
      //
      //  var cell = hot.getCell(change[0], hot.propToCol(change[1]));
      //  var row = $scope.gridData.rows[change[0]];
      //  //saveGradeService.saveGrade(course_section_id, row.id, change[1], change[3]);
      //  saveGradeService.saveGrade(course_section_id, row.id, change, cell);
      //});
    }
  };
  
  $q.all([
    Courses.one(course_section_id).get().then(function(data) {
      course = data;
      $scope.course_name = course.course.fullname;
      angular.forEach($filter('orderBy')(course.marking_period, 'start_date'), function(mp) {
        $scope.gridData.columns.push({
          title: mp.name,
          data: 'grade_' + mp.id,
          width: 100
        });
      });
      $scope.gridData.columns.push({
        title: 'Final',
        data: 'grade_final',
        width: 100
      });
    }),
    Grades.getList({enrollment__course_section: course_section_id}).then(function(data){
      grades = data;
    }),
    FinalGrades.getList({enrollment__course_section: course_section_id}).then(function(data){
      finalGrades = data;
    })
  ]).then(function(){
    angular.forEach(course.enrollments, function(enrollment) {
      enrollment.name = enrollment.first_name + " " + enrollment.last_name;
      angular.forEach(grades, function(grade) {
        if (grade.student_id === enrollment.id) {
          enrollment['grade_' + grade.marking_period] = grade.grade;
        }
      });
      $scope.gridData.rows.push(enrollment);
      angular.forEach(finalGrades, function(grade) {
        if (grade.student_id === enrollment.id) {
          enrollment['grade_final'] = grade.grade;
        }
      });
    });
  })
}]);


app.controller(
    'StudentGradesController',
    ['$scope', '$routeParams', '$filter', '$q', 'saveGradeService', 'Students', 'Courses', 'SchoolYears', 'Grades', 'FinalGrades',
    function($scope, $routeParams, $filter, $q, saveGradeService, Students, Courses, SchoolYears, Grades, FinalGrades) {
  var student_id = $routeParams.student_id;
  var years;
  var grades;
  var finalGrades;
  var selectedYear = {};
  var courses;
  $scope.gridData = {};
  $scope.gridData.columns = [{
    title: 'Course',
    readOnly: true,
    data: 'name',
    width: 100}];
  $scope.htSettings = {};
  $scope.htSettings.afterChange = function(changes, source) {

    var hot = this;

    if (source !== 'loadData') {
      angular.forEach(changes, function(change) {
        var cell = hot.getCell(change[0], hot.propToCol(change[1]));
        var row = $scope.gridData.rows[change[0]];

        //row = $scope.gridData.rows[change[0]];
        //saveGradeService.saveGrade(row.id, student_id, change[1], change[3]);
        saveGradeService.saveGrade(row.id, student_id, change, cell);
      });
    }
  };
  $scope.gridData.rows = [];
  $q.all([
    Students.one(student_id).get().then(function(data) {
      $scope.student = data;
    }),
    Grades.getList({enrollment__user: student_id}).then(function(data){
      grades = data;
    }),
    FinalGrades.getList({enrollment__user: student_id}).then(function(data){
      finalGrades = data;
    }),
    SchoolYears.getList({markingperiod__coursesection__enrollments: student_id}).then(function(data){
      years = data;
      $scope.years = years;
      angular.forEach(years, function(year){
        if (year.active_year === true) {
          selectedYear = year;
        }
      });
    }),
    Courses.getList({enrollments: student_id}).then(function(data) {
      courses = data;
    })
  ]).then(function(){
    angular.forEach($filter('orderBy')(selectedYear.markingperiod_set, 'start_date'), function(mp) {
      $scope.gridData.columns.push({
        title: mp.name,
        data: 'grade_' + mp.id,
        width: 100
      });
    });
    $scope.gridData.columns.push({
      title: 'Final',
      data: 'grade_final',
      width: 100
    });
    angular.forEach(years, function(year){
      year.courses = [];
      angular.forEach(courses, function(course) {
        angular.forEach(year.markingperiod_set, function(marking_period) {
          if (marking_period.school_year.id === year.id) {
            year.courses.push(course);
          }
        });
      });
    });

    for (var i = 0, lenI = selectedYear.courses.length; i< lenI; i++) {
      var course = selectedYear.courses[i];
      for (var j = 0, lenJ = grades.length; j < lenJ; j++) {
        var grade = grades[j];
        if (grade.course_section_id === course.id) {
          course['grade_' + grade.marking_period] = grade.grade;
        }
      }
      angular.forEach(finalGrades, function(grade) {
        if (grade.course_section_id === course.id) {
          course['grade_final'] = grade.grade;
        }
      });
      if($scope.gridData.rows.indexOf(course) == -1){
        $scope.gridData.rows.push(course);
      }
    }


  });
}]);


app.service('saveGradeService', ['$http', function($http) {
  this.saveGrade = function(course_section_id, student_id, change, cell) {
  var prop = change[1],
      newVal = change[3];
  //this.saveGrade = function(course_section_id, student_id, prop, newVal) {
    if (prop === 'grade_final') {
      data = {
        student: student_id,
        course_section: course_section_id,
        grade: newVal
      };
      $http({
        method: "POST",
        url: "/api/set_final_grade/",
        data: data
      }).success(function(data, status){
        console.log(data);
      });
    } else if (prop.substring(0, 6) === 'grade_') {
      var marking_period = prop.substring(6),
        data = {
          student: student_id,
          marking_period: marking_period,
          course_section: course_section_id,
          grade: newVal
        };
      $http({
        method: "POST",
        url: "/api/set_grade/",
        data: data
      }).success(function(data, status){
        //WE ARE SURE THAT THERE IS NO ERROR SO WE CAN ADD CLASS TO CELL
        cell.classList.add('table-is-valid');
        console.log(data);
      }).error(function(data, status, headers, config) {
        cell.classList.add('table-is-not-valid');
        console.log(data);
        console.log(status);
      });
    }
  }
}]);


app.factory('Courses', ['Restangular', function(Restangular) {
  return Restangular.service('sections');
}]);

app.factory('Grades', ['Restangular', function(Restangular) {
  return Restangular.service('grades');
}]);

app.factory('FinalGrades', ['Restangular', function(Restangular) {
  return Restangular.service('final_grades');
}]);

app.factory('Students', ['Restangular', function(Restangular) {
  return Restangular.service('students');
}]);

app.factory('SchoolYears', ['Restangular', function(Restangular) {
  return Restangular.service('school_years');
}]);
