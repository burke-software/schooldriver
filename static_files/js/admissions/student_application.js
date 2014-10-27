var admissionsApp = angular.module('admissions',[]);

admissionsApp.controller('StudentApplicationController', ['$scope', '$http', function($scope, $http) {
    
    $scope.application_template = {};
    $scope.applicant_field_options = [];
    $scope.applicant_integrated_fields = [];
    $scope.integratedField={};
    $scope.is_custom_field_new = true;
    $scope.custom_field_current_id = null;

    $scope.customField = {
        "custom_option" : "custom",
        "is_field_integrated_with_applicant" : false,
        "field_choices" : "",
        "field_type" : "",
        "field_name" : "",
        "field_label": "",
        "helptext" : ""
    };

    $scope.getCustomFieldById = function(field_id) {
        for (var i=0; i < $scope.applicant_field_options.length; i ++ ) {
            var field = $scope.applicant_field_options[i];
            if ( field.id == field_id ) {
                return field;
                break;
            }
        }
    };

    $scope.getApplicantFieldByFieldName = function(field_name) {
        for (var i=0; i < $scope.applicant_integrated_fields.length; i ++ ) {
            var field = $scope.applicant_integrated_fields[i];
            if ( field.name == field_name ) {
                return field;
                break;
            }
        }
    };

    // we need to map django field types to html field types
    $scope.get_html_input_type = function(django_type) {
        if ( django_type == 'choice' ) {
            return 'multiple';
        } else {
            return 'input';
        }
    };

    $scope.refreshCustomFieldList = function() {
        $http.get("/api/applicant-custom-field")
            .success(function(data, status, headers, config) {
                $scope.applicant_field_options = data;
        });
    };

    $scope.init = function() {
        $http.get("/api/application-template/1/")
            .success(function(data, status, headers, config) {
                json_template = JSON.parse(data.json_template)
                if (!json_template.sections) {
                    $scope.application_template = {"sections" : []};
                } else {
                    $scope.application_template = json_template;
                }
        });

        $scope.refreshCustomFieldList();

        $http({
            method: "OPTIONS",
            url: "/api/applicant/",
        }).success(function(data, status, headers, config){
            // generate a list of fields from the Applicant Django model
            var integrated_fields = data.actions.POST;
            for (var field_name in integrated_fields) {
                var field = integrated_fields[field_name];
                $scope.applicant_integrated_fields.push({
                    "name" : field_name, 
                    "required" : field.required,
                    "label" : field.label,
                    "type" : field.field_type,
                    "choices" : field.choices,
                    "max_length" : field.max_length,
                });
            };  
        });
    };

}]);