app.controller('StudentApplicationController', ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {

    $scope.application_template = {};
    $scope.applicationFields = [];
    $scope.applicantIntegratedFields = [];
    $scope.integratedField={};
    $scope.applicant_data = {};
    $scope.applicant_additional_information = [];
    $scope.applicationComplete = false;
    $scope.submitSaveInProgress = false;
    $scope.applicantForeignKeyFieldChoices = {};
    $scope.submissionError = {
        "status" : false,
        "errors" : []
    };
    $scope.stateOptions = [];

    $scope.monthOptions = [
        {value: '01', display_name: "January"},
        {value: '02', display_name: "February"},
        {value: '03', display_name: "March"},
        {value: '04', display_name: "April"},
        {value: '05', display_name: "May"},
        {value: '06', display_name: "June"},
        {value: '07', display_name: "July"},
        {value: '08', display_name: "August"},
        {value: '09', display_name: "September"},
        {value: '10', display_name: "October"},
        {value: '11', display_name: "November"},
        {value: '12', display_name: "December"},
    ];

    $scope.dayOptions = [];

    $scope.populateDayOptions = function() {
        for (var i=1; i <= 31; i++) {
            var dayNum = i.toString();
            if ( i < 10 ) {
                dayNum = "0" + dayNum;
            }
            $scope.dayOptions.push(dayNum);
        }
    };

    $scope.yearOptions = [];

    $scope.populateYearOptions = function() {
        for (var i=1970; i <= 2014; i++) {
            var yearNum = i.toString();
            $scope.yearOptions.push(yearNum);
        }
    };


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
                custom_field.field_type = $scope.getCorrectFieldType(custom_field);
                if ( !custom_field.field_name ) {
                    custom_field.field_name = "custom_field_" + custom_field.id;
                }
                section.fields[field_id] = custom_field;
            }
        }
    };

    $scope.getCorrectFieldType = function(custom_field) {
        // the field type is assumed to be "input"; if it is an integrated
        // field, check the related field type and return 'data' or 'multiple'
        // if it is a date or choice type applicant field.
        var fieldType = 'input';
        if (custom_field.is_field_integrated_with_applicant === true) {
            var relatedField = $scope.getApplicantFieldByFieldName(custom_field.field_name);
            if ( relatedField.type == 'date' ) {
                fieldType = 'date';
            } else if ( relatedField.type in ['choice', 'field']) {
                fieldType = 'multiple';
            } else if (custom_field.choices && custom_field.choices.length > 0 ) {
                fieldType = 'multiple';
            }
        } else {
            fieldType = custom_field.field_type;
        }
        return fieldType;
    };

    $scope.getApplicationFieldChoices = function(field_id) {
        var custom_field = $scope.getApplicationFieldById(field_id);
        if ( custom_field.is_field_integrated_with_applicant === true) {
            var integrated_field = $scope.getApplicantFieldByFieldName(custom_field.field_name);
            if (integrated_field.name in $scope.applicantForeignKeyFieldChoices) {
                return $scope.applicantForeignKeyFieldChoices[integrated_field.name];
            } else {
                return integrated_field.choices;
            }
        } else if (custom_field.is_field_integrated_with_applicant === false ) {
            if (custom_field.field_choices) {
                var choices = [];
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

    $scope.getForeignKeyFieldChoiceDisplayName = function(fieldName, choiceId) {
        var fieldChoices = $scope.applicantForeignKeyFieldChoices[fieldName];
        for (var i in fieldChoices) {
            var choice = fieldChoices[i];
            if (choice.value == choiceId) {
                return choice.display_name;
                break;
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
        $http.get("/api/applicant-custom-field/")
            .success(function(data, status, headers, config) {
                $scope.applicationFields = data;
                $scope.formatApplicationTemplate();
        });
    };

    $scope.getApplicantForeignKeyFieldChoices = function() {
        $http.get("/api/applicant-foreign-key-field-choices/")
            .success(function(data, status, headers, config) {
                $scope.applicantForeignKeyFieldChoices = data;
        });
    };

    $scope.init = function() {
        $scope.getApplicantForeignKeyFieldChoices();
        // clean the submission errors for now
        $scope.submissionError.errors = [];

        $http.get("/api/application-template/?is_default=True")
            .success(function(data, status, headers, config) {
                // data[0] returns the first default template,
                // theoretically there should only be one, but this is
                // just a failsafe incase there happens to be more than 1
                var json_template = JSON.parse(data[0].json_template)
                if (!json_template.sections) {
                    $scope.application_template = {"sections" : []};
                } else {
                    $scope.application_template = json_template;
                }
                $scope.refreshCustomFieldList();
        });

        $scope.populateDayOptions();
        $scope.populateYearOptions();


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
                    "type" : field.type,
                    "choices" : field.choices,
                    "max_length" : field.max_length,
                });
                if (field_name == 'state') {
                    $scope.stateOptions = field.choices;
                }
            }
        });
    };

    $scope.reformatDateField = function(dateDict) {
        // Accept a dict in the form {year: "YYYY", month: "MM", day: "DD"}
        // and return a string in the form "YYYY-MM-DD"
        var dateString = '';
        if ( dateDict ) {
            dateString = dateDict.year + "-" + dateDict.month + "-" + dateDict.day;
        }
        return dateString;
    };

    $scope.userReadableDateField = function(dateDict) {
        // Accept a dict in the form {year: "YYYY", month: "MM", day: "DD"}
        // and return a string in the form "January 02, 2012"
        var monthName = "";
        for ( var m in $scope.monthOptions ) {
            var month = $scope.monthOptions[m];
            if ( month.value == dateDict.month ) {
                monthName = month.display_name;
                break;
            }
        }
        var dateString = monthName + " " + dateDict.day + ", " + dateDict.year;
        return dateString;
    };

    $scope.submitApplication = function() {
        $scope.submitSaveInProgress = true;

        // turn previous errors off while we attempt to submit the app
        $scope.submissionError.status = false;
        $scope.submissionError.errors = [];
        // first collect all the values from the template:
        var sections = $scope.application_template.sections;
        // need to initialize an empty contacts array
        $scope.applicant_data.emergency_contacts = [];
        for (var section_id in sections) {
            var section = sections[section_id];
            for (var i in section.fields) {
                var field = section.fields[i];
                if (field.is_field_integrated_with_applicant === true) {
                    if (field.field_type == 'date') {
                        var reformattedDate = $scope.reformatDateField(field.value);
                        $scope.applicant_data[field.field_name] = reformattedDate;
                    } else {
                        $scope.applicant_data[field.field_name] = field.value;
                    }


                } else if (field.is_field_integrated_with_applicant === false) {
                    $scope.applicant_additional_information.push({
                        "custom_field" : field.id,
                        "answer" : field.value,
                    });
                }
                if (field.field_type == 'emergency_contact') {
                    $scope.applicant_data.emergency_contacts.push(field.value);
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
            var applicant_id = data.id;
            for (var i in $scope.applicant_additional_information) {
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
            $scope.submitSaveInProgress = false;
            for ( var i in data ) {
                var field = $scope.getApplicationFieldByFieldName(i);
                var error_msg = data[i][0];
                if ( field && data[i] ) {
                    var error = {
                        "field_label" : field.field_label,
                        "error_msg" : error_msg
                    };

                    $scope.submissionError.errors.push(error);
                }
            }
        });
    };

}]);
