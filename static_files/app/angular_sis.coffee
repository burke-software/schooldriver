app = angular.module("angular_sis")
app.config [
  "$httpProvider"
  ($httpProvider) ->
    $httpProvider.defaults.headers.common["X-CSRFToken"] = csrf_token
]
app.config (RestangularProvider) ->
  RestangularProvider.setBaseUrl "/api"
  RestangularProvider.setRequestSuffix "/"
  RestangularProvider.addResponseInterceptor (data, operation, what, url, response, deferred) ->
    extractedData = undefined
    if operation is "getList" && data["results"] != undefined
      extractedData = data.results
      extractedData.meta = {}
      extractedData.meta['count'] = data.count
      extractedData.meta['next'] = data.next
      extractedData.meta['previous'] = data.previous
    else
      extractedData = data
    extractedData

  return

app.config ($routeProvider, $locationProvider) ->
  $routeProvider.when "/course/course_section_grades/:course_section_id/",
    controller: "CourseGradesController"
  $routeProvider.when "/course/student_grades/:student_id/",
    templateUrl: '/static/app/partials/student_grades.html',
    controller: "StudentGradesController"
  $routeProvider.when "/course/student_grades/:student_id/:year_id/",
    templateUrl: '/static/app/partials/student_grades.html',
    controller: "StudentGradesController"
  $routeProvider.when "/schedule/course/",
    templateUrl: '/static/app/partials/course_detail.html',
    controller: "CourseController",
    reloadOnSearch: false

  $locationProvider.html5Mode true
