app.controller(
  'StudentGradeReportController',
  ['$scope', '$q',
  function($scope) 
{
  $scope.student_id = 1;
  $scope.marking_period_id = 1;
}]);

app.directive('studentGradeReportWidget', 
    ['GradeReportService', function(GradeReportService) 
{
  return {
    templateUrl : staticURL('app/portal/templates/student-grade-report-widget.html'),
    link: function($scope, $element, $attrs) {
      GradeReportService.getData(
        $scope.student_id, $scope.marking_period_id
      ).then(function(sections){
        $scope.sections = sections;
      });
    }
  };
}]);

app.service('GradeReportService', ['$q', 'Restangular', function($q, Restangular) {
  this.getData = function(student_id, marking_period_id) {
    var promise = $q.all([
      Restangular.all('sections').getList({
          enrollments: student_id, 
          marking_period: marking_period_id
      }).then(function(data){
        sections = data;
      })
    ]).then(function(){
      return sections;
    });
    return promise;
  }
}]);
