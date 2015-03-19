angular.module('gradeBookApp.controllers')
  .controller(
  'coursesCtrl',
  [
    '$scope',
    'courseFactory',
    function ($scope,  courseFactory) {

      $scope.courses = [];

      $scope.select = {};

      $scope.years = [];

      $scope.teachers = [
        "Teacher 1", "Teacher 2", "Teacher 3"
      ];

      $scope.$watch('select.teacher',function () {
        if ($scope.select.year && $scope.select.teacher) {
          getCourses();
        }
      });

      $scope.$watch('select.year',function () {
        if ($scope.select.year && $scope.select.teacher) {
          getCourses();
        }
      });

      var createYears = function () {
        for(var i = 2000, j = 2015;  i < j; i++) {
          $scope.years.push(i);
        }
      };

      createYears();

      var getCourses = function () {
        courseFactory.get().$promise.then(
          function (result) {
            $scope.courses = result['results'];
          }
        )
      };
    }
  ]
);
