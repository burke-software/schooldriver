app.controller('ViewStudentController', 
  ['$scope', '$routeParams', '$route', 'Students', 
  function($scope, $routeParams, $route, Students) {
    var student_id = $routeParams.student_id;

  Students.one(student_id).get().then(function(data) {
    $scope.student = data;
  });
  
}]);


app.factory('Students', ['Restangular', function(Restangular) {
  return Restangular.service('students');
}]);