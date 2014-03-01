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
});
