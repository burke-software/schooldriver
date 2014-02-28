$(document).ready(function() {
    $('a.menu-collapse-handler').click(function () {
        var open = false;
        if ( $(this).parent().hasClass('grp-closed') ) {
            open = true;
        }
        
        $('li.grp-user-options-container').removeClass('grp-open');
        $('li.grp-user-options-container').addClass('grp-closed');
        
        if ( open ) {
            $(this).parent().addClass('grp-open');
            $(this).parent().removeClass('grp-closed');
        } else {
            $(this).parent().addClass('grp-closed');
            $(this).parent().removeClass('grp-open');
        }
    });
    
    
    
    $("select[name=action]").change(function() {
        if ( $("option[value=export_simple_selected_objects]:selected").length ) {
            $.post(  
                "",  
                $("#grp-changelist-form").serialize(),  
                function(data){  
                    $("#admin_export_form").html(data);
                }  
            ); 
            $("#export_xls_form").addClass('active');
            return false;
        }
    });
});