function submit_form(){
    $(":input:not(.changed)").attr("disabled", "disabled");
}

function toggle_comments(){
    $('.comment').toggle();
}

function mark_change(event) {
    // Change color to show change
    $(event.target).addClass('changed');
}

function keyboard_nav(event) {
    key = event.which;
    if (key == 13 || key == 40 || key == 38 || key == 37 || key == 39) {
        column = $(event.target).parents('td').attr('class').replace(/row_\d*/, '').replace(/column_/,'').trim();
        row = $(event.target).parents('td').attr('class').replace(/^column_\d* row_/, '').trim();
        if(key == 13 || key == 40) { // Down
            $('td.column_' + column + '.row_' + (parseInt(row)+1)).children('input').select();
        } else if (key == 38) { // Up
            $('td.column_' + column + '.row_' + (parseInt(row)-1)).children('input').select();
        } else if (key == 37) { // Left
            $('td.column_' + (parseInt(column)-1) + '.row_' + row).children('input').select();
        } else if (key == 39) { // Right
            $('td.column_' + (parseInt(column)+1) + '.row_' + row).children('input').select();
        }
        return false;
    }
}

function recalc_grade(event, course) {
    final_input = $('input[id=id_coursefinalform_' + course + ']');
    if (final_input.attr('class') != 'grade_form final_override') {
        grade = 0;
        num_mp_grades = 0;
        
        add_total = true;
        $('input[id^=id_grade_' + course + ']').each(
            function(i){
                mp_grade_value = $(this).val()
                mp_grade = parseFloat(mp_grade_value);
                if (!(isNaN(mp_grade))) {
                        grade += mp_grade;
                        num_mp_grades += 1;
                } else if (mp_grade_value == "I" || mp_grade_value == "i") {
                    // If there is an I, the final should be just I
                    final_input.val("I");
                    add_total = false;
                    return;
                }
            }
        )
        
        if (add_total) {
            grade = grade / num_mp_grades;
        grade = Math.round(grade*100)/100;
        final_input.val(grade);
        }
    }
    mark_change(event);
}