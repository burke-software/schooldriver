app = angular.module 'angular_sis', ['restangular', 'ngRoute', 'ui.bootstrap']

app.controller 'CourseController', ($scope, $routeParams, $route, RestfulModel) ->
    $scope.oneAtATime = false
    $scope.status =
        isFirstOpen: true
        isFirstDisabled: false
    courseModel = new RestfulModel.Instance("courses")
    sectionModel = new RestfulModel.Instance("sections")
    $scope.courses = courseModel.getList()

    $scope.$on '$routeUpdate', ->
        updateDetail()

    updateDetail = () ->
        $scope.section = null
        $scope.course = null
        if $routeParams.section_id
            sectionModel.getOptions().then (options) ->
                $scope.sectionOptions = options
            sectionModel.getOne($routeParams.section_id, $scope.sectionForm).then (obj) ->
                $scope.section = obj
                $scope.saveSection = obj.saveForm
        else 
            courseModel.getOptions().then (options) ->
                $scope.courseOptions = options
            courseModel.getOne($routeParams.course_id, $scope.form).then (obj) ->
                $scope.course = obj
                $scope.saveCourse = obj.saveForm
    updateDetail()

    $scope.resultsNext = (previous) ->
        if previous == true
            page_num = $scope.courses.meta.previous.match(/\d+$/);
        else
            page_num = $scope.courses.meta.next.match(/\d+$/);
        $scope.courses = courseModel.getList({page: page_num})


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
                    , (response) ->
                        _.each response.data, (errors, key) ->
                            form_field.isSaving = false
                            #form[key].$dirty = true
                            form[key].$setValidity('server', false)
                            form[key].errors = errors
                obj
        @getList = (query) ->
            Restangular.all(@modelName).getList(query).$object

        return

    Instance: Instance


app.directive "bscField", ->
    scope:
        fieldOptions: "="
        fieldForm: "="

    templateUrl: "/static/app/partials/field.html"
    transclude: true
