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

app.filter('phoneType', function () {
  return function(input) {
    input = input || '';
    var out = input;
    if (input === "H") {
      out = "home";
    } else if (input === "C") {
      out = "cell";
    } else if (input === "W") {
      out = "work";
    } else if (input === "O") {
      out = "other";
    }
    return out;
  };
});

app.filter('sex', function () {
  return function(input) {
    input = input || '';
    var out = input;
    if (input === "M") {
      out = "Male";
    } else if (input === "F") {
      out = "Female";
    }
    return out;
  };
});

app.factory('Students', ['Restangular', function(Restangular) {
  return Restangular.service('students');
}]);
