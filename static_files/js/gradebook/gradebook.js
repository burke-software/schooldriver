$(document).ready(function() {
    sh_highlightDocument();

    $(".tableDiv").each(function() {
        var Id = $(this).get(0).id;
        
        window_width = $(window).width()
        window_height = $(window).height()
        
        var maintbheight = window_height - 200;
        var maintbwidth = window_width - 300;

        $("#" + Id + " .FixedTables").fixedTable({
            width: maintbwidth,
            height: maintbheight,
            fixedColumns: 1,
            classHeader: "fixedHead",
            classFooter: "fixedFoot",
            classColumn: "fixedColumn",
            fixedColumnWidth: 175,
            outerId: Id,
            Contentbackcolor: "#FFFFFF",
            Contenthovercolor: "#F3F3F3",
            fixedColumnbackcolor:"#FFF",
            fixedColumnhovercolor:"#F3F3F3"
        });
    });
    
    $("#id_benchmark").multiselect();

    // Show item details when hovering over column header
    $(".assignment :not(.forall)").tooltip({
        bodyHandler: function() {
            var item_id = $(this).attr("item_id");
            var tipHere = $("<div>Loading...</div>");
            $.get("ajax_get_item_tooltip/" + item_id + "/", function(data) {
               tipHere.html(data);
            });
            return tipHere;
        }
    });
});

function submit_filter_form(form){
    $(form).submit();
}

function select_cell(event){
    // User clicks or navigates to a cell.
    if ($(event.target).is("td")) {
        make_into_input($(event.target).children('div'));
    } else if ($(event.target).is("div")) {
        make_into_input($(event.target));
    }
}

function make_into_input(element){
    // Make text grade into input for grade entry
    value = element.text(); 
    parent = $(element).parent('td');
    $(element).replaceWith('<input onblur="mark_change(event)" onkeydown="return keyboard_nav(event)" class="grade_input" prev_value="'+value+'" value="'+value+'"/>');
    $(parent).children('input').focus();
    $(parent).children('input').select();
}

function mark_change(event) {
    // Mark a changed grade. It will save then come back as save success.
    // OMG use var or variables will be global
    var prev_value = $(event.target).attr('prev_value');
    var cur_value = $(event.target).val()
    if (prev_value != cur_value) {
        $(event.target).removeClass('save_success');
        $(event.target).addClass('saving');
        var mark_id = $(event.target).parents('td').attr('id').replace(/^tdc\d+_r\d+_mark(\d+)$/, '$1').trim()
        var row = $(event.target).parents('td').attr('id').replace(/^tdc\d+_r(\d+)_.*$/, '$1').trim();
        var average_cell = $('#average' + row)
        average_cell.children().removeClass('save_success');
        average_cell.children().addClass('saving');
        $.post(  
          "../../gradebook/ajax_save_grade/",
          {mark_id: mark_id, value: cur_value},
          function(data) {
            if (data.success == "SUCCESS") {
                var new_value = data.value;
                $(event.target).replaceWith('<div class="save_success">' + new_value + '</div>');
                average_cell.html('<div class="save_success">' + data.average + '</div>');
            }
          }, "json"  
        )
        .error(function() {
                $(event.target).replaceWith('<div class="save_failure">' + prev_value + '</div>');
            }
        );
    } else {
        $(event.target).replaceWith('<div>' + $(event.target).val() + '</div>');
    }
}

function get_new_assignment_form(event){
    // Get a new assignment form to display of modal overlay
    $.post(
        "ajax_get_item_form/",
        function(data){  
            $("#new_assignment_form").html(data);
        }  
    ); 
    $("#new_assignment_form").overlay({
            top: '3',
            fixed: false
        });
    $("#new_assignment_form").overlay().load();
}

function get_edit_assignment_form(event){
    // Get a new assignment form to display of modal overlay
    item_id = $(event.target).attr('item_id');
    $.post(
        "ajax_get_item_form/" + item_id + "/",
        function(data){
            $("#new_assignment_form").html(data);
        }
    ); 
    $("#new_assignment_form").overlay({
            top: '3',
            fixed: false
        });
    $("#new_assignment_form").overlay().load();
}

function get_new_demonstration_form(event){
    // Get a new demonstration form to display of modal overlay
    $.post(
        "ajax_get_demonstration_form/",
        function(data){  
            $("#new_demonstration_form").html(data);
        }  
    ); 
    $("#new_demonstration_form").overlay({
            top: '3',
            fixed: false
        });
    $("#new_demonstration_form").overlay().load();
}

function get_edit_demonstration_form(event){
    // Get a new demonstration form to display of modal overlay
    demonstration_id = $(event.target).data('demonstration_id');
    if(demonstration_id == undefined) {
        // bloody hell event bubbling
        demonstration_id = $(event.target).parents('[data-demonstration_id]').data('demonstration_id');
    }
    $.post(
        "ajax_get_demonstration_form/" + demonstration_id + "/",
        function(data){
            $("#new_demonstration_form").html(data);
        }
    ); 
    $("#new_demonstration_form").overlay({
            top: '3',
            fixed: false
        });
    $("#new_demonstration_form").overlay().load();
}

