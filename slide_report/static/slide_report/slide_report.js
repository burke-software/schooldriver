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
      'name': $(value).data('name')
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

$(function() {
  $( "#sortable_filters" ).sortable({
    placeholder: "ui-state-highlight",
    update: load_preview,
  });
  $( "#sortable_filters" ).disableSelection();

  $(".draggable").draggable({
    connectToSortable: '#sortable_filters',
    helper: 'clone',
    revert: "invalid",
  });
  $(".draggable").disableSelection();
  load_preview();
});
