function toggle(id) {
    if( id == "id_all_years" ){
        $("#id_this_year").attr('checked', false);
        if ($("#id_all_years").is(':checked')) { 
            $("#id_date_begin").val("");
            $("#id_date_end").val("");
            $('#id_date_begin').attr('disabled', true);
            $('#id_date_end').attr('disabled', true);
	    $('.datetimeshortcuts').hide();
        } else {
            $('#id_date_begin').attr('disabled', false);
            $('#id_date_end').attr('disabled', false);
	    $('.datetimeshortcuts').show();
        }
    } else if ( id == "id_this_year" ) {
        $("#id_all_years").attr('checked', false);
        if ($("#id_this_year").is(':checked')) { 
            $("#id_date_begin").val("");
            $("#id_date_end").val("");
            $('#id_date_begin').attr('disabled', true)
            $('#id_date_end').attr('disabled', true)
	    $('.datetimeshortcuts').hide();
        } else {
            $('#id_date_begin').attr('disabled', false);
            $('#id_date_end').attr('disabled', false);
	    $('.datetimeshortcuts').show();
        }
    }
}

$(document).ready(function() {
	if ($("#id_this_year").attr('checked') == 'checked')  {
	    $('#id_date_begin').attr('disabled', true);
	    $('#id_date_end').attr('disabled', true);
	    setTimeout("$('.datetimeshortcuts').hide()",20);
	}
});
