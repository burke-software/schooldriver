app.controller('ViewStudentController', 
  ['$scope', '$routeParams', '$route', 'Students', 'CurrentEnrollments', 
  function($scope, $routeParams, $route, Students, CurrentEnrollments) {
  
  var student_id = $routeParams.student_id;

  Students.one(student_id).get().then(function(data) {
    $scope.student = data;

    // View student only requires the primary cohort, so let's filter
    var allCohorts = data.cohorts;
    for (var i=0; i<allCohorts.length; i++) {
      if (allCohorts[i].primary) {
        $scope.primaryCohort = allCohorts[i];
      }
    }
  });

  CurrentEnrollments.getList({'user':student_id}).then(function(data) {
     $scope.enrollments = data;
  });
  
}]);

app.factory('Students', ['Restangular', function(Restangular) {
  return Restangular.service('students');
}]);


app.factory('CurrentEnrollments', ['Restangular', function(Restangular) {
  return Restangular.service('enrollments');
}]);
