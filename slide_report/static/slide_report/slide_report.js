jQuery(function($) { $.extend({
    form: function(url, data, method) {
        if (method == null) method = 'POST';
        if (data == null) data = {};

        var form = $('<form>').attr({
            method: method,
            action: url
         }).css({
            display: 'none'
         });

        var addData = function(name, data) {
            if ($.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    var value = data[i];
                    addData(name + '[]', value);
                }
            } else if (typeof data === 'object') {
                for (var key in data) {
                    if (data.hasOwnProperty(key)) {
                        addData(name + '[' + key + ']', data[key]);
                    }
                }
            } else if (data != null) {
                form.append($('<input>').attr({
                  type: 'hidden',
                  name: String(name),
                  value: String(data)
                }));
            }
        };

        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                addData(key, data[key]);
            }
        }

        return form.appendTo('body');
    }
}); });

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


function view_results(type) {
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
  data_dict = {
    csrfmiddlewaretoken: csrf_token,
    data: JSON.stringify(filter_data),
  }
  
  if (type == 'preview') { // AJAX
    $.post(
      'view/?type=' + type,
      data_dict,
      function(data) {
        $('#preview_area').html(data);
        $('#preview_area').fadeIn();
      } 
    );
  } else {
    $.form('view/?type=' + type, data_dict, 'POST').submit();
  }
}

var filter_i = 0;
function add_filter(event, ui) {
    prepare_filter(ui.item);
    view_results('preview');
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

  $(".draggable").draggable({
    connectToSortable: '#sortable_filters',
    helper: 'clone',
    revert: "invalid",
  });
  $(".select_filters li.draggable").dblclick(function(ev){
    var new_filter = $(this).clone(add_filter).appendTo('#sortable_filters');
    prepare_filter(new_filter);
  });
  view_results('preview');
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
