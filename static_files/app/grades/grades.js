  app.controller('StudentGradesController', function($scope, GradebookService, $routeParams, $route) {
    var grades_api;
    $scope.columns = [
      {
        width: 160,
        value: 'row.course_section',
        title: 'Course',
        fixed: true,
        readOnly: true
      }
    ];
    grades_api = GradebookService;
    $scope.changeGrade = grades_api.setGrade;
    $scope.beforeChangeGrade = function(changes, source) {
      var attribute, change, id, instance, row, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = changes.length; _i < _len; _i++) {
        change = changes[_i];
        id = change[0];
        row = grades_api.rows[id];
        attribute = change[1];
        instance = row[attribute.split('.')[0]];
        _results.push(instance.isPristine = false);
      }
      return _results;
    };
    $scope.$on('$routeChangeSuccess', function() {
      var year_id;
      grades_api.marking_periods = [];
      grades_api.rows = [];
      $scope.rows = grades_api.rows;
      grades_api.student_id = $routeParams.student_id;
      if ($routeParams.year_id) {
        year_id = $routeParams.year_id;
      } else {
        year_id = default_school_year_id;
      }
      return grades_api.getGrades({
        student: grades_api.student_id,
        course_section__marking_period__school_year: year_id,
        ordering: 'marking_period__start_date'
      }).then(function(grades) {
        var final, grade, new_row, row, _i, _j, _len, _len1, _ref;
        $scope.grades = grades;
        for (_i = 0, _len = grades.length; _i < _len; _i++) {
          grade = grades[_i];
          new_row = true;
          _ref = grades_api.rows;
          for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
            row = _ref[_j];
            if (row.course_section_id === grade.course_section_id) {
              new_row = false;
            }
          }
          if (new_row) {
            final = {
              grade: 0
            };
            grades_api.rows.push({
              course_section: grade.course_section,
              course_section_id: grade.course_section_id,
              final: final
            });
          }
        }
        return grades_api.addMarkingPeriods(grades, grades_api.rows, $scope.columns, 'course_section_id');
      });
    });
    $scope.comment_button_text = "Show Comments";
    return $scope.showComments = function() {
      return $scope.comment_button_text = grades_api.toggleComments($scope.columns);
    };
  });

  app.controller('CourseGradesController', function($scope, $routeParams, $route, GradebookService) {
    var grades_api;
    $scope.columns = [
      {
        width: 160,
        value: 'row.student',
        title: 'Student',
        fixed: true,
        readOnly: true
      }
    ];
    grades_api = GradebookService;
    $scope.rows = grades_api.rows;
    $scope.changeGrade = grades_api.setGrade;
    $scope.$on('$routeChangeSuccess', function() {
      var course_section_id;
      course_section_id = $routeParams.course_section_id;
      grades_api.course_section_id = course_section_id;
      return grades_api.getGrades({
        course_section: course_section_id,
        ordering: 'marking_period__start_date'
      }).then(function(grades) {
        var final, grade, new_student, student, this_student, _i, _j, _len, _len1, _ref;
        grades = grades;
        for (_i = 0, _len = grades.length; _i < _len; _i++) {
          grade = grades[_i];
          new_student = true;
          this_student = null;
          _ref = grades_api.rows;
          for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
            student = _ref[_j];
            if (student.student_id === grade.student_id) {
              new_student = false;
            }
          }
          if (new_student) {
            final = {
              grade: 0
            };
            grades_api.rows.push({
              student: grade.student,
              student_id: grade.student_id,
              final: final
            });
          }
        }
        return grades_api.addMarkingPeriods(grades, grades_api.rows, $scope.columns, 'student_id');
      });
    });
    $scope.comment_button_text = "Show Comments";
    return $scope.showComments = function() {
      return $scope.comment_button_text = grades_api.toggleComments($scope.columns);
    };
  });

  app.factory('GradebookService', function(Restangular) {
    var comment_ids, finalRenderer, gradeRenderer, grades_api;
    gradeRenderer = function(instance, td, row, col, prop, value, cellProperties) {
      var data_instance, data_row;
      Handsontable.TextCell.renderer.apply(this, arguments);
      data_row = grades_api.rows[row];
      data_instance = data_row[prop.split('.')[0]];
      if (data_instance) {
        if (data_instance.isValid === true) {
          return td.className += "table-is-valid";
        } else if (data_instance.isValid === false) {
          return td.className += "table-is-not-valid";
        } else if (data_instance.isPristine === true) {
          return td.style.borderRight = "2px solid #f00";
        } else if (data_instance.isPristine === false) {
          return td.style.borderRight = "2px solid #00f";
        }
      } else {
        td.className += ' no-marking-period';
        return cellProperties.readOnly = true;
      }
    };
    finalRenderer = function(instance, td, row, col, prop, value, cellProperties) {
      var data_instance, data_row;
      Handsontable.TextCell.renderer.apply(this, arguments);
      data_row = grades_api.rows[row];
      data_instance = data_row['final'];
      if (data_instance.isValid === false) {
        return td.className += "table-is-not-valid";
      } else if (data_instance.hasOverride === true) {
        return td.className += "table-is-overridden";
      }
    };
    grades_api = Restangular.all('grades');
    grades_api.marking_periods = [];
    grades_api.rows = [];
    grades_api.recalculateGrades = function(student) {
      var final, final_grade, grade, gradeFloat, gradeLower, grade_object, marking_period, num_of_mp, _i, _len, _ref;
      final = 0.0;
      num_of_mp = 0;
      _ref = grades_api.marking_periods;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        marking_period = _ref[_i];
        grade_object = student['grade' + marking_period.marking_period_id];
        if (grade_object) {
          grade = grade_object.grade;
          gradeFloat = parseFloat(grade);
          if (grade !== null) {
            if (isNaN(gradeFloat)) {
              gradeLower = grade.toLowerCase();
              if (gradeLower === "i") {
                return "I";
              } else if (gradeLower === "p" || gradeLower === "lp" || gradeLower === "hp") {
                final += 100;
                num_of_mp += 1;
              } else if (gradeLower === "f" || gradeLower === "m") {
                num_of_mp += 1;
              }
            } else {
              final += gradeFloat;
              num_of_mp += 1;
            }
          }
        }
      }
      final_grade = (final / num_of_mp).toFixed(2);
      student.hasOverride = false;
      if (isNaN(final_grade)) {
        return student.final.grade = '';
      } else {
        return student.final.grade = final_grade;
      }
    };
    grades_api.findMarkingPeriods = function(grades) {
      var grade, marking_period, new_marking_period, _i, _j, _len, _len1, _ref, _results;
      _results = [];
      for (_i = 0, _len = grades.length; _i < _len; _i++) {
        grade = grades[_i];
        new_marking_period = true;
        _ref = grades_api.marking_periods;
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          marking_period = _ref[_j];
          if (marking_period.marking_period_id === grade.marking_period_id) {
            new_marking_period = false;
          }
        }
        if (new_marking_period && grade.marking_period !== null) {
          _results.push(grades_api.marking_periods.push({
            marking_period: grade.marking_period,
            marking_period_id: grade.marking_period_id
          }));
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };
    grades_api.addMarkingPeriods = function(grades, rows, columns, field) {
      var grade, grade_columns, marking_period, new_column, row, _i, _j, _k, _l, _len, _len1, _len2, _len3, _ref;
      grade_columns = [];
      _ref = grades_api.marking_periods;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        marking_period = _ref[_i];
        marking_period.grade_key = 'grade' + marking_period.marking_period_id;
        new_column = {
          width: 70,
          renderer: gradeRenderer,
          value: 'row.' + marking_period.grade_key + '.grade',
          title: marking_period.marking_period
        };
        if (edit === 'False') {
          new_column.readOnly = true;
        }
        columns.push(new_column);
        for (_j = 0, _len1 = rows.length; _j < _len1; _j++) {
          row = rows[_j];
          for (_k = 0, _len2 = grades.length; _k < _len2; _k++) {
            grade = grades[_k];
            if (grade[field] === row[field]) {
              if (grade.marking_period_id === marking_period.marking_period_id) {
                row[marking_period.grade_key] = grade;
              } else if (grade.override_final === true) {
                row.final = grade;
              }
            }
          }
        }
      }
      new_column = {
        width: 70,
        renderer: finalRenderer,
        value: 'row.final.grade',
        title: 'Final'
      };
      if (edit_final === 'False') {
        new_column.readOnly = true;
      }
      columns.push(new_column);
      for (_l = 0, _len3 = rows.length; _l < _len3; _l++) {
        row = rows[_l];
        if (row.final.id) {
          row.final.hasOverride = true;
        } else {
          grades_api.recalculateGrades(row);
        }
      }
      return grades_api.rows = rows;
    };
    grades_api.setGrade = function(changes, source) {
      var attribute, change, id, instance, new_grade, row, _i, _len, _ref, _results;
      if (source !== 'loadData') {
        _results = [];
        for (_i = 0, _len = changes.length; _i < _len; _i++) {
          change = changes[_i];
          id = change[0];
          row = grades_api.rows[id];
          attribute = change[1];
          if (attribute === "final.grade") {
            if ((_ref = row.final.grade) === "" || _ref === null || _ref === "None") {
              if (row.final.id) {
                row.final.remove();
                row['final'] = {
                  grade: 0
                };
              }
              _results.push(grades_api.recalculateGrades(row));
            } else {
              row.final.hasOverride = true;
              if (row.final.id) {
                _results.push(row.final.save().then((function(response) {
                  return row.final.isValid = true;
                }), function(response) {
                  return row.final.isValid = false;
                }));
              } else {
                new_grade = {
                  grade: row.final.grade,
                  override_final: true
                };
                if (grades_api.student_id) {
                  new_grade.student_id = grades_api.student_id;
                } else {
                  new_grade.student_id = row.student_id;
                }
                if (grades_api.course_section_id) {
                  new_grade.course_section_id = grades_api.course_section_id;
                } else {
                  new_grade.course_section_id = row.course_section_id;
                }
                _results.push(grades_api.post(new_grade).then((function(response) {
                  return row.final.isValid = true;
                }), function(response) {
                  row.final.isValid = false;
                  return $('.handsontable').data('handsontable').render();
                }));
              }
            }
          } else {
            if (!row.final.id) {
              grades_api.recalculateGrades(row);
            }
            instance = row[attribute.split('.')[0]];
            _results.push(instance.save().then((function(response) {
              instance.isValid = true;
              return $('.handsontable').data('handsontable').render();
            }), function(response) {
              instance.isValid = false;
              return $('.handsontable').data('handsontable').render();
            }));
          }
        }
        return _results;
      }
    };
    grades_api.getGrades = function(filters) {
      return grades_api.getList(filters).then(function(grades) {
        grades_api.findMarkingPeriods(grades);
        grades_api.grades = grades;
        return grades;
      });
    };
    comment_ids = [];
    grades_api.toggleComments = function(columns) {
      var column, comment_id, deleted, key, marking_period, _i, _j, _k, _len, _len1, _len2, _ref;
      if (comment_ids.length === 0) {
        _ref = grades_api.marking_periods;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          marking_period = _ref[_i];
          for (key = _j = 0, _len1 = columns.length; _j < _len1; key = ++_j) {
            column = columns[key];
            if (column.value === 'row.' + marking_period.grade_key + '.grade') {
              columns.splice(key + 1, 0, {
                width: 160,
                value: 'row.' + marking_period.grade_key + '.comment',
                title: marking_period.marking_period + ' Comments'
              });
              comment_ids.push(key + 1);
              break;
            }
          }
        }
        return "Hide Comments";
      } else {
        deleted = 0;
        for (_k = 0, _len2 = comment_ids.length; _k < _len2; _k++) {
          comment_id = comment_ids[_k];
          columns.splice(comment_id - deleted, 1);
          deleted += 1;
        }
        comment_ids = [];
        return "Show Comments";
      }
    };
    return grades_api;
  });
