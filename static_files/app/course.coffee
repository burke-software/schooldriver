app = angular.module 'angular_sis', ['restangular', 'ngRoute', 'ui.bootstrap']

app.controller 'CourseController', ($scope, $routeParams, $route, RestfulModel) ->
    $scope.oneAtATime = false
    $scope.status =
        isFirstOpen: true
        isFirstDisabled: false

    $scope.$on '$routeChangeSuccess', ->
        courseModel = new RestfulModel.Instance("courses")
        $scope.courses = courseModel.getList()
        courseModel.getOptions().then (options) ->
            $scope.courseOptions = options
        courseModel.getOne($routeParams.course_id, $scope.form).then (course) ->
            $scope.course = course
            $scope.saveCourse = course.saveForm


app.factory 'RestfulModel', (Restangular) ->
    Instance = (name) ->
        @modelName = name
        @getOptions = ->
            Restangular.all(@modelName).options().then (options) ->
                options.actions.POST
        @getOne = (object_id, form) ->
            Restangular.one(@modelName, object_id).get().then (obj) ->
                obj.saveForm = (form_name) ->
                    # save only the field that was changed.
                    form_field = form[form_name]
                    form_field.isSaving = true
                    form_field.isSaved = false
                    patch_object = {}
                    patch_object[form_name] = form_field.$viewValue
                    obj.patch(patch_object).then (response) ->
                        form_field.$setValidity "server", true
                        form_field.isSaving = false
                        form_field.isSaved = true
                    ), (response) ->
                        _.each response.data, (errors, key) ->
                            form_field.isSaving = false
                            #form[key].$dirty = true
                            form[key].$setValidity('server', false)
                            form[key].errors = errors
                obj
        @getList = ->
            Restangular.all(@modelName).getList().$object

        return

    Instance: Instance


app.directive "bscField", ->
    scope:
        fieldOptions: "="
        fieldForm: "="

    templateUrl: "/static/app/partials/field.html"
    transclude: true
