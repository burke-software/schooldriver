function createCookie(name,value,days) {
    if (days) {
	var date = new Date();
	date.setTime(date.getTime()+(days*24*60*60*1000));
	var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
	var c = ca[i];
	while (c.charAt(0)==' ') c = c.substring(1,c.length);
	if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}


$(document).ready(function() {
    // Check cookies to see if sections are already open
    var headers = ['a_general','a_grades','a_schedule', 'a_discipline',
		   'a_attendance', 'a_student_interactions', 'a_alumni',
		   'a_counseling','a_admissions','a_volunteer','a_work_study'];
    if (readCookie('a_general') == null) { // Default is open
	createCookie('a_general', 'true');
    }
    for (var i=0; i<headers.length; i++) {
	if (readCookie(headers[i]) == "true") {
	    $("#" + headers[i]).toggleClass('expanded').next(".sv-main").show();
	}
    }
    
    // Switches CSS classes. This controls the right and down arrows.  
    $(".section-header").click(function () {
	$(this).parent().removeClass('noprint');
	if ($(this).hasClass("subsection")) {
	    $(this).toggleClass('sub-expanded');
	    $(this).toggleClass('noprint');
	} else {
	    if ($(this).hasClass('expanded')) {
		createCookie($(this).attr('id'), 'false');
	    } else {
		createCookie($(this).attr('id'), 'true');
	    }
	    $(this).toggleClass('expanded');
	    $(this).toggleClass('noprint');
	}
	
	// Toggle the section.
	$(this).next(".sv-main").slideToggle(600);
    });
});

function ajax_include_deleted(){
    var checked = $('#id_include_deleted').is(":checked");
    $.ajax({
	url: "/sis/ajax_include_deleted?checked=" + checked
    });
}

function ajax_quick_add_note() {
    $.post(  
        "/alumni/ajax_quick_add_note/" + alumni_id + "/",
        function(data){
	    html = '<form action="/alumni/ajax_quick_add_note" method="post" id="quick_add_note_form">'
		+ data
		+ '<input type="button" value="Save" class="grp-button" onclick="ajax_quick_add_note_save()"/></form>';
	    $("#quick_add_alumni_note").html(html);
        }
    );
}

function ajax_quick_add_note_save() {
    CKEDITOR.instances['id_note'].updateElement();
    form_data = $('#quick_add_note_form').serialize();
    $.post(
        "/alumni/ajax_quick_add_note/" + alumni_id + "/",
	form_data,
        function(note){
	    CKEDITOR.instances['id_note'].destroy();
	    button_html = '<a href="javascript:void(0)" onclick="ajax_quick_add_note()">Quick add note</a>';
	    $("#quick_add_alumni_note").html(button_html);
	    note_html = '<tr><td>' + note + '</td></tr>';
	    $('#div_to_insert_new_notes').before(note_html)
        }
    );
}
