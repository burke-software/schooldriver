app = angular.module("angular_sis")
app.config [
  "$httpProvider"
  ($httpProvider) ->
    $httpProvider.defaults.headers.common["X-CSRFToken"] = csrf_token
]
app.config (RestangularProvider) ->
  RestangularProvider.setBaseUrl "/api"
  RestangularProvider.setRequestSuffix "/"

app.config ($routeProvider, $locationProvider) ->
  $routeProvider.when "/grades/course_grades/:course_id/",
    controller: "CourseGradesController"
  $routeProvider.when "/grades/student_grades/:student_id/",
    controller: "StudentGradesController"
  $routeProvider.when "/grades/student_grades/:student_id/:year_id/",
    controller: "StudentGradesController"

  $locationProvider.html5Mode true
