angular.module('gradeBookApp.controllers')
  .controller(
  'classSectionListCtrl',
  [
    '$scope',
    'classSectionFactory',  // <- REMOVE
    'sectionFactory',
    '$log',
    function ($scope, classSectionFactory, sectionFactory,$log) {

      $scope.classSectionList = [];

      $scope.select = {};

      $scope.years = [];

      $scope.teachers = [
        "Teacher 1", "Teacher 2", "Teacher 3"
      ];

      $scope.$watch('select.teacher',function () {
        if ($scope.select.year && $scope.select.teacher) {
          getClassSectionList();
        }
      });

      $scope.$watch('select.year',function () {
        if ($scope.select.year && $scope.select.teacher) {
          getClassSectionList();
        }
      });

      var createYears = function () {
        for(var i = 2000, j = 2015;  i < j; i++) {
          $scope.years.push(i);
        }
      };

      createYears();

      var getClassSectionList = function () {
        sectionFactory.get().$promise.then(
          function (result) {
            console.log(result);
          }
        );

        //classSectionFactory.get().$promise.then(
        //  function (result){
        //    $scope.classSectionList = result;
        //  },
        //  function (error) {
        //    $log.error('classSectionListCtrl:getClassSectionList', error);
        //  }
        //)
      };


    }
  ]
);
