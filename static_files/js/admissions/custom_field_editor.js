var CustomFieldEditor = function() {
    var self = this;

    self.defaultFieldType = "input";
    self.isFieldNew = true;

    self.formatNewFieldModal = function() {
        $("#editModalTitle").html("Create New Custom Field");
        self.populateFieldName("");
        self.selectFieldTypeRadioButton(self.defaultFieldType);
        self.determineIfChoicesShouldBeVisible();
        self.isFieldNew = true;
    };

    self.populateFieldName = function(field_name) {
        $("#field-name-input").val(field_name);
    };

    self.selectFieldTypeRadioButton = function(value_to_select) {
        $("input[name=fieldTypeOptions][value=" + value_to_select + "]").prop('checked', true);
    };

    self.determineIfChoicesShouldBeVisible = function() {
        var current_field_type = $("input[name=fieldTypeOptions]:checked").val();
        if (current_field_type == 'input' || current_field_type == 'textarea') {
            $("#optional-field-choices").hide();
        } else {
            $("#optional-field-choices").show();
        }
    };

    self.submitCustomField = function() {
        var customFieldData = {
            "field_name" : $("#field-name-input").val(),
            "field_type" : $("input[name=fieldTypeOptions]:checked").val(),
            "field_choices" : $("#field-choices-text-area").val()
        }
        if (self.isFieldNew == true) {
            $.ajax({
                type: "POST",
                url: "/api/applicant-custom-field/",
                data: customFieldData,
                success: function() {
                    alert('success!');
                }
            }).fail(function() {
                alert("failure!!!")
            });
        }
    };
};

var editor = new CustomFieldEditor();

$(document).ready(function() {
    $("#newFieldButton").on("click", function() {
        editor.formatNewFieldModal();
    });

    $("input[name=fieldTypeOptions]").change(function() {
        editor.determineIfChoicesShouldBeVisible();
    });

    $("#save-change-button").on("click", function() {
        editor.submitCustomField();
    });
});
