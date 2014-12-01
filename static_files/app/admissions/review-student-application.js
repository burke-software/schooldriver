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
});

