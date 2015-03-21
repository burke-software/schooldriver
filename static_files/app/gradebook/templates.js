angular.module('gradeBookApp.templates', ['gradebook/gradebook.html']);

angular.module("gradebook/gradebook.html", []).run(function($templateCache, $http) {
    $http.get(static('app/gradebook/modules/gradebook/gradebook.html'), { cache: $templateCache })
});