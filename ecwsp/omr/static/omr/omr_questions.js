function clean_ckeditor(question_id) {
    var instances = CKEDITOR.instances;
    re = "id_questionanswers_" + question_id + "-.*-answer";
    instances["id_question_" + question_id + "-question"].destroy();
    $.each(instances, function(key, value) { 
      if ( key.match(re) ) {
        instances[key].destroy();
      }
    });
  }
  
  function dismissQuestionBankPopup(window, question_bank_id) {
    $.post(  
      "ajax_question_bank_to_question/" + question_bank_id + "/",
      function(data){
        $('#new_question_div').before(data);
      }  
    );
    window.close();
  }
  
  function dismissBenchmarkPopup(window, benchmark_id, benchmark_text) {
    $('#id_question_' + foo + '-benchmarks').val($('#id_question_' + foo + '-benchmarks').val() + benchmark_id + '|');
    
    $('#id_question_' + foo + '-benchmarks_on_deck').append('<div id="id_question_' + foo + '-benchmarks_on_deck_' + benchmark_id + '"><span class="iconic" id="kill_id_question_' + foo + '-benchmarks' + benchmark_id + '">X</span> ' + benchmark_text + ' </div>');
    
    window.close();
  }
  
  foo = "";
  function showBenchmarkPopup(page, question_id) {
    foo = question_id;
    return showAddAnotherPopup(page);
  }
  
  function check_correct_answer(question_id) {
    possible = $("#id_question_" + question_id + "-point_value").val();
    
    // Clear green
    $('input')
      .filter(function() {
        return this.id.match("id_questionanswers_" + question_id + "-.*-point_value");
      })
      .removeAttr("style")
    ;
    // Set green for correct answer
    $('input')
      .filter(function() {
        return this.id.match("id_questionanswers_" + question_id + "-.*-point_value");
      })
      .filter(function() { return $(this).val() == possible; })
      .css('background-color', '#a6ffa8')
    ;
  }
  
  function edit_question(id) {
    // Change read only question into editable
    $.post(  
      "ajax_question_form/" + id + "/",
      function(data){
        $("#question_" + id).html(data);
      }  
    );
  }
  
  function cancel_edit(id){
  // cancel changes and bring back read only form.
    var confirmed = confirm("Cancel changes?");
    if ( confirmed ) {
      clean_ckeditor(id);
      if (id == 'new') {
        $("#question_" + id).remove();
      } else {
        $.post(  
          "ajax_read_only_question/" + id + "/",
          function(data){
            $("#question_" + id).html(data);
          }  
        );
      }
    }
  }
  
  function delete_question(id) {
    // Delete selected question completly.
    var confirmed = confirm("Are you sure you want to permanently delete this question?");
    if ( confirmed ) {
      clean_ckeditor(id);
      $.post(  
        "ajax_delete_question/" + id + "/",
        function(data){
          // Remove element only on successful ajax call
          if (data == "SUCCESS") {
            $("#question_" + id).remove();
          }
        }  
      );
    }
  }
  
  function mark_as_answer(question_id, answer_id) {
    $.post(
        "ajax_mark_as_answer/" + answer_id + "/",
        function(data){
            if (data) {
                $("#point_value_" + answer_id).html(data);
                $("#div_answer_" + answer_id).css('background', '#A6FFA8');
                $(".mark_button_" + question_id).remove();
            }
        }  
    );
  }
  
  function add_question() {
    // Add new question
    if ( $('#question_new').length ) {
      var submit_new = confirm('You must save previous question first. Would you like to save now?');
      if ( submit_new ) {
        $('#question_new').find('#save_question_new').click()
      }
      return false;
    }
    
    $.post(
      "ajax_question_form/new/",
      function(data){
        $('#new_question_div').before(data);
      }  
    );
  }
  
  function save_question(form_id, question_id) {
    // Ajax save a form
    for ( instance in CKEDITOR.instances ) {
      CKEDITOR.instances[instance].updateElement();
    }
    
    $("#" + form_id).find('.answer_div').each( function(i, answer_div) {
      // in the answer div, find the answer span, then find the text area and get it's ID. Use that to find the CKEDITOR instance.
      // The replace br is due to some oddity in firefox where by default there is a br unless clicked on.
      if ( CKEDITOR.instances[$(answer_div).find('.answer_span').find('textarea').attr('id')].getData().replace('<br />\n', '').length <= 0 ) {
        $(answer_div).find('input:checkbox').prop("checked", true);
        $(answer_div).find('input:checkbox').val("on");
        $(answer_div).find('input:checkbox').attr("checked", "checked");
      }
    });
    
    form_data = $("#" + form_id).serialize();
    
    clean_ckeditor(question_id);
    
    $.post(  
      "ajax_question_form/" + question_id + "/",
      form_data,
      function(data){
        if ( question_id == "new" ){
          $('#new_question_div').before(data);
          $('#question_new').remove();
        } else {
          $("#question_" + question_id).html(data);
        }
      }  
    );
  }
  
  function move_question(direction, question_id) {
    var question_div = $('#question_' + question_id);
    if ( direction == "up" ) {
      var prev_div = question_div.prev();
      // Don't move into silly places!
      if (prev_div.attr('id') == "title_h2") {
          return false;
      }
      
      var question_up_id = question_div.attr('id');
      var question_down_id = prev_div.attr('id');
      question_div.css("position", "relative");
      prev_div.css("position", "relative");
      question_div.animate({top: -prev_div.height()},500);
      prev_div.animate({top: question_div.height()},500, function() {
        setTimeout(function() {
          question_div.css('position', 'static');
          prev_div.css('position', 'static');
          question_div.css('top', '0px');
          prev_div.css('top', '0px');
          question_div.removeAttr("style");
          prev_div.removeAttr("style");
          question_div.insertBefore(prev_div);
        }, 50);
      });
    } else {
      var prev_div = question_div.next();
      // Don't move into silly places!
      if (prev_div.attr('id') == "new_question_div") {
          return false;
      }
      
      var question_up_id = prev_div.attr('id');
      var question_down_id = question_div.attr('id');
      question_div.css("position", "relative");
      prev_div.css("position", "relative");
      question_div.animate({top: prev_div.height()},500);
      prev_div.animate({top: -question_div.height()},500, function() {
        setTimeout(function() {
          question_div.css('position', 'static');
          prev_div.css('position', 'static');
          question_div.css('top', '0px');
          prev_div.css('top', '0px');
          question_div.removeAttr("style");
          prev_div.removeAttr("style");
          prev_div.insertBefore(question_div);
        }, 50);
      });
    }
      
    $.post(  
      "ajax_reorder_question/",
      {'question_up_id': question_up_id, 'question_down_id': question_down_id},
      function(data){
        $.each(data, function(key, value) {
          $('#question_' + key).find('.question_order').html(value);
        });
      },
      "json"
    );

  }
  
  function check_type(question_id) {
    var question_type = $('#id_question_' + question_id + '-type');
    if ( question_type.val() == "True/False" ) {
      $('#question_' + question_id + '_answers_div').hide();
      $('#question_' + question_id + '_is_true_div').show();
    } else {
      $('#question_' + question_id + '_answers_div').show();
      $('#question_' + question_id + '_is_true_div').hide();
    }
  }
  
  function finalize_test(test_id) {
    var confirmed = confirm("Are you sure you want to finalize this test?\nYou will no longer be able to make changes to this test.");
    if ( confirmed ) {
      $.blockUI({
        overlayCSS: { backgroundColor: '#00f' },
        message: '<h1>Sending tests to QueXF...please wait. This may take up to a minute. You will be notified in case or errors.</h1>', 
      });
      
        var result = $.post(  
            "ajax_finalize_test/",
            function(data){
                if (data == "SUCCESS") {
                    document.location.href = '/omr/test_result/' + test_id;
                } else {
                    // Error, let user know they should panic!
                    $.blockUI({
                        overlayCSS: { backgroundColor: '#ff0009' },
                        message: '<h1>Error! Click outside this box to dismiss.</h1>' + data, 
                    });
                    $('.blockOverlay').attr('title','Click to unblock').click($.unblockUI); 
                }
            }
        );
        result.error(function() {
            $.blockUI({
                overlayCSS: { backgroundColor: '#ff0009' },
                message: '<h1>Error! Click outside this box to dismiss.</h1>', 
            });
            $('.blockOverlay').attr('title','Click to unblock').click($.unblockUI); 
        })
    }
  }