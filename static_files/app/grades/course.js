  app.controller('CourseController', function($scope, $routeParams, $route, RestfulModel) {
    var courseModel, sectionModel, updateDetail;
    $scope.oneAtATime = false;
    $scope.status = {
      isFirstOpen: true,
      isFirstDisabled: false
    };
    courseModel = new RestfulModel.Instance("courses");
    sectionModel = new RestfulModel.Instance("sections");
    $scope.courses = courseModel.getList();
    $scope.$on('$routeUpdate', function() {
      return updateDetail();
    });
    updateDetail = function() {
      $scope.section = null;
      $scope.course = null;
      if ($routeParams.section_id) {
        sectionModel.getOptions().then(function(options) {
          return $scope.sectionOptions = options;
        });
        return sectionModel.getOne($routeParams.section_id, $scope.sectionForm).then(function(obj) {
          $scope.section = obj;
          return $scope.saveSection = obj.saveForm;
        });
      } else {
        courseModel.getOptions().then(function(options) {
          return $scope.courseOptions = options;
        });
        return courseModel.getOne($routeParams.course_id, $scope.form).then(function(obj) {
          $scope.course = obj;
          return $scope.saveCourse = obj.saveForm;
        });
      }
    };
    updateDetail();
    return $scope.resultsNext = function(previous) {
      var page_num;
      if (previous === true) {
        page_num = $scope.courses.meta.previous.match(/\d+$/);
      } else {
        page_num = $scope.courses.meta.next.match(/\d+$/);
      }
      return $scope.courses = courseModel.getList({
        page: page_num
      });
    };
  });

  app.factory('RestfulModel', function(Restangular) {
    var Instance;
    Instance = function(name) {
      this.modelName = name;
      this.getOptions = function() {
        return Restangular.all(this.modelName).options().then(function(options) {
          return options.actions.POST;
        });
      };
      this.getOne = function(object_id, form) {
        return Restangular.one(this.modelName, object_id).get().then(function(obj) {
          obj.saveForm = function(form_name) {
            var form_field, patch_object;
            form_field = form[form_name];
            form_field.isSaving = true;
            form_field.isSaved = false;
            patch_object = {};
            patch_object[form_name] = form_field.$viewValue;
            return obj.patch(patch_object).then(function(response) {
              form_field.$setValidity("server", true);
              form_field.isSaving = false;
              return form_field.isSaved = true;
            }, function(response) {
              return _.each(response.data, function(errors, key) {
                form_field.isSaving = false;
                form[key].$setValidity('server', false);
                return form[key].errors = errors;
              });
            });
          };
          return obj;
        });
      };
      this.getList = function(query) {
        return Restangular.all(this.modelName).getList(query).$object;
      };
    };
    return {
      Instance: Instance
    };
  });

  app.directive("bscField", function() {
    return {
      scope: {
        fieldOptions: "=",
        fieldForm: "="
      },
      templateUrl: static('app/common/partials/field.html'),
      transclude: true
    };
  });
