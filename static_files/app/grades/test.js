describe('saveGradeService', function () {
  var saveGradeService;
  beforeEach(module('angular_sis'));
  beforeEach(inject(function (_saveGradeService_) {
    saveGradeService = _saveGradeService_;
  }));
  it('sends set_grade api post', function () {
    saveGradeService.saveGrade(2, 3, 'grade_final', '1');
  });
});
