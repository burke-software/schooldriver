var app = angular.module("angular_sis", ['restangular', 'ngRoute', 'ui.bootstrap', 'ngHandsontable', 'gradeBookApp']);

if (typeof csrf_token !== 'undefined') {
    app.config([
        "$httpProvider", function($httpProvider) {
          return $httpProvider.defaults.headers.common["X-CSRFToken"] = csrf_token;
        }
    ]);
}

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

function staticURL(path) {
    /* Works like django static files - adds the static path */
    var STATIC_URL = window.STATIC_URL || 'static';

    //if (typeof STATIC_URL !== 'undefined') {
    //    var STATIC_URL = 'static';
    //}
    return STATIC_URL + path;
}

app.config(function($routeProvider, $locationProvider) {
    $routeProvider.when("/course/course_section/:course_section_id/grades/", {
      templateUrl: staticURL('app/grades/course_grades.html'),
      controller: "CourseGradesController"
    });
    $routeProvider.when("/course/student/:student_id/grades/", {
      templateUrl: staticURL('app/grades/student_grades.html'),
      controller: "StudentGradesController"
    });
    $routeProvider.when("/course/student/:student_id/grades/:year_id/", {
      templateUrl: staticURL('app/grades/student_grades.html'),
      controller: "StudentGradesController"
    });
    $routeProvider.when("/schedule/course/", {
      templateUrl: staticURL('app/common/partials/course_detail.html'),
      controller: "CourseController",
      reloadOnSearch: false
    });
    $routeProvider.when('/admissions/application/:applicantId/', {
      templateUrl: staticURL('app/admissions/review-application.html'),
      controller: 'ReviewStudentApplicationController',
    });
    $routeProvider.when('/admissions/application', {
      templateUrl: staticURL('app/admissions/student-application.html'),
      controller: 'StudentApplicationController',
    });
    return $locationProvider.html5Mode(true);
});
