function select_cell(event){
    if ($(event.target).is("td")) {
        make_into_input($(event.target).children('div'));
    } else if ($(event.target).is("div")) {
        make_into_input($(event.target));
    }
}

function make_into_input(element){
    value = 90
    parent = $(element).parent('td');
    $(element).replaceWith('<input onblur="mark_change(event)" onkeydown="return keyboard_nav(event)" class="grade_input" prev_value="'+value+'" value="'+value+'"/>');
    $(parent).children('input').focus();
    $(parent).children('input').select();
}

function mark_change(event) {
    $prev_value = $(event.target).attr('prev_value');
    if ( $prev_value != $(event.target).val() ) {
        $(event.target).removeClass('save_success');
        $(event.target).addClass('saving');
        $.post(  
          "gradebook/ajax_save_grade/",
          function(data){
            if (data == "SUCCESS") {
                $new_value = $(event.target).val();
                $(event.target).replaceWith('<div class="save_success">' + $new_value + '</div>');
            }
          }  
        );
    } else {
        $(event.target).replaceWith('<div>' + $(event.target).val() + '</div>');
    }
    
} 

function keyboard_nav(event) {
    key = event.which;
    if (key == 13 || key == 40 || key == 38 || key == 37 || key == 39) {
        column = $(event.target).parents('td').attr('id').replace(/_r\d*/, '').replace(/tdc/,'').trim();
        row = $(event.target).parents('td').attr('id').replace(/^tdc\d*_r/, '').trim();
        
        var selected_element;
        if(key == 13 || key == 40) { // Down
            selected_element = $('td#tdc' + column + '_r' + (parseInt(row)+1));
        } else if (key == 38) { // Up
            selected_element = $('td#tdc' + column + '_r' + (parseInt(row)-1));
        } else if (key == 37) { // Left
            selected_element = $('td#tdc' + (parseInt(column)-1) + '_r' + row);
        } else if (key == 39) { // Right
            selected_element = $('td#tdc' + (parseInt(column)+1) + '_r' + row);
        }
        make_into_input($(selected_element).children('div'));
        $(selected_element).children('input').focus();
        $(selected_element).children('input').select();
        return false;
    }
}