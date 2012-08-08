function select_cell(event){
    if ($(event.target).is("td")) {
        make_into_input($(event.target).children('div'));
    } else if ($(event.target).is("div")) {
        make_into_input($(event.target));
    }
    
    
}

function make_into_input(element){
    parent = $(element).parent('td');
    $(element).replaceWith('<input onchange="mark_change(event)" onkeydown="return keyboard_nav(event)" class="grade_input" value="90"/>');
    $(parent).children('input').focus();
    $(parent).children('input').select();
}

function mark_change(event) {
    $(event.target).addClass('saving');
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