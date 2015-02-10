'use strict';
angular.module('gradeBookApp', [
  'ngRoute',
  'ngResource',
  'ngCookies',
  'ui.bootstrap',
  'ngHandsontable',
  'gradeBookApp.controllers',
  'gradeBookApp.services',
  'gradeBookApp.templates'
])
  .config(
  [
    '$provide',
    '$routeProvider',
    function ($provide, $routeProvider) {
      $provide.factory('appConfig', function () {
        return {
          apiUrl: 'http://192.168.59.103:8000/api/'
        }
      });

      $routeProvider.
        when('/students/classSections',{
          controller: 'classSectionListCtrl',
          templateUrl: 'studentGrades/classSectionList/classSectionList.html'
        })
        .when('/students/classSections/:sectionId',{
          controller: 'singleSectionCtrl',
          templateUrl: 'studentGrades/singleSection/singleSection.html'
        })
        .otherwise({
          redirectTo: '/students/classSections'
        });
    }
  ]
).run(
  [
    '$http',
    '$cookies',
    function ($http,$cookies){
      $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
    }
  ]
);


angular.module('gradeBookApp.services', []);
angular.module('gradeBookApp.controllers',[]);

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

angular.module('gradeBookApp.services')
  .factory(
  'assignmentFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + '/assignments/:assignmentId/ ',
        {
          assignmentId: '@assignmentId'
        },
        {
          create: {
            method: 'POST'
          },
          update: {
            method: 'PUT'
          }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.services')
  .factory(
  'categoryFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log) {
      return $resource(appConfig.apiUrl + '/categories/ ',
        {
        },
        {
         get: {
           method: 'GET',
           isArray: true,
           interceptor: {
             responseError: function (error) {
               $log.error('GET CATEGORY LIST');
               return [
                 {
                   id: 1,
                   name: 'Category 1'
                 },
                 {
                   id: 2,
                   name: 'Category 2'
                 },
                 {
                   id: 3,
                   name: 'Category 3'
                 }
               ];
             }
           }
         }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.services')
  .factory(
  'classSectionFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log){
      return $resource(appConfig.apiUrl + '/classSection/:sectionId/ ',
        {
          sectionId: '@sectionId'
        },
        {
          getBySection: {
            method: 'GET',
            interceptor: {
              responseError: function (error) {
                $log.error('GET USER LIST WITH ASSIGNMENTS:', error);
                return {
                  id: 1,
                  assignments: [
                    {
                      id:1,
                      name: 'Quiz',
                      weight: 25,
                      category: 1
                    },
                    {
                      id: 2,
                      name: 'Midterm',
                      weight: 50,
                      category: 2
                    },
                    {
                      id: 3,
                      name: 'Project',
                      weight:15,
                      category: 3
                    }
                  ],
                  users: [
                    {
                      id: 1,
                      firstName: 'Ashor',
                      lastName: 'Lior',
                      finalGrade: 0,
                      assignments: [
                        {
                          id: 1,
                          assignmentId:1,
                          value: 26
                        },
                        {
                          id:2,
                          assignmentId:2,
                          value: 35
                        },
                        {
                          id: 3,
                          assignmentId:3,
                          value: 57
                        }
                      ]
                    },
                    {
                      id: 2,
                      firstName: 'Lianna',
                      lastName: 'Congrains',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:4,
                          assignmentId:1,
                          value: 15
                        },
                        {
                          id:5,
                          assignmentId:2,
                          value: 15
                        },
                        {
                          id: 6,
                          assignmentId:3,
                          value: 17
                        }
                      ]
                    },
                    {
                      id: 3,
                      firstName: 'Andy',
                      lastName: 'Dirkse',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:7,
                          assignmentId:1,
                          value: 35
                        },
                        {
                          id:8,
                          assignmentId:2,
                          value: 55
                        },
                        {
                          id: 9,
                          assignmentId:3,
                          value: 58
                        }
                      ]
                    },

                    {
                      id: 5,
                      firstName: 'Jacob',
                      lastName: 'Hammer',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:13,
                          assignmentId:1,
                          value: 26
                        },
                        {
                          id:14,
                          assignmentId:2,
                          value: 51
                        },
                        {
                          id: 15,
                          assignmentId:3,
                          value: 57
                        }
                      ]
                    },
                    {
                      id: 5,
                      firstName: 'Maria',
                      lastName: 'Hadrin',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 6,
                      firstName: 'Salma',
                      lastName: 'Ortega',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 14,
                      firstName: 'Vincent',
                      lastName: 'Rose',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 24,
                      firstName: 'Allen',
                      lastName: 'West',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    }
                  ]
                }
              }
            }
          },
          get: {
            method: 'GET',
            isArray: true,
            interceptor: {
              responseError: function (error) {
                $log.error('GET CLASSES AND SECTIONS:', error);
                return [
                  {
                    name: 'Algebra II',
                    sections: [
                      {
                        id: 1,
                        name: 'Period 1'
                      },
                      {
                        id: 2,
                        name: 'Period 2'
                      },
                      {
                        id:3,
                        name: 'Period 3'
                      },
                      {
                        id: 4,
                        name: 'Period 4'
                      }
                    ]
                  },
                  {
                    name: 'Algebra I',
                    sections: [
                      {
                        id: 5,
                        name: 'Period 1'
                      },
                      {
                        id: 6,
                        name: 'Period 2'
                      }
                    ]
                  },
                  {
                    name: 'Geometry 10',
                    sections: [
                      {
                        id: 7,
                        name: 'Period 1'
                      },
                      {
                        id: 8,
                        name: 'Period 2'
                      }
                    ]
                  }
                ]
              }
            }
          }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.services')
  .factory(
  'coursesFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + '/courses/:courseId/ ',
        {
          courseId: '@courseId'
        },
        {
          create: {
            method: 'POST'
          },
          update: {
            method: 'PUT'
          }
        }
      )
    }
  ]
);

