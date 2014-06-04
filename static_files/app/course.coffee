app = angular.module 'angular_sis', ['restangular', 'ngRoute']

app.controller 'CourseController', ['$scope', '$routeParams', '$route', 'RestfulModel', ($scope, $routeParams, $route, RestfulModel) ->
    $scope.$on '$routeChangeSuccess', ->
        courseModel = new RestfulModel.Instance("courses")
        $scope.courses = courseModel.getList()
        courseModel.getOptions().then (options) ->
            $scope.course_options = options
        courseModel.getOne($routeParams.course_id, $scope.form).then (course) ->
            $scope.course = course
            $scope.saveCourse = course.saveForm
]

app.factory 'RestfulModel', ['Restangular', (Restangular) ->
    Instance = (name) ->
        @modelName = name
        @getOptions = ->
            Restangular.all(@modelName).options().then (options) ->
                options.actions.POST
        @getOne = (object_id, form) ->
            Restangular.one(@modelName, object_id).get().then (obj) ->
                obj.saveForm = (form_name) ->
                    obj.patch().then ((response) ->
                        form[form_name].$setValidity('server', true)
                    ), (response) ->
                        _.each response.data, (errors, key) ->
                            form[key].$dirty = true
                            form[key].$setValidity('server', false)
                            form[key].errors = errors
                obj
        @getList = ->
            console.log('FUCK LIST?')
            Restangular.all(@modelName).getList().$object

        return

    Instance: Instance
]
