
app.factory('ApplicationFieldFactory', function(Restangular) {
    var applicationFields = Restangular.all('applicant-custom-field');
    return applicationFields;
});

app.factory('ApplicationTemplateFactory', function(Restangular) {
    var applicationTemplate = Restangular.all('application-template');
    return applicationTemplate;
});

