var admissionsApp = angular.module('admissions',['ngRoute']);

admissionsApp.config([
    '$routeProvider',  '$locationProvider',
    function($routeProvider, $locationProvider) {
        $routeProvider
            .when('/admissions/application/:applicantId/', {
                controller: 'ReviewStudentApplicationController',
                templateUrl: '/static/app/partials/review_application.html',
            });
        $locationProvider.html5Mode(true).hashPrefix('!');
}]);

admissionsApp.controller('ReviewStudentApplicationController', [
    '$scope', '$route', '$routeParams', '$http',
    function($scope, $route, $routeParams, $http) {
        $scope.$routeParams = $routeParams;
        $scope.applicationTemplate = {};
        $scope.applicationFields = [];
        $scope.submissionDate = "";
        

        $scope.init = function() {
            $scope.getDefaultApplicationTemplate();
        };

        $scope.getDefaultApplicationTemplate = function() {
            $http.get("/api/application-template/?is_default=True")
                .success(function(data, status, headers, config) {
                    // data[0] returns the first default template,
                    // theoretically there should only be one
                    var jsonTemplate = JSON.parse(data[0].json_template)
                    $scope.applicationTemplate = jsonTemplate;
                    $scope.refreshCustomFieldList();
            });
        };

        $scope.refreshCustomFieldList = function() {
            $http.get("/api/applicant-custom-field/")
                .success(function(data, status, headers, config) {
                    $scope.applicationFields = data;
                    $scope.formatApplicationTemplate();
                    var applicantId = $scope.$routeParams.applicantId;
                    var url = "/api/applicant/" + applicantId + "/";
                    $http.get(url)
                        .success(function(data, status, headers, config) {
                            $scope.applicantData = data;
                            $scope.populateApplicationTemplateWithStudentResponses(data);
                    });
            });
        };

        $scope.formatApplicationTemplate = function() {
            // the application template contains a list of sections; each section
            // contains a list of field-id's. We should fetch the actual fields
            // and replace the list of field-id's with a list of actual fields
            // to save time in the DOM when interating through the sections
            var template_sections = $scope.applicationTemplate.sections;
            for (var section_id in template_sections) {
                var section = template_sections[section_id];
                for (var field_id in section.fields) {
                    var section_field = section.fields[field_id];
                    var custom_field = $scope.getApplicationFieldById(section_field.id);
                    section.fields[field_id] = custom_field;
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

        $scope.populateApplicationTemplateWithStudentResponses = function(applicantData) {
            var template = $scope.applicationTemplate;
            var studentResponses = applicantData;
            for (var section_id in template.sections) {
                var section = template.sections[section_id];
                for (var field_id in section.fields) {
                    var field = section.fields[field_id];
                    if ( field.is_field_integrated_with_applicant == true ) {
                        field.value = studentResponses[field.field_name];
                    } else {
                        for (var i in studentResponses.additionals) {
                            var additional = studentResponses.additionals[i];
                            if (additional.custom_field == field.id) {
                                if ( field.field_type == 'emergency_contact' ) {
                                    var pythonUnicodeString = additional.answer;
                                    if (pythonUnicodeString) {
                                        var escapedString = pythonUnicodeString.replace(/u'(?=[^:]+')/g, "'");
                                        escapedString = escapedString.replace(/'/g,'"');
                                        field.value = JSON.parse(escapedString); 
                                    }
                                } else {
                                    field.value = additional.answer;
                                }
                                break
                            }
                        }
                    }
                }
            }
        };
        
        
}]);