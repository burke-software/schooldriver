var admissionsApp = angular.module('admissions',['pascalprecht.translate']);

admissionsApp.config(['$translateProvider', function ($translateProvider) {
    $translateProvider.useUrlLoader('/api/translations/admissions');
    $translateProvider.preferredLanguage('en');
}]);

admissionsApp.controller('StudentApplicationController', ['$scope', '$http', '$translate', function($scope, $http, $translate) {
    
    $scope.changeLanguage = function(key) {
        $translate.use(key);
      };

    $scope.application_template = {};
    $scope.applicationFields = [];
    $scope.applicantIntegratedFields = [];
    $scope.integratedField={};
    $scope.applicant_data = {};
    $scope.applicant_additional_information = [];
    $scope.applicationComplete = false;
    $scope.submissionError = {
        "status" : false,
        "errors" : []
    }

    $scope.applicationNotComplete = function() {
        return !$scope.applicationComplete;
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

    $scope.getApplicationFieldByFieldName = function(field_name) {
        for ( var i in $scope.applicationFields ) {
            var field = $scope.applicationFields[i];
            if ( field.field_name == field_name ) {
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
                custom_field.choices = $scope.getApplicationFieldChoices(section_field.id);
                section.fields[field_id] = custom_field;
            }
        }
    };

    $scope.getApplicationFieldChoices = function(field_id) {
        var custom_field = $scope.getApplicationFieldById(field_id);
        if ( custom_field.is_field_integrated_with_applicant === true) {
            var integrated_field = $scope.getApplicantFieldByFieldName(custom_field.field_name);
            return integrated_field.choices;
        } else if (custom_field.is_field_integrated_with_applicant === false ) {
            if (custom_field.field_choices != "") {
                var choices = []
                var choice_array = custom_field.field_choices.split(',');
                for (var i in choice_array) {
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
        for (var i=0; i < $scope.applicantIntegratedFields.length; i ++ ) {
            var field = $scope.applicantIntegratedFields[i];
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
                $scope.applicationFields = data;
                $scope.formatApplicationTemplate();
        });
    };

    $scope.init = function() {
        // clean the submission errors for now
        $scope.submissionError.errors = [];

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

        $scope.refreshCustomFieldList();

        $http({
            method: "OPTIONS",
            url: "/api/applicant/",
        }).success(function(data, status, headers, config){
            // generate a list of fields from the Applicant Django model
            var integrated_fields = data.actions.POST;
            for (var field_name in integrated_fields) {
                var field = integrated_fields[field_name];
                $scope.applicantIntegratedFields.push({
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


    $scope.customErrorMessages = {
        "bday" : "Data has wrong format. Please use a valid date in the format YYYY-MM-DD",
    }


    $scope.submitApplication = function() {
        // first collect all the values from the template:
        var sections = $scope.application_template.sections;
        for (var section_id in sections) {
            var section = sections[section_id];
            for (var i in section.fields) {
                var field = section.fields[i];
                if (field.is_field_integrated_with_applicant === true) {
                    $scope.applicant_data[field.field_name] = field.value;
                } else if (field.is_field_integrated_with_applicant === false) {
                    $scope.applicant_additional_information.push({
                        "custom_field" : field.id,
                        "answer" : field.value,
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
            $scope.submissionError.status = true;
            for ( var i in data ) {
                var field = $scope.getApplicationFieldByFieldName(i);
                if ( field && data[i] ) {
                    var error_msg = data[i][0]
                    if ( field.field_name in $scope.customErrorMessages) {
                        error_msg = $scope.customErrorMessages[field.field_name];
                    }
                    var error = {
                        "field_label" : field.field_label,
                        "error_msg" : error_msg
                    };
                    $scope.submissionError.errors.push(error);
                }
            };

        });
    };

}]);