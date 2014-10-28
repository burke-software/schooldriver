var admissionsApp = angular.module('admissions',[]);

admissionsApp.controller('ReviewApplicationsController', ['$scope', '$http', function($scope, $http) {
    
    $scope.allApplicants = [];

    $scope.init = function() {
        $scope.getAllApplicants();
        $scope.getApplicationTemplate();
    };

    $scope.getAllApplicants = function() {
        $http.get("/api/applicant/")
            .success(function(data, status, headers, config) {
                $scope.allApplicants = data;
                console.log(data);
        });
    };

    $scope.loadStudentApplication = function() {
        // need to implement this
    };

    $scope.getApplicationTemplate = function() {
        $http.get("/api/application-template/1/")
            .success(function(data, status, headers, config) {
                json_template = JSON.parse(data.json_template)
                if (!json_template.sections) {
                    $scope.application_template = {"sections" : []};
                } else {
                    $scope.application_template = json_template;
                }
        });
    };

}]);