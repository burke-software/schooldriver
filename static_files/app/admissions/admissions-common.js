
app.factory('ApplicationService', function(Restangular) {
    var self = {};

    self.applicationTemplateApi = Restangular.all('application-template');
    self.applicationFieldsApi = Restangular.all('applicant-custom-field');

    self.loadDefaultTemplate = function() {
        return self.applicationTemplateApi.getList({is_default: 'true'})
            .then( function(templates) {
                var applicationTemplate = templates[0];
                var jsonTemplate = JSON.parse(applicationTemplate.json_template)
                self.defaultTemplate = jsonTemplate;
            }).then( function() {
                self.applicationFieldsApi.getList().then( function(fields) {
                    self.applicationFields = fields;
                }).then( function() {
                    self.populateDefaultTemplateWithApplicationFields();
                });
            });
    };

    self.populateDefaultTemplateWithApplicationFields = function() {
        // application template simply contains field IDs - we need to 
        // match those field id's with the corresponding field and inject
        // that field into the template
        var template_sections = self.defaultTemplate.sections;
        for (var section_id in template_sections) {
            var section = template_sections[section_id];
            for (var field_id in section.fields) {
                var section_field = section.fields[field_id];
                var custom_field = self.getApplicationFieldById(section_field.id);
                section.fields[field_id] = custom_field;
            }
        }
    };

    self.getApplicationFieldById = function(field_id) {
        for ( var i in self.applicationFields ) {
            var field = self.applicationFields[i];
            if ( field.id == field_id ) {
                return field;
                break;
            }
        }
    };

    self.convertPythonUnicodeToJsonObject = function(pythonUnicodeString) {
        // some python strings that we want to convert to Json have u"some"
        // so we need to get rid of that u before Json-parsing
        if (pythonUnicodeString) {
            var escapedString = pythonUnicodeString.replace(/u'(?=[^:]+')/g, "'");
            escapedString = escapedString.replace(/'/g,'"');
            return JSON.parse(escapedString);
        }
    }; 

    return self;

});