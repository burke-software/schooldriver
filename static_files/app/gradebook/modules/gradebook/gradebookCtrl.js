angular.module('gradeBookApp.controllers')
.controller(
  'gradeBookCtrl',
  [
    '$scope',
    'courseFactory',
    'assignmentFactory',
    'schoolYearFactory',
    'sectionFactory',
    '$log',
    function ($scope, courseFactory, assignmentFactory, schoolYearFactory, sectionFactory, $log) {

      var getCourses = function () {
        courseFactory.get().$promise.then(
          function (result) {
            $scope.courses = result['results'];
          }
        )
      };

      var hideRightColumn = function () {
        $scope.filtersVisible = false;
        $scope.settingsVisible = false;
        $scope.assignmentVisible = false;
        $scope.notificationVisible = false;
        $scope.colorGuideVisible = false;
        $scope.notificationType = null;
      };

      var getActiveMarkingPeriod = function () {
        schoolYearFactory.get().$promise.then(
          function (result){
            for (var i = 0, len = result.length; i < len; i++) {
              if (result[i].active_year){
                $scope.markingPeriodSet = result[i].markingperiod_set;
                break;
              }
            }
          }
        )
      };

      $scope.getSection = function (sectionId) {
        $scope.activeSection = sectionId;
        sectionFactory.get({sectionId: sectionId}).$promise.then(
          function (result) {
            $scope.sectionSelected = true;
            console.log(result);
            $scope.section = result;
          },
          function (error) {
            $log.error('singleSectionCtrl:getSection', error);
            $scope.sectionSelected = false;
          }
        )
      };

      $scope.sectionSelected = false;

      $scope.section = {};

      $scope.newAssignment = {};

      $scope.markingPeriodSet = [];

      $scope.saveAssignment = function () {
        assignmentFactory.create($scope.newAssignment).$promise.then(
          function (result) {
            console.log(result);
            hideRightColumn();
          }
        )
      };

      $scope.notificationType = null;
      $scope.filtersVisible = false;
      $scope.settingsVisible = false;
      $scope.assignmentVisible = false;
      $scope.multipleAssignments = false;
      $scope.notificationVisible = false;
      $scope.colorGuideVisible = false;


      $scope.search = {
        where: 'all',
        what: null
      };

      $scope.activeSection = null;

      $scope.settings = {};

      $scope.settings.colorHeaders = {};

      $scope.setSearchRange = function (value) {
        $scope.search.where = value;
      };

      $scope.cancel = function () {
        hideRightColumn();
      };

      $scope.toggleFilter = function () {
        hideRightColumn();
        $scope.filtersVisible = true;
      };

      $scope.toggleSettings = function () {
        hideRightColumn();
        $scope.settingsVisible = true;
      };

      $scope.toggleAssignments = function (readOnly) {
        $scope.readOnly = readOnly;
        hideRightColumn();
        $scope.assignmentVisible = true;
      };

      $scope.showMultipleAssignments = function (multiple) {
        $scope.multipleAssignments = multiple;
      };

      $scope.editAssignment = function () {
        $scope.readOnly = false;
        hideRightColumn();
        $scope.assignmentVisible = true;
      };

      $scope.showIconsGuide = function () {
        hideRightColumn();
        $scope.colorGuideVisible = true;
      };

      $scope.showNotificationDescription = function (notificationType) {
        hideRightColumn();
        $scope.notificationType = notificationType;
        $scope.notificationVisible = true;
      };


      getCourses();
      getActiveMarkingPeriod();

    }
  ]
);
