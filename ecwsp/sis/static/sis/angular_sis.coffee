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
  $routeProvider.when "/course/course_grades/:course_id/",
    controller: "CourseGradesController"
  $routeProvider.when "/course/student_grades/:student_id/",
    controller: "StudentGradesController"
  $routeProvider.when "/course/student_grades/:student_id/:year_id/",
    controller: "StudentGradesController"
  $routeProvider.when "/schedule/course/:course_id/",
    controller: "CourseController"

  $locationProvider.html5Mode true
