var admissionsApp = angular.module('admissions',[]);

admissionsApp.controller('ReviewApplicationsController', ['$scope', '$http', function($scope, $http) {
    
    $scope.allApplicants = [];
    $scope.applicationFields = [];
    $scope.viewAllApplicants = true;
    $scope.currentlyLoadedStudentApplication = {};
    $scope.application_template = {};

    $scope.init = function() {
        $scope.getAllApplicants();
        $scope.getApplicationTemplate();
        $scope.refreshCustomFieldList();
    };

    $scope.getAllApplicants = function() {
        $http.get("/api/applicant/")
            .success(function(data, status, headers, config) {
                $scope.allApplicants = data;
        });
    };

    $scope.showAllApplicantsAgain = function() {
        $scope.viewAllApplicants = true;
    };

    $scope.loadStudentApplication = function(applicant) {
        $scope.currentlyLoadedStudentApplication = $scope.application_template;
        $scope.populateApplicationTemplateWithStudentResponses(applicant);
        $scope.viewAllApplicants = false;
    };

    $scope.populateApplicationTemplateWithStudentResponses = function(applicant) {
        var template = $scope.currentlyLoadedStudentApplication;
        for (var section_id in template.sections) {
            var section = template.sections[section_id];
            for (var field_id in section.fields) {
                var field = section.fields[field_id];
                if (field.is_field_integrated_with_applicant == true) {
                    field.value = applicant[field.field_name];
                } else {
                    for (var i in applicant.additionals) {
                        var additional = applicant.additionals[i];
                        if (additional.custom_field == field.id) {
                            field.value = additional.answer;
                            break
                        }
                    }
                }
            }
        }
    };

    $scope.getApplicationFieldById = function(field_id) {
        for ( var i in $scope.applicationFields ) {
            var field = $scope.applicationFields[i];
            if ( field.id == field_id ) {
                return field;
                break;
            }
        }
    };

    $scope.formatApplicationTemplate = function() {
        // the application template contains a list of sections; each section
        // contains a list of field-id's. We should fetch the actual fields
        // and replace the list of field-id's with a list of actual fields
        // to save time in the DOM when interating through the sections
        var template_sections = $scope.application_template.sections;
        for (var section_id in template_sections) {
            var section = template_sections[section_id];
            for (var field_id in section.fields) {
                var section_field = section.fields[field_id];
                var custom_field = $scope.getApplicationFieldById(section_field.id);
                section.fields[field_id] = custom_field;
            }
        }
    };

    $scope.refreshCustomFieldList = function() {
        $http.get("/api/applicant-custom-field")
            .success(function(data, status, headers, config) {
                $scope.applicationFields = data;
                $scope.formatApplicationTemplate();
        });
    };

    $scope.getApplicationTemplate = function() {
        $http.get("/api/application-template/?is_default=True")
            .success(function(data, status, headers, config) {
                // data[0] returns the first default template,
                // theoretically there should only be one, but this is
                // just a failsafe incase there happens to be more than 1
                json_template = JSON.parse(data[0].json_template)
                if (!json_template.sections) {
                    $scope.application_template = {"sections" : []};
                } else {
                    $scope.application_template = json_template;
                }
        });
    };

}]);