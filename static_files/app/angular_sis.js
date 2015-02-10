var app = angular.module("angular_sis", ['restangular', 'ngRoute', 'ui.bootstrap', 'ngHandsontable', 'gradeBookApp']);

app.config([
    "$httpProvider", function($httpProvider) {
      return $httpProvider.defaults.headers.common["X-CSRFToken"] = csrf_token;
    }
]);

app.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl("/api");
    RestangularProvider.setRequestSuffix("/");
    RestangularProvider.addResponseInterceptor(function(data, operation, what, url, response, deferred) {
      var extractedData;
      extractedData = void 0;
      if (operation === "getList" && data["results"] !== void 0) {
        extractedData = data.results;
        extractedData.meta = {};
        extractedData.meta['count'] = data.count;
        extractedData.meta['next'] = data.next;
        extractedData.meta['previous'] = data.previous;
      } else {
        extractedData = data;
      }
      return extractedData;
    });
});

function static(path) {
    /* Works like django static files - adds the static path */
    return STATIC_URL + path;
}

app.config(function($routeProvider, $locationProvider) {
    $routeProvider.when("/course/course_section_grades/:course_section_id/", {
      controller: "CourseGradesController"
    });
    $routeProvider.when("/course/student_grades/:student_id/", {
      templateUrl: static('app/grades/student_grades.html'),
      controller: "StudentGradesController"
    });
    $routeProvider.when("/course/student_grades/:student_id/:year_id/", {
      templateUrl: static('app/grades/student_grades.html'),
      controller: "StudentGradesController"
    });
    $routeProvider.when("/schedule/course/", {
      templateUrl: static('app/common/partials/course_detail.html'),
      controller: "CourseController",
      reloadOnSearch: false
    });
    $routeProvider.when('/admissions/application/:applicantId/', {
      templateUrl: static('app/admissions/review-application.html'),
      controller: 'ReviewStudentApplicationController',
    });
    $routeProvider.when('/admissions/application', {
      templateUrl: static('app/admissions/student-application.html'),
      controller: 'StudentApplicationController',
    });
    return $locationProvider.html5Mode(true);
});