/**
 * Created by jkl on 05.01.15.
 */
angular.module('gradeBookApp.services')
  .factory(
  'gradeFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + '/grades/:gradeId/ ',
        {
          gradeId: '@gradeId'
        },
        {
          create: {
            method: 'POST'

          },

          update: {
            method: 'PUT'

          }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.services')
  .factory(
  'sectionFactory',
  [
    'appConfig',
    '$resource',
    function (appConfig, $resource) {
      return $resource(appConfig.apiUrl + 'sections/:sectionId/ ',
        {
          sectionId: '@sectionId'
        },
        {
          create: {
            method: 'POST'
          },
          update: {
            method: 'PUT'
          }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.services')
  .factory(
  'studentFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log) {
      return $resource(appConfig.apiUrl + '/student/:studentId/ ',
        {
          studentId: '@studentId'
        },
        {
          update: {
            method: 'PUT'
          },
          get: {
            method: 'GET',
            interceptor: {
              responseError: function (error) {
                $log.error('GET SINGLE USER:', error);
                return {
                  id: 1,
                  firstName: 'Ashor',
                  lastName: 'Lior',
                  finalGrade: 0,
                  assignments: [
                    {
                      id: 1,
                      assignmentId:1,
                      value: 26
                    },
                    {
                      id:2,
                      assignmentId:2,
                      value: 35
                    },
                    {
                      id: 3,
                      assignmentId:3,
                      value: 57
                    }
                  ]
                }
              }
            }
          }
        }
      )
    }
  ]
);

angular.module('gradeBookApp.templates', ['studentGrades/classSectionList/classSectionList.html', 'studentGrades/singleSection/_addNewAssignment.html', 'studentGrades/singleSection/_adjustGradeSettings.html', 'studentGrades/singleSection/singleSection.html']);

angular.module("studentGrades/classSectionList/classSectionList.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("studentGrades/classSectionList/classSectionList.html",
    "<div class=\"row\"><h2>Student grades</h2></div><div class=\"row\"><h3>Please select teacher and year</h3></div><div class=\"row field\"><label class=\"inline one column year-teacher\">Year</label><div class=\"picker two columns\"><select ng-model=\"select.year\" ng-options=\"year as year for year in years\"><option value=\"\">Select year</option></select></div></div><div class=\"row field\"><label class=\"inline one column year-teacher\">Teacher</label><div class=\"picker two columns\"><select ng-model=\"select.teacher\" ng-options=\"teacher for teacher in teachers\"><option value=\"\">Select teacher</option></select></div></div><div class=\"row\" ng-if=\"select.teacher && select.year\"><h3>select a class section to edit grades</h3><table class=\"rounded\"><thead><tr><th>CLASSES</th><th>SECTIONS</th></tr></thead><tbody ng-repeat=\"classSection in classSectionList\"><tr ng-repeat=\"section in classSection.sections\"><td rowspan=\"{{classSection.sections.length}}\" ng-if=\"$index == 0\">{{classSection.name}}</td><td><a ng-href=\"#/students/classSections/{{section.id}}\">{{section.name}}</a></td></tr></tbody></table></div>");
}]);

angular.module("studentGrades/singleSection/_addNewAssignment.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("studentGrades/singleSection/_addNewAssignment.html",
    "<div class=\"modal active\"><div class=\"content\"><div class=\"modal-header\"><h2 class=\"modal-title text-center\">Add new assignment</h2></div><div class=\"modal-body\"><form class=\"form-horizontal\"><div class=\"row field\"><label class=\"inline two columns year-teacher\">Name</label><div class=\"seven columns\"><input type=\"text\" style=\"width: 100%\" class=\"input\" ng-model=\"assignment.name\" placeholder=\"enter assignment title name\"></div></div><div class=\"row field\"><label class=\"two columns inline year-teacher\">Weight</label><div class=\"seven columns\"><input type=\"text\" style=\"width: 100%\" class=\"input\" ng-model=\"assignment.weight\" placeholder=\"enter assignment weight as a percentage\"></div></div><div class=\"row\"><label class=\"two columns inline year-teacher\">Category</label><div class=\"seven columns picker\"><select class=\"form-control\" ng-model=\"assignment.category\" ng-options=\"category.id as category.name for category in categories\"><option value=\"\">Select category</option></select></div></div></form></div><div class=\"row\"><div class=\"ten columns centered text-center\"><div class=\"btn primary medium\"><a ng-click=\"ok()\">OK</a></div><div class=\"btn warning medium\"><a ng-click=\"cancel()\">Cancel</a></div></div></div></div></div>");
}]);

