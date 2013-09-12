function submit_form(){
    $(":input:not(.changed):not(input[type=submit])").attr('disabled','disabled')
}

function toggle_comments(){
    $('.comment').toggle();
    fullscreen_table(true);
}

function fullscreen_table(destroy){
    if ($('#gradebook_div').length){
        if (destroy){
            //$('#gradebook_table').fixedHeaderTable('destroy');
        }
        window_height = $(window).height()
        needed_height = $('#gradebook_div').height();
        buffer = 170
        if (window_height-buffer < needed_height) {
            //$('#gradebook_table').fixedHeaderTable({ height: '300', width: '300', fixedColumn: 1 });
        }
    }
}

function mark_change(event) {
    // Change color to show change
    $(event.target).addClass('changed');
} 

function remove_grade(event, input_id) {
    $('#' + input_id).removeClass('final_override');
    $('#' + input_id).addClass('changed');
    $('#' + input_id).val('');
    $(event.target).remove();
}

function keyboard_nav(event) {
    key = event.which;
    if (key == 13 || key == 40 || key == 38 || key == 37 || key == 39) {
        column = $(event.target).parents('td').attr('id').replace(/_r\d*/, '').replace(/tdc/,'').trim();
        row = $(event.target).parents('td').attr('id').replace(/^tdc\d*_r/, '').trim();
        
        var selected_element;
        if(key == 13 || key == 40) { // Down
            selected_element = $('td#tdc' + column + '_r' + (parseInt(row)+1)).children('input');
        } else if (key == 38) { // Up
            selected_element = $('td#tdc' + column + '_r' + (parseInt(row)-1)).children('input');
        } else if (key == 37) { // Left
            selected_element = $('td#tdc' + (parseInt(column)-1) + '_r' + row).children('input');
        } else if (key == 39) { // Right
            selected_element = $('td#tdc' + (parseInt(column)+1) + '_r' + row).children('input');
        }
        $(selected_element).focus();
        $(selected_element).select();
        return false;
    }
}

function recalc_ytd_grade(mp_grade_inputs, ytd_input) {
    if (ytd_input.attr('class') != 'grade_form final_override') {
        grade = 0;
        num_mp_grades = 0;
        add_total = true;
        letter_grade = false;
        mp_grade_inputs.each(function(i){
            mp_grade_value = $(this).val()
            mp_grade = parseFloat(mp_grade_value);
            if (!(isNaN(mp_grade))) {
                grade += mp_grade;
                num_mp_grades += 1;
            } else if (mp_grade_value.toLowerCase() == "i") {
                // If there is an I, the final should be just I
                ytd_input.val("I");
                add_total = false;
                return;
            } else if (mp_grade_value.toLowerCase() == "p" ||
                       mp_grade_value.toLowerCase() == "lp" ||
                       mp_grade_value.toLowerCase() == "hp") {
                grade += 100;
                num_mp_grades += 1;
                letter_grade = true;
            } else if (mp_grade_value.toLowerCase() == "f" ||
                       mp_grade_value.toLowerCase() == "m") {
                num_mp_grades += 1;
                letter_grade = true;
            }
        });
        
        if (add_total) {
            grade = grade / num_mp_grades;
            grade = Math.round(grade*100)/100;
            if (letter_grade) {
                if (grade > letter_grade_required_for_pass){
                    ytd_input.val("P");
                } else {
                    ytd_input.val("F");
                }
            } else {
                ytd_input.val(grade);
            }
        }
    }
}

function student_grade_change(event, student_id) {
    mp_grade_inputs = $('input[id^=id_grade_' + student_id + ']')
    ytd_input = $('input[id=grade_final_' + student_id + ']');
    recalc_ytd_grade(mp_grade_inputs, ytd_input);
    mark_change(event);
}

function recalc_student_grade(event, course) {
    mp_grade_inputs = $('input[id^=id_grade_' + course + ']');
    ytd_input = $('input[id=id_coursefinalform_' + course + ']');
    recalc_ytd_grade(mp_grade_inputs, ytd_input);
    mark_change(event);
}
