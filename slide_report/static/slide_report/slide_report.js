function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function load_preview() {
  var csrf_token = getCookie('csrftoken');
  var filters = $('.active_filters .report_filter');
  var filter_data = []
  $('#preview_area').fadeOut();
  $(filters).each(function(key, value) { 
    var filter_dict = {
      'name': $(value).data('name'),
      'form': $(value).children('form.filter_form').serialize()
    }
    filter_data.push(filter_dict)
  })
  $.post(
    'ajax_preview/',
    {
      csrfmiddlewaretoken: csrf_token,
      data: JSON.stringify(filter_data),
    },
    function(data) {
      $('#preview_area').html(data);
      $('#preview_area').fadeIn();
    } 
  ); 
}

var filter_i = 0;
function add_filter(event, ui) {
    prepare_filter(ui.item);
    load_preview();
}

function prepare_filter(filter) {
    var form = $(filter).children('form.filter_form')
    form.show();
    $(filter).attr('id', 'filter_' + filter_i);
    form.children('input[name="filter_number"]').val(filter_i);
    filter_i = filter_i + 1;
}

$(function() {
  $( "#sortable_filters" ).sortable({
    placeholder: "ui-state-highlight",
    update: add_filter,
  });
  $( "#sortable_filters" ).disableSelection();

  $(".draggable").draggable({
    connectToSortable: '#sortable_filters',
    helper: 'clone',
    revert: "invalid",
  });
  $(".draggable").disableSelection();
  $(".select_filters li.draggable").dblclick(function(ev){
    var new_filter = $(this).clone(add_filter).appendTo('#sortable_filters');
    prepare_filter(new_filter);
  });
  load_preview();
});

function process_errors(arr) {
  /* Process ajax error infomation
   * arr is an array generated in a django template */
  $('#sortable_filters .report_filter').removeClass('filter_error');
  arr.forEach(function(value) {
    var filter_li = $('#sortable_filters li#filter_'+value);
    filter_li.addClass('filter_error');
  });
}
