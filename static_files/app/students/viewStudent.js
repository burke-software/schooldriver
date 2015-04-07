app.controller('ViewStudentController', 
  ['$scope', '$routeParams', '$route', 'Students', 
  function($scope, $routeParams, $route, Students) {
  
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
  
}]);

app.factory('Students', ['Restangular', function(Restangular) {
  return Restangular.service('students');
}]);