angular.module("studentGrades/singleSection/_adjustGradeSettings.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("studentGrades/singleSection/_adjustGradeSettings.html",
    "<div class=\"modal active\"><div class=\"content\"><div class=\"modal-header\"><h2 class=\"modal-title text-center\">Adjust grade settings</h2></div><div class=\"modal-body\"><form class=\"form-horizontal\"><div class=\"row field\" ng-repeat=\"assignment in assignments\"><label class=\"inline three columns year-teacher\">{{assignment.name}}</label><div class=\"three columns append\"><input type=\"text\" class=\"input text-right\" style=\"margin-top: -2px\" ng-model=\"assignment.weight\" placeholder=\"enter weight\"> <span class=\"adjoined\" id=\"basic-addon2\">%</span></div></div></form></div><div class=\"row\"><div class=\"ten columns centered text-center\"><div class=\"btn primary medium\"><a ng-click=\"ok()\">Save</a></div><div class=\"btn warning medium\"><a ng-click=\"cancel()\">Cancel</a></div></div></div></div></div>");
}]);

angular.module("studentGrades/singleSection/singleSection.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("studentGrades/singleSection/singleSection.html",
    "<div class=\"\"><hot-table afterchange=\"afterChange\" aftergetcolheader=\"afterGetColHeader\" rowheaders=\"true\" colheaders=\"true\" datarows=\"users\" columns=\"columns\" fixedcolumnsleft=\"3\" minsparerows=\"1\" minsparecols=\"1\"></hot-table></div><div style=\"margin-top: 20px\"><div class=\"btn primary medium\"><a ng-href=\"#/students/classSections\">View courses & sections</a></div></div>");
}]);
