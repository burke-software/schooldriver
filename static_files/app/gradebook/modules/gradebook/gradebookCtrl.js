angular.module('gradeBookApp.controllers')
.controller(
  'gradeBookCtrl',
  [
    '$scope',
    'courseFactory',
    'assignmentCategoryFactory',
    'assignmentFactory',
	  'assignmentTypeFactory',
	  'benchmarkFactory',
    'schoolYearFactory',
    'sectionFactory',
    '$log',
    function ($scope, courseFactory, assignmentCategoryFactory, assignmentFactory, assignmentTypeFactory, benchmarkFactory, schoolYearFactory, sectionFactory, $log) {

	    /***
	     * GET LIST OF COURSES
	     */
      var getCourses = function () {
        courseFactory.get().$promise.then(
          function (result) {
            $scope.courses = result['results'];
          }
        )
      };

	    /***
	     * GET LIST OF CATEGORIES
	     */
      var getCategoryList = function () {
	      assignmentCategoryFactory.get().$promise.then(
		        function (result) {
              $scope.assignmentCategories = result;
            }
        )
      };


	    /***
	     * GET LIST OF ASSIGNMENT TYPES
	     */
	    var getAssignmentTypeList = function () {
		    assignmentTypeFactory.get().$promise.then(
				    function (result) {
					    $scope.assignmentTypes = result;
				    }
		    )
	    };

	    /***
	     * GET BENCHMARK LIST
	     */
	    var getBenchmarkList = function () {
		    benchmarkFactory.get().$promise.then(
				    function (result) {
					    $scope.benchmarkList = result;
				    }
		    )
	    }

      var hideRightColumn = function () {
        $scope.filtersVisible = false;
        $scope.settingsVisible = false;
        $scope.assignmentVisible = false;
        $scope.notificationVisible = false;
        $scope.colorGuideVisible = false;
        $scope.notificationType = null;
      };

	    /***
	     * GET ACTIVE MARKING PERIOD
	     */
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

	    var dateToYMD = function (date) {
		    var d = date.getDate();
		    var m = date.getMonth() + 1;
		    var y = date.getFullYear();
		    return '' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);
	    };

	    /***
	     * GET SECTION BY SECTION ID
	     * @param sectionId
	     */
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

	    /***
	     * SAVE ASSIGNMENT
	     */
      $scope.saveAssignment = function () {

				$scope.newAssignment.course_section = $scope.activeSection;

        assignmentFactory.create($scope.newAssignment).$promise.then(
          function (result) {
            console.log(result);
	          $scope.newAssignment = {};
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
	    getCategoryList();
	    getAssignmentTypeList();
	    getBenchmarkList();
      getActiveMarkingPeriod();

    }
  ]
);
