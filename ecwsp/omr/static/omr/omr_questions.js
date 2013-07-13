$(function() {
  // When contenteditable blurs, trigger a change event if it was changed
  $('body').on('focus', '[contenteditable]', function() {
    var $this = $(this);
    $this.data('before', $this.html());
    return $this;
  }).on('blur', '[contenteditable]', function() {
    var $this = $(this);
    if ($this.data('before') !== $this.html()) {
      $this.data('before', $this.html());
      $this.trigger('change');
    }
    return $this;
  });

  $('#question_sortable').sortable({
    zindex: 10,
    handle: 'i.question.handle',
    update: function(event, ui) {
      $.post(
        '/omr/test_questions/'+$(ui.item).data("question_id")+'/save_question/',
        {content: ui.item.index(), field: 'order'},
        function(data){
          $.each(data, function(key, value){
            $('#question_'+key+'_div').find('span.question_order').html(value + 1);
          });
        },
        "json"
      )  
    }
  });

});

function save_inline_question(e, obj_id, field){
  var data = $(e).html();
  $.post(
    '/omr/test_questions/'+obj_id+'/save_question/',
    {content: data, field: field},
    function(data){
      $('#save_status').html(data);
    }
  );
}

function save_inline_answer(e, obj_id, field){
  var data = $(e).html();
  $.post(
    '/omr/test_questions/'+obj_id+'/save_answer/',
    {content: data, field: field},
    function(data){
      $('#save_status').html(data);
    }
  );
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
  
  function showBenchmarkPopup(triggeringLink, question_id) {
    var name = triggeringLink.id.replace(/^add_/, '');
    //name = id_to_windowname(name);
    href = triggeringLink.href;
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, "Whatever", 'height=500,width=1000,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
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
  
  function mark_as_answer(question_id, answer_id) {
    $.post(
        "ajax_mark_as_answer/" + answer_id + "/",
        function(data){
            if (data) {
                $("#point_value_" + answer_id).html(data);
                $(".mark_button_" + question_id).remove();
            }
        }  
    );
  }
  
function add_question(question_type) {
  $.post(
    "ajax_question_form/new/",
    {question_type: question_type},
    function(data){
      $('#new_question_div').before(data);
    }  
  );
}

function delete_question(question_id) {
  var confirmed = confirm("Are you sure you wish to delete this question?");
  if ( confirmed ) {
    var jqxhr = $.post(
      "ajax_delete_question/"+question_id+"/",
      function(data){
        $('#question_'+question_id+'_div').remove();
        $.each(data, function(key, value){
          $('#question_'+key+'_div').find('span.question_order').html(value + 1);
        });
      }  
    )
    .done(function() { $('#save_status').html('Success!'); })
    .fail(function() { $('#save_status').html('ERROR!'); });
  }
}

function add_answer(question_id) {
  $.post(
    "add_answer/"+question_id+"/new/",
    function(data){
      $('#new_answer_div-'+question_id).before(data);
    }  
  );
}

function delete_answer(answer_id) {
  var confirmed = confirm("Are you sure you wish to delete this answer?");
  if ( confirmed ) {
    var jqxhr = $.post(
      "ajax_delete_answer/"+answer_id+"/",
      function(data){
        $('#answer_'+answer_id+'_div').remove();
        $.each(data, function(key, value){
          $('#answer_'+key+'_div').find('span.answer_order').html(value);
        });
      }  
    )
    .done(function() { $('#save_status').html('Success!'); })
    .fail(function() { $('#save_status').html('ERROR!'); });
  }
}

function ajax_benchmarks_form_save(question_id){
  var div = $('div#benchmarks_'+question_id)
  $.post(
    'ajax_benchmarks_form/'+question_id+'/',
    $('#question_benchmarks_'+question_id+'_form').serialize(),
    function(data){
      $(div).html(data); 
      $(div).removeClass('editing');
    });
}

function ajax_benchmarks_form(div, question_id){
  if ( $(div).hasClass('editing') ) {
  } else {
    $.post(
      'ajax_benchmarks_form/'+question_id+'/',
      function(data){
        $(div).html(data); 
        $(div).addClass('editing');
      });
  }
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

function selectElementContents(el) {
    var range = document.createRange();
    range.selectNodeContents(el);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}
