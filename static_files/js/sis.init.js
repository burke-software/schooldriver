if ($(".multiselect").is('*')) {
    $(".multiselect").multiselect({
        position: {
            my: 'left bottom',
            at: 'left top'
        },
        height: 600,
    }).multiselectfilter();
}
if ($(".datepicker").is('*')) { $(".datepicker").datepicker(); }
