app.controller(
    'CourseGradesController',
    ['$scope', '$routeParams', '$http', '$filter', '$q', 'Courses', 'Grades', 'FinalGrades',
    function($scope, $routeParams, $http, $filter, $q, Courses, Grades, FinalGrades) {
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
      angular.forEach(changes, function(change) { 
        row = $scope.gridData.rows[change[0]];
        prop = change[1];
        oldVal = change[2];
        newVal = change[3];
        if (prop === 'grade_final') {
          student = row.id;
          data = {
            student: student,
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
        }else if (prop.substring(0, 6) === 'grade_') {
          marking_period = prop.substring(6);
          student = row.id;
          data = {
            student: student,
            marking_period: marking_period,
            course_section: course_section_id,
            grade: newVal
          };
          $http({
            method: "POST",
            url: "/api/set_grade/",
            data: data
          }).success(function(data, status){
            console.log(data);
          });
        }
      });
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
    }),
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
    ['$scope', '$routeParams', '$http', '$filter', '$q', 'Students', 'SchoolYears', 'Grades', 'FinalGrades',
    function($scope, $routeParams, $http, $filter, $q, Students, SchoolYears, Grades, FinalGrades) {
  var student_id = $routeParams.student_id;
  var years;
  var selectedYear;
  $scope.gridData = {};
  $scope.gridData.columns = [{
    title: 'Course',
    readOnly: true,
    data: 'name',
    width: 100}];
  $scope.gridData.rows = [];
  $scope.htSettings = {};
  $q.all([
    Students.one(student_id).get().then(function(data) {
      $scope.student = data;
    }),
    Grades.getList({enrollment__user: student_id}).then(function(data){
      grades = data;
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
  ]).then(function(){
    angular.forEach($filter('orderBy')(selectedYear.markingperiod_set, 'start_date'), function(mp) {
      $scope.gridData.columns.push({
        title: mp.name,
        data: 'grade_' + mp.id,
        width: 100
      });
    });
     
  });
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
