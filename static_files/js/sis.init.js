if ($(".multiselect").is('*')) {
    $(".multiselect").css('min-height', '400px').css('min-width', '400px').multiselect({
        position: {
            my: 'left bottom',
            at: 'left top'
        },
        height: 600,
    });
}
if ($(".simple_multiselect").is('*')) {
    $(".simple_multiselect").simple_multiselect();
}

if ($(".datepicker,.vDateField").is('*')) { $(".datepicker,.vDateField").datepicker(); }
