angular.module('gradeBookApp.controllers')
  .controller(
  'singleSectionCtrl',
  [
    '$scope',
    'classSectionFactory',
    'assignmentFactory',
    'gradeFactory',
    'studentFactory',
    '$routeParams',
    '$modal',
    '$log',
    function ($scope, classSectionFactory, assignmentFactory, gradeFactory, studentFactory, $routeParams, $modal, $log) {
      $scope.sectionId = $routeParams.sectionId;

      if (!$scope.sectionId) {
        return;
      }

      $scope.originalDataSource = [];
      $scope.users = [];
      $scope.columns = [];

      $scope.afterChange = function (change, source) {
        if (source === 'loadData') {
          return;
        }
        serveChanges(change[0]);
      };

      $scope.afterGetColHeader = function (col, TH) {
        // FOR FINAL GRADE COL HEADER
        if (col === 2) {
          var adjustButton = buildButton('fa fa-wrench');
          Handsontable.Dom.addEvent(adjustButton,'click', function (e){
            adjustGradeSettings();
          });
          TH.firstChild.appendChild(adjustButton);
        }

        if (col >= staticColHeadersCount) {
          if (col === _assignmentArray.length + staticColHeadersCount) {
            var addButton = buildButton('fa fa-plus-square');
            Handsontable.Dom.addEvent(addButton,'click', function (e){
              addNewAssignment();
            });
            TH.firstChild.appendChild(addButton);
          } else {
            var deleteButton = buildButton('fa fa-minus-square');
            Handsontable.Dom.addEvent(deleteButton, 'click', function () {
              var conf = confirm('Are you sure you want to delete assignment');
              if (conf) {
                deleteAssignment(col);
              }
            });
            TH.firstChild.appendChild(deleteButton);
          }
        }

      };

      var staticColHeadersCount = 3; //firstName, lastName, finalGrade

      var adjustGradeSettings = function () {
        console.log('adjustGradeSettings');

        var modalInstance = $modal.open({
          windowClass: "modal fade in active",
          templateUrl:'studentGrades/singleSection/_adjustGradeSettings.html',
          controller: 'adjustGradeSettingsCtrl',
          resolve: {
            assignments: function () {
              return $scope.originalDataSource.assignments;
            }
          }
        });
      };

      var addNewAssignment = function () {
        console.log('addNewAssignment');

        var modalInstance = $modal.open({
          windowClass: "modal fade in active",
          templateUrl:'studentGrades/singleSection/_addNewAssignment.html',
          controller: 'addNewAssignmentCtrl'
        });

        modalInstance.result.then(
          function (assignment) {

            assignmentFactory.create(assignment).$promise.then(
              function (result) {
                // UPDATE ORIGINAL DATASOURCE
                $scope.originalDataSource.assignments.push(result);

                prepareAssignmentArray($scope.originalDataSource.assignments);

                console.log(result);
                console.log($scope.columns);
                console.log($scope.originalDataSource);
              },
              function (error) {
                $log.error('singleSectionCtrl.addNewAssignment', error);
              }
            );

          },
          function () {
            $log.info('Modal dismissed at: ' + new Date());
          }
        );
      };

      var deleteAssignment = function (column) {
        var assignmentId = _assignmentArray[column - staticColHeadersCount];
        assignmentFactory.delete({assignmentId: assignmentId}).$promise.then(
          function (result) {
            $log.log('AFTER DELETE WE SHOULD UPDATE WHOLE DATASET');
            getSection();
          },
          function (error) {
            $log.error('singleSectionCtrl.deleteAssignment:', error);
          }
        )
      };

      var buildButton = function (className) {
        //var button = document.createElement('BUTTON');
        var icon = document.createElement('i');
        icon.className = className + ' button';
        //button.appendChild(icon);
        //button.className = 'glyphicon ' + className;
        return icon;
      };

      /***
       * GET DEFAULT COLUMNS - FIRST THREE
       * @return {{data: string, title: string, readOnly: boolean}[]}
       */
      var defaultColumns = function () {
        return [
          {
            data: 'firstName',
            title: 'First Name',
            readOnly: true
          },
          {
            data: 'lastName',
            title: 'Last Name',
            readOnly: true
          },
          {
            data: 'finalGrade',
            title: 'Final Grade',
            readOnly: true
          }
        ]
      };

      /***
       * GET ORIGINAL ID FOR ASSIGNMENT BASED ON ASSIGNMENT TEMPORARY NAME
       * @param assignmentName
       * @return {Number}
       */
      var getAssignmentIndex = function (assignmentName) {
        var id = assignmentName.split('assignment_')[1];
        return parseInt(id, 10);
      };

      /***
       * UPDATE ORIGINAL DATASOURCE - TO KEEP ALL DATA UP TO DATE
       * @param studentId
       * @param studentObject
       */
      var updateOriginalDataSource = function (studentId, studentObject) {
        for (var i = 0, len = $scope.originalDataSource.length; i < len;i++) {
          var student = $scope.originalDataSource[i];
          if (student.id === studentId) {
            student = studentObject;
            break;
          }
        }
      };

      /***
       * UPDATE DATASOURCE WHICH IS MAIN SOURCE FOR HANDSONTABLE
       * @param studentId
       * @param studentObject
       */
      var updateTransformedDataSource = function (studentId, studentObject) {
        for (var i = 0, len = $scope.users.length; i < len;i++) {
          if ($scope.users[i].id === studentId) {
            $scope.users[i] = studentObject;
            break;
          }
        }
      };

      /***
       * GET SINGLE STUDENT AFTER UPDATE
       * @param studentId
       */
      var getSingleStudent = function (studentId) {
        studentFactory.get({studentId: studentId}).$promise.then(
          function (result) {
            //console.log(result);
            updateOriginalDataSource(studentId, result);
            var transformedStudent = prepareSingleStudent(result);
            updateTransformedDataSource(studentId, transformedStudent);
          },
          function (error) {
            $log.error('singleSectionCtrl.getSingleStudent', error);
          }
        )
      };

      /***
       * UPDATE SINGLE GRADE IN ASSIGNMENT
       * Make update request to backend
       * @param assignment
       * @param studentId
       */
      var updateGrade = function (item, studentId) {
        gradeFactory.update({gradeId: item.id},item).$promise.then(
          function (result) {
            console.log(result);
            getSingleStudent(studentId);
          },
          function (error) {
            $log.error('singleSectionCtrl.updateGrade', error);
          }
        );
      };

      var addGrade = function (item, studentId) {
        gradeFactory.create(item).$promise.then(
          function (result) {
            console.log(result);
            getSingleStudent(studentId);
          },
          function (error) {
            $log.error('singleSectionCtrl.addGrade', error);
          }
        )
      };

      /***
       * SERVE CHANGES
       * Fire all methods after cell change
       * @param change
       */
      var serveChanges = function (change) {
        console.log('serveChange');
        var userIndex = change[0],
            assignmentIndex = getAssignmentIndex(change[1]),
            oldValue = change[2],
            newValue = change[3];

        console.log(oldValue);
        console.log(newValue);
        if(oldValue != newValue) {
          var user = $scope.originalDataSource.users[userIndex];

          if (oldValue === undefined) {
            var entry = {
              assignmentId: assignmentIndex,
              value: parseInt(newValue,10)
            };
            addGrade(entry, user.id);
          } else {
            for (var i = 0, len = user.assignments.length; i < len; i++) {
              if (user.assignments[i].assignmentId === assignmentIndex) {
                var assignment =  user.assignments[i];
                assignment.value = parseInt(newValue,10);
                updateGrade(assignment, user.id);
                break;
              }
            }
          }

        }
      };

      var _assignmentArray = [];

      /***
       * PREPARE STUDENT FROM ORIGINAL DATASOURCE TO TRANSFORMED ONE
       * @param user
       * @return {{id: *, firstName: (*|.get.interceptor.responseError.firstName|.getBySection.interceptor.responseError.firstName), lastName: (*|.get.interceptor.responseError.lastName|.getBySection.interceptor.responseError.lastName), finalGrade: (*|.get.interceptor.responseError.finalGrade|.getBySection.interceptor.responseError.finalGrade)}}
       */
      var prepareSingleStudent = function (user) {
        var newUser = {
          id:user.id,
          firstName: user.firstName,
          lastName: user.lastName,
          finalGrade: user.finalGrade
        };

        var userAssignments = user.assignments;

        for (var a = 0, aLen = _assignmentArray.length; a < aLen; a++) {
          var _assignmentId = _assignmentArray[a];

          for(var u = 0, uLen = userAssignments.length; u < uLen; u++) {
            if (userAssignments[u].assignmentId === _assignmentId) {
              newUser['assignment_' + _assignmentId] = userAssignments[u].value;
            }
          }
        }
        //console.log(newUser);
        return newUser;
      };

      /***
       * PREPARE ARRAY OF ASSIGNMENTS
       * To keep all assignments in order. Required for correct headers render
       * @param assignments
       */
      var prepareAssignmentArray = function (assignments) {
        _assignmentArray = [];
        var _columns = defaultColumns();

        for (var i = 0, len = assignments.length; i < len; i++) {
          _assignmentArray.push(assignments[i].id);

          _columns.push({
            data: 'assignment_' +  assignments[i].id,
            title: assignments[i].name
          })
        }

        _columns.push({
          title: 'Add new assignment',
          readOnly: true
        });

        $scope.columns = _columns;
      };

      var prepareAssignments = function (result) {
        $scope.originalDataSource = result;
        prepareAssignmentArray(result.assignments);

        for (var i = 0, len = result.users.length; i<len;i++) {
          $scope.users.push(prepareSingleStudent(result.users[i]));
        }
      };

      /***
       * GET SECTION
       * Get list of all students for section with assignments
       */
      var getSection = function () {
        console.log('getSection');
        classSectionFactory.getBySection({sectionId: $scope.sectionId}).$promise.then(
          function (result) {
            console.log(result);
            $scope.users = [];
            prepareAssignments(result);
          },
          function (error) {
            $log.error('singleSectionCtrl:getSection', error);
          }
        )
      };

      getSection();
    }
  ]
).controller(
  'adjustGradeSettingsCtrl',
  [
    '$scope',
    '$modalInstance',
    'assignments',
    function ($scope, $modalInstance,assignments) {

      $scope.assignments = assignments;
      console.log(assignments);

      $scope.ok = function () {
        $modalInstance.close();
      };

      $scope.cancel = function () {
        $modalInstance.dismiss();
      };
    }
  ]
).controller(
  'addNewAssignmentCtrl',
  [
    '$scope',
    'categoryFactory',
    '$modalInstance',
    function ($scope, categoryFactory, $modalInstance) {

      $scope.assignment = {};

      $scope.categories = [];

      var getCategories = function () {
        categoryFactory.get().$promise.then(
          function (result) {
            $scope.categories = result;
          },
          function (error) {

          }
        )
      };

      getCategories();

      $scope.ok = function () {
        console.log($scope.assignment);
        $modalInstance.close($scope.assignment);
      };

      $scope.cancel = function () {
        $modalInstance.dismiss();
      };
    }
  ]
);
