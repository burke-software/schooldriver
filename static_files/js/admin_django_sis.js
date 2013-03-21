$(document).ready(function() {
    $('a.menu-collapse-handler').click(function () {
        $('li.grp-user-options-container.grp-open').removeClass('grp-open');
        $('li.grp-user-options-container.grp-open').addClass('grp-closed');
        if ( $(this).parent().hasClass('grp-closed') ) {
            $(this).parent().addClass('grp-open');
            $(this).parent().removeClass('grp-closed');
        } else {
            $(this).parent().addClass('grp-closed');
            $(this).parent().removeClass('grp-open');
        }
    });
});