app.controller('ReviewStudentApplicationController', 
    function($scope, $route, $routeParams, ApplicationFieldFactory, ApplicationTemplateFactory, Restangular) {
        $scope.$routeParams = $routeParams;
        $scope.submissionDate = "";

        // get this applicant's saved data
        Restangular.one('applicant', $routeParams.applicantId).get()
            .then( function(applicant) {
                $scope.applicantData = applicant
            });

        // get the default application template and format it
        ApplicationTemplateFactory.getList({is_default: 'true'})
            .then( function(templates) {
                var applicationTemplate = templates[0];
                var jsonTemplate = JSON.parse(applicationTemplate.json_template)
                $scope.applicationTemplate = jsonTemplate;
            }).then( function() {
                ApplicationFieldFactory.getList().then( function(fields) {
                    $scope.applicationFields = fields;
                }).then( function() {
                    $scope.populateApplicationTemplateWithApplicationFields();
                }).then( function() {
                    $scope.populateApplicationTemplateWithStudentResponses();
                });
            });

        $scope.populateApplicationTemplateWithApplicationFields = function() {
            // applicationt template simply contains field IDs - we need to 
            // match those field id's with the corresponding field and inject
            // that field into the template
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

        $scope.populateApplicationTemplateWithStudentResponses = function() {
            var template = $scope.applicationTemplate;
            var studentResponses = $scope.applicantData;
            for (var section_id in template.sections) {
                var section = template.sections[section_id];
                for (var field_id in section.fields) {
                    var field = section.fields[field_id];
                    if ( field.is_field_integrated_with_applicant == true ) {
                        field.value = studentResponses[field.field_name];
                    } else {
                        field.value = $scope.getAdditionalFieldValue(field);
                    }
                }
            }
        }; 

        $scope.getAdditionalFieldValue = function(field) {
            var additionalData = $scope.getApplicationFieldById(field.id);
            if ( field.field_type == 'emergency_contact' ) {
                return $scope.convertPythonUnicodeToJsonObject(additionalData.answer); 
            } else {
                return additionalData.answer;
            }

        }; 

        $scope.getAdditionalDataByFieldId = function(fieldId) {
            additional = null;
            for (var i in $scope.applicantData.additionals ) {
                var candidateAdditional = $scope.applicantData.additionals[i];
                if ( candidateAdditional.custom_field == fieldId ) {
                    additional = candidateAdditional;
                    break;
                }
            }
            return additional;
        };

        $scope.convertPythonUnicodeToJsonObject = function(pythonUnicodeString) {
            if (pythonUnicodeString) {
                var escapedString = pythonUnicodeString.replace(/u'(?=[^:]+')/g, "'");
                escapedString = escapedString.replace(/'/g,'"');
                return JSON.parse(escapedString);
            }
        }; 
});

