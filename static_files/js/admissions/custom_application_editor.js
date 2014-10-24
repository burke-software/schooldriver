var admissionsApp = angular.module('admissions',[]);

admissionsApp.controller('CustomApplicationEditorController', ['$scope', '$http', function($scope, $http) {
    
    $scope.application_template = {};
    $scope.applicant_field_options = [];
    $scope.applicant_integrated_fields = [];
    $scope.integratedField={};
    $scope.is_custom_field_new = true;

    $scope.customField = {
        "custom_option" : "integrated",
        "choices" : "",
        "type" : "",
        "name" : "",
        "label": "",
        "helptext" : "",
        "helptext_alt_lang": "",
    };

    $scope.updateIntegratedFieldChoice = function(field) {
        var integrated_field = $scope.integratedField.data;
        $scope.customField.name = integrated_field.name;
        $scope.customField.type = integrated_field.type;
        $scope.customField.choices = integrated_field.choices;
        $scope.customField.label = integrated_field.label;
        $scope.customField.custom_option = "integrated";
    };

    $scope.isNewFieldIntegrated = function() {
        if ($scope.customField.custom_option === "integrated") {
            return true;
        } else {
            return false;
        }
    }

    $scope.newCustomFieldButtonClicked = function() {
        $scope.is_custom_field_new = true;
    }

    $scope.saveNewCustomField = function() {
        if ( $scope.is_custom_field_new === true) {
            var data = $scope.customField;
            $http.post('/api/applicant-custom-field/', data).
              success(function(data, status, headers, config) {
                // this callback will be called asynchronously
                // when the response is available
              }).
               error(function(data, status, headers, config) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                console.log(headers);
                console.log(data);
              });
        }
    }

    $scope.isNewFieldCustom = function() {
        return !$scope.isNewFieldIntegrated();
    }

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

        $http.get("/api/applicant-custom-field")
            .success(function(data, status, headers, config) {
                $scope.applicant_field_options = data;
        });

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

    $scope.moveSectionUp = function(section) {
        var sections = $scope.application_template.sections;
        index_of_section = sections.indexOf(section);
        if (index_of_section != 0) {
            var index_of_section_above = index_of_section - 1;
            var section_above = sections[index_of_section_above];
            // swap this section with the section above
            sections[index_of_section] = section_above;
            sections[index_of_section_above] = section;
        }
    };

    $scope.moveSectionDown = function(section) {
        var sections = $scope.application_template.sections;
        index_of_section = sections.indexOf(section);
        index_of_last_section = sections.length -1;
        if (index_of_section != index_of_last_section) {
            var index_of_section_below = index_of_section + 1;
            var section_below = sections[index_of_section_below];
            // swap this section with the section below
            sections[index_of_section] = section_below;
            sections[index_of_section_below] = section;
        }
    };

    $scope.generateUniqueSectionId = function() {
        var list_of_current_section_ids = [];
        var sections = $scope.application_template.sections;
        for (var i = 0; i < sections.length; i++) {
            list_of_current_section_ids.push(sections[i].id);
        }
        var new_id = 0;
        while (list_of_current_section_ids.indexOf(new_id) != -1) {
            new_id += 1;
        }
        return new_id;
    }

    $scope.newSection = function() {
        $scope.application_template.sections.push({
            "name": "New Section",
            "id" : $scope.generateUniqueSectionId(),
            "fields" : [],
        });
    };

    $scope.isFieldInput = function(field) {
        if (field.type === "input") {
            return true;
        } else {
            return false;
        }
    }

    $scope.removeSectionField = function(section, field) {
        var index_of_field = section.fields.indexOf(field);
        section.fields.splice(index_of_field, 1);
    }

    $scope.addSectionField = function(section, field) {
        section.fields.push({
            "name" : field.field_name, 
            "label" : field.field_label,
            "type" : field.field_type,
            "choices" : field.field_choices
        });
    };  

    $scope.saveApplicationTemplate = function() {
        var url = '/api/application-template/1/';
        var data = {
            "name" : "default application",
            "is_default" : true,
            "json_template" : JSON.stringify($scope.application_template)
        };
        $.ajax({
            type: "PUT",
            data: data,
            url: url
        });
    };
}]);