var admissionsApp = angular.module('admissions',[]);

admissionsApp.controller('StudentApplicationController', ['$scope', '$http', function($scope, $http) {
    
    $scope.application_template = {};
    $scope.applicant_field_options = [];
    $scope.applicant_integrated_fields = [];
    $scope.integratedField={};
    $scope.applicant_data = {};
    $scope.applicant_additional_information = [];
    $scope.applicationComplete = false;

    $scope.applicationNotComplete = function() {
        return !$scope.applicationComplete;
    }

    $scope.getCustomFieldById = function(field_id) {
        for (var i=0; i < $scope.applicant_field_options.length; i ++ ) {
            var field = $scope.applicant_field_options[i];
            if ( field.id == field_id ) {
                return field;
                break;
            }
        }
    };

    $scope.getCustomFieldChoices = function(field_id) {
        var custom_field = $scope.getCustomFieldById(field_id);
        if ( custom_field.is_field_integrated_with_applicant === true) {
            var integrated_field = $scope.getApplicantFieldByFieldName(custom_field.field_name);
            return integrated_field.choices;
        } else if (custom_field.is_field_integrated_with_applicant === false ) {
            if (custom_field.choices != "") {
                var choices = []
                var choice_array = custom_field.choices.split(',');
                for (i in choice_array) {
                    choices.push({
                        "display_name" : choice_array[i],
                        "value" : choice_array[i]
                    });
                }
                return choices;
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



    $scope.submitApplication = function() {
        // first collect all the values from the template:
        var sections = $scope.application_template.sections;
        for (section_id in sections) {
            var section = sections[section_id];
            for (i in section.fields) {
                var section_field = section.fields[i];
                var field = $scope.getCustomFieldById(section_field.id)
                if (field.is_field_integrated_with_applicant === true) {
                    $scope.applicant_data[field.field_name] = section_field.value;
                } else if (field.is_field_integrated_with_applicant === false) {
                    $scope.applicant_additional_information.push({
                        "custom_field" : section_field.id,
                        "answer" : section_field.value,
                    });
                }  
            }
        }
        
        // now, let's post the applicant data, and use the response to
        // post the additional information in separate requests...
        $http({
            method: "POST",
            url: "/api/applicant/",
            data: $scope.applicant_data
        }).success(function(data, status, headers, config){
            // generate a list of fields from the Applicant Django model
            var applicant_id = data.id
            for (i in $scope.applicant_additional_information) {
                // inject the applicant_id into the data 
                $scope.applicant_additional_information[i].applicant = applicant_id;
            }
            $http({
                method: "POST",
                url: "/api/applicant-additional-information/",
                data : $scope.applicant_additional_information,
            }).success(function(data, status, headers, config){
                $scope.applicationComplete = true;
            });
        }).error(function(data, status, headers, config) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(data);
        });
    };

}]);