function show_student_overlay(event) {
    student_id = event.target.id.replace(/^student(\d+)$/, '$1').trim();
    $.post(
        "ajax_get_student_info/" + student_id + "/",
        function(data){
            $("#student_info_overlay").html(data);
        }
    ); 
    $("#student_info_overlay").overlay({
            top: '3',
            fixed: false
        });
    $("#student_info_overlay").overlay().load();
}

function show_fill_all_form(event) {
    event.stopPropagation();
    object_id = $(event.target).data('demonstration_id');
    object_type = 'demonstration';
    if(object_id == undefined) {
        // bloody hell event bubbling
        object_id = $(event.target).parents('[data-demonstration_id]').data('demonstration_id');
    }
    if(object_id == undefined) {
        // still? then this isn't a demonstration
        object_id = $(event.target).parents('[item_id]').attr('item_id');
        object_type = 'item';
    }
    $.post(
        "ajax_get_fill_all_form/" + object_type + "/" + object_id + "/",
        function(data){
            $("#fill_all_form").html(data);
        }
    );
    $("#fill_all_form").overlay({
            top: '3',
            fixed: false
        });
    $("#fill_all_form").overlay().load();
}

function handle_form_fragment_submit(form) {

    // Handle submit for an assignment with ajax
    form_data = $(form).serialize();
    item_id = $(form).attr('item_id');
    if (item_id == 'None') {
        url = "ajax_get_item_form/"
    } else {
        url = "ajax_get_item_form/" + item_id + "/"
    }
    $.post(
        url,
        form_data,
        function(data){
            if ( data == "SUCCESS" ){
                location.reload();
            } else {
                $("#new_assignment_form").html(data);
            }
        }  
    );
    return false;
}

function handle_demonstration_form_fragment_submit(form) {

    // Handle submit for a demonstration with ajax
    form_data = $(form).serialize();
    demonstration_id = $(form).attr('demonstration_id');
    if (demonstration_id == 'None') {
        url = "ajax_get_demonstration_form/"
    } else {
        url = "ajax_get_demonstration_form/" + demonstration_id + "/"
    }
    $.post(
        url,
        form_data,
        function(data){
            if ( data == "SUCCESS" ){
                location.reload();
            } else {
                $("#new_demonstration_form").html(data);
            }
        }  
    );
    return false;
}

function handle_fill_all_form_fragment_submit(form) {

    // Handle overlay form submit with ajax
    form_data = $(form).serialize();
    $.post(
        $(form).attr('action'),
        form_data,
        function(data){
            if ( data == "SUCCESS" ){
                location.reload();
            } else {
                $("#fill_all_form").html(data);
            }
        }  
    );
    return false;
}
function confirm_assignment_delete(item_id){
    // stupid warning. not all categories have demonstrations. for those that do, the warning isn't scary enough.
    if (confirm("WARNING! *ALL* DEMONSTRATIONS OF THIS ASSIGNMENT WILL BE DELETED! Are you sure you want to delete this assignment?")) {
        $.post(
            "ajax_get_item_form/" + item_id + "/delete/",
            function(data){
                if ( data == "SUCCESS" ){
                    location.reload();
                } else {
                    alert("Unexpected error");
                }
            }  
        );
        
    }
    return false;
}

function confirm_demonstration_delete(demonstration_id){
    // another stupid warning that will confuse people
    if (confirm("Are you sure you want to delete this demonstration?")) {
        $.post(
            "ajax_get_demonstration_form/" + demonstration_id + "/delete/",
            function(data){
                if ( data == "SUCCESS" ){
                    location.reload();
                } else {
                    alert("Unexpected error");
                }
            }  
        ) /*.error(alert("The server refused to delete the demontration."));*/
        // TODO: just return HTTP errors if there's a problem, and then use .error() instead of checking for SUCCESS. Without .error(), the request just hangs, which is sloppy but okay for now.
        
    }
    return false;
}

function keyboard_nav(event) {
    key = event.which;
    if (key == 13 || key == 40 || key == 38 || key == 37 || key == 39) {
        // jnm 20120912 we're leaving this cell, so trigger mouseleave to remove highlighting
        $(event.target).closest('td').trigger('mouseleave')
        column = $(event.target).parents('td').attr('id').replace(/^tdc(\d+)_.*$/, '$1').trim();
        row = $(event.target).parents('td').attr('id').replace(/^tdc\d+_r(\d+)_.*$/, '$1').trim();
        
        var selected_id = 'td[id^=td';
        if(key == 13 || key == 40) { // Down
            selected_id += 'c' + column + '_r' + (parseInt(row)+1);
        } else if (key == 38) { // Up
            selected_id += 'c' + column + '_r' + (parseInt(row)-1);
        } else if (key == 37) { // Left
            selected_id += 'c' + (parseInt(column)-1) + '_r' + row;
        } else if (key == 39) { // Right
            selected_id += 'c' + (parseInt(column)+1) + '_r' + row;
        }
        selected_id += '_]';
        selected_element = $(selected_id);
        make_into_input($(selected_element).children('div'));
        $(selected_element).children('input').focus();
        $(selected_element).children('input').select();
        // jnm 20120912 trigger :hover highlighting of newly focused cell
        $(selected_element).trigger('mouseenter');
        return false;
    }
}
