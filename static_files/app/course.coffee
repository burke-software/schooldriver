app = angular.module 'angular_sis', ['restangular', 'ngRoute']

app.controller 'CourseController', ['$scope', '$timeout', '$routeParams', '$route', 'Restangular', ($scope, $timeout, $routeParams, $route, Restangular) ->
    
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
        $scope.course_options = Restangular.all('courses').options().$object
]
