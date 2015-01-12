app.controller('ReviewStudentApplicationController', 
    function($scope, $routeParams, Restangular, ApplicationService) {

        ApplicationService.loadDefaultTemplate().then( function() {
            $scope.applicationTemplate = ApplicationService.defaultTemplate;
            // get this applicant's saved data and populate template with it
            Restangular.one('applicant', $routeParams.applicantId).get()
                .then( function(applicant) {
                    $scope.applicantData = applicant;
                }).then( function() {
                    $scope.populateApplicationTemplateWithStudentResponses();
                });
        });

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
            var additionalData = $scope.getAdditionalDataByFieldId(field.id);
            if ( field.field_type == 'emergency_contact' ) {
                return ApplicationService.convertPythonUnicodeToJsonObject(additionalData.answer); 
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


});

