app = angular.module 'angular_sis', ['restangular', 'ngRoute']

app.controller 'CourseController', ['$scope', '$timeout', '$routeParams', '$route', 'Restangular', 'RestfulModel', ($scope, $timeout, $routeParams, $route, Restangular, RestfulModel) ->
    
    $scope.errorMessage = (name) ->
        return errors[name]
    errors = {}
    
    $scope.$on '$routeChangeSuccess', ->
        Restangular.one('courses', $routeParams.course_id).get().then (course) ->
            $scope.course = course
            $scope.saveCourse = (form_name) ->
                course.patch().then ((response) ->
                    $scope.form[form_name].$setValidity('server', true)
                    errors = {}
                ), (response) ->
                    errors = response.data
                    _.each response.data, (errors, key) ->
                        $scope.form[key].$dirty = true
                        $scope.form[key].$setValidity('server', false)

        $scope.courses = Restangular.all('courses').getList().$object
        course_model = new RestfulModel.Instance("courses")
        course_model.get_options().then (options) ->
            $scope.course_options = options
]

app.factory 'RestfulModel', ['Restangular', (Restangular) ->
    Instance = (name) ->
        @model_name = name
        @get_options = ->
            Restangular.all(@model_name).options().then (options) ->
                options.actions.POST
        @get_one = (object_id) ->
            console.log('to do')
        return

    # return these
    Instance: Instance
]
