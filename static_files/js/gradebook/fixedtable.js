(function($) {
    // ***********************************************
    //The main fixedTable function
    $.fn.fixedTable = function(opts) {
        //default options defined in $.fn.fixedTable.defaults - at the bottom of this file.
        var options = $.extend({}, $.fn.fixedTable.defaults, opts);
        var mainid = "#" + options.outerId;
        var tbl = this;
        var layout = buildLayout(tbl, opts);
        //see the buildLayout() function below

        //we need to set the width (in pixels) for each of the tables in the fixedContainer area
        //but, we need to subtract the width of the fixedColumn area.
        var w = options.width - options.fixedColumnWidth;
        //sanity check
        if (w <= 0) { w = options.width; }

        $(".fixedContainer", layout).width(w);

        $(".fixedContainer ." + options.classHeader, layout).css({
            width: (w) + "px",
            "float": "left",
            "overflow": "hidden"
        });

        $(".fixedContainer .fixedTable", layout).css({
            "float": "left",
            width: (w) + "px",
            /* if overflow-x is auto, then either the last student's name is partially cut off, or the names don't align properly with the grades */
            /* forcing a horizontal scrollbar fixes #42 */
            "overflow-x": "scroll",
            "overflow-y": "auto"
        });
        $(".fixedContainer", layout).css({
            width: (w) + "px",
            "float": "left"
        });    //adjust the main container to be just larger than the fixedTable

        $(".fixedContainer ." + options.classFooter, layout).css({
            width: (w) + "px",
            "float": "left",
            "overflow": "hidden"
        });
        $("." + options.classColumn + " > .fixedTable", layout).css({
            "width": options.fixedColumnWidth,
            "overflow": "hidden",
            "border-collapse": $(tbl).css("border-collapse"),
            "padding": "0"
        });

        $("." + options.classColumn, layout).width(options.fixedColumnWidth);
        $("." + options.classColumn, layout).height(options.height);
        $("." + options.classColumn + " ." + options.classHeader + " table tbody tr td", layout).width(options.fixedColumnWidth);
        $("." + options.classColumn + " ." + options.classFooter + " table tbody tr td", layout).width(options.fixedColumnWidth);

        //adjust the table widths in the fixedContainer area
        var fh = $(".fixedContainer > ." + options.classHeader + " > table", layout);
        var ft = $(".fixedContainer > .fixedTable > table", layout);
        var ff = $(".fixedContainer > ." + options.classFooter + " > table", layout);

        var maxWidth = fh.width();
        if (ft.length > 0 && ft.width() > maxWidth) { maxWidth = ft.width(); }
        if (ff.length > 0 && ff.width() > maxWidth) { maxWidth = ff.width(); }


        if (fh.length) { fh.width(maxWidth); }
        if (ft.length) { ft.width(maxWidth); }
        if (ff.length) { ff.width(maxWidth); }

        //adjust the widths of the fixedColumn header/footer to match the fixed columns themselves
        $("." + options.classColumn + " > ." + options.classHeader + " > table > tbody > tr:first > td", layout).each(function(pos) {
            var tblCell = $("." + options.classColumn + " > .fixedTable > table > tbody > tr:first > td:eq(" + pos + ")", layout);
            var tblFoot = $("." + options.classColumn + " > ." + options.classFooter + " > table > tbody > tr:first > td:eq(" + pos + ")", layout);
            var maxWidth = $(this).width();
            if (tblCell.width() > maxWidth) { maxWidth = tblCell.width(); }
            if (tblFoot.length && tblFoot.width() > maxWidth) { maxWidth = tblFoot.width(); }
            $(this).width(maxWidth);
            $(tblCell).width(maxWidth);
            if (tblFoot.length) { $(tblFoot).width(maxWidth); }
        });


        //set the height of the table area, minus the heights of the header/footer.
        // note: we need to do this after the other adjustments, otherwise these changes would be overwrote
        var h = options.height - parseInt($(".fixedContainer > ." + options.classHeader, layout).height()) - parseInt($(".fixedContainer > ." + options.classFooter, layout).height());
        //sanity check
        if (h < 0) { h = options.height; }
        $(".fixedContainer > .fixedTable", layout).height(h);
        $("." + options.classColumn + " > .fixedTable", layout).height(h);

        //Adjust the fixed column area if we have a horizontal scrollbar on the main table
        // - specifically, make sure our fixedTable area matches the main table area minus the scrollbar height,
        //   and the fixed column footer area lines up with the main footer area (shift down by the scrollbar height)
        var h = $(".fixedContainer > .fixedTable", layout)[0].offsetHeight - 16;
        $("." + options.classColumn + " > .fixedTable", layout).height(h);  //make sure the row area of the fixed column matches the height of the main table, with the scrollbar

        // Apply the scroll handlers
        $(".fixedContainer > .fixedTable").scroll(function(event) { handleScroll(mainid, options, event); });
        $("." + options.classColumn + " > .fixedTable").scroll(function(event) { handleScroll(mainid, options, event); });
        $(".fixedContainer > ." + options.classHeader).scroll(function(event) { handleScroll(mainid, options, event); });
        $(".fixedContainer > ." + options.classFooter).scroll(function(event) { handleScroll(mainid, options, event); });
        //the handleScroll() method is defined near the bottom of this file.

        //$.fn.fixedTable.adjustSizes(mainid);
        adjustSizes(options);
        return tbl;
    }

    function buildLayout(src, options) {
        //create a working area and add it just after our table.
        //The table will be moved into this working area
        var area = $("<div class=\"fixedArea\"></div>").appendTo($(src).parent());

        //fixed column items
        var fc = $("<div class=\"" + options.classColumn + "\" style=\"float: left;\"></div>").appendTo(area);
        var fch = $("<div class=\"" + options.classHeader + "\"></div>").appendTo(fc);
        var fct = $("<div class=\"fixedTable\"></div>").appendTo(fc);
        var fcf = $("<div class=\"" + options.classFooter + "\"></div>").appendTo(fc);

        //fixed container items
        var fcn = $("<div class=\"fixedContainer\"></div>").appendTo(area);
        var fcnh = $("<div class=\"" + options.classHeader + "\"></div>").appendTo(fcn);
        var fcnt = $("<div class=\"fixedTable\"></div>").appendTo(fcn);
        var fcnf = $("<div class=\"" + options.classFooter + "\"></div>").appendTo(fcn);

        //create the fixed column area
        if (options.fixedColumns > 0 && !isNaN(options.fixedColumns)) {
            buildFixedColumns(src, "thead", options.fixedColumns, fch);
            buildFixedColumns(src, "tbody", options.fixedColumns, fct);
            buildFixedColumns(src, "tfoot", options.fixedColumns, fcf);
            //see the buildFixedColumns() function below
        }

        //Build header / footer areas
        buildFixedTable(src, "thead", fcnh);
        buildFixedTable(src, "tfoot", fcnf);
        //see the buildFixedTable() function below

        //Build the main table
        //we'll cheat here - the src table should only be a tbody section, with the remaining columns, 
        //so we'll just add it to the fixedContainer table area.
        fcnt.append(src);
        return area;
    }

    /* ******************************************************************** */
    // duplicate a table section (thead, tfoot, tbody), but only for the desired number of columns
    function buildFixedColumns(src, section, cols, target) {
        //TFOOT - get the needed columns from the table footer
        if ($(section, src).length) {
            var colHead = $("<table></table>").appendTo(target);

            //If we have a thead or tfoot, we're looking for "TH" elements, otherwise we're looking for "TD" elements
            var cellType = "td";  //deafault cell type
            if (section.toLowerCase() == "thead" || section.toLowerCase() == "tfoot") { cellType = "th"; }

            //check each of the rows in the thead
            $(section + " tr", src).each(function() {
                var tr = $("<tr></tr>").appendTo(colHead);
                $(cellType + ":lt(" + cols + ")", this).each(function() {
                    $("<td>" + $(this).html() + "</td>").addClass(this.className).attr("id", this.id).appendTo(tr);
                    //Note, we copy the class names and ID from the original table cells in case there is any processing on them.
                    //However, if the class does anything with regards to the cell size or position, it could mess up the layout.

                    //Remove the item from our src table.
                    $(this).remove();
                });
            });
        }
    }

    /* ******************************************************************** */
    // duplicate a table section (thead, tfoot, tbody)
    function buildFixedTable(src, section, target) {
        if ($(section, src).length) {
            var th = $("<table></table>").appendTo(target);
            var tr = null;

            //If we have a thead or tfoot, we're looking for "TH" elements, otherwise we're looking for "TD" elements
            var cellType = "td";  //deafault cell type
            if (section.toLowerCase() == "thead" || section.toLowerCase() == "tfoot") { cellType = "th"; }

            $(section + " tr", src).each(function() {
                var tr = $("<tr></tr>").appendTo(th);
                $(cellType, this).each(function() {
                    $("<td>" + $(this).html() + "</td>").appendTo(tr);
                });

            });
            //The header *should* be added to our head area now, so we can remove the table header
            $(section, src).remove();
        }
    }

    // ***********************************************
    // Handle the scroll events
    function handleScroll(mainid, options, event) {
        // jnm 20120918
        // handle all scrolling, even that caused by ctrl+f on elements without scrollbars!
        var tableArea = $(mainid + " .fixedContainer > .fixedTable");
        var fixedColumn = $(mainid + " ." + options.classColumn + " > .fixedTable");
        var header = $(mainid + " .fixedContainer > ." + options.classHeader);
        var footer = $(mainid + " .fixedContainer > ." + options.classFooter);
        var target = $(event.target);
        var x = target.scrollLeft();
        var y = target.scrollTop();
        if(target.is(tableArea)) {
            if(header.scrollLeft() != x)
                header.scrollLeft(x);
            if(footer.scrollLeft() != x)
                footer.scrollLeft(x);
            if(fixedColumn.scrollTop() != y)
                fixedColumn.scrollTop(y);
        }
        else if(target.is(fixedColumn)) {
            // FF 15 bogs down if we do this unconditionally
            if(tableArea.scrollTop() != y)
                tableArea.scrollTop(y);
        }
        else if(target.is(header)) {
            if(tableArea.scrollLeft() != x)
                tableArea.scrollLeft(x);
            if(footer.scrollLeft() != x)
                footer.scrollLeft(x);
        }
        else if(target.is(footer)) {
            if(tableArea.scrollLeft() != x)
                tableArea.scrollLeft(x);
            if(header.scrollLeft() != x )
                header.scrollLeft(x);
        }
    }

    // ***********************************************
    //  Reset the heights of the rows in our fixedColumn area
    function adjustSizes(options) {

        var Id = options.outerId;
        var maintbheight = options.height;
        var backcolor = options.Contentbackcolor;
        var hovercolor = options.Contenthovercolor;
        var fixedColumnbackcolor = options.fixedColumnbackcolor;
        var fixedColumnhovercolor = options.fixedColumnhovercolor;

        // row height
        $("#" + Id + " ." + options.classColumn + " .fixedTable table tbody tr").each(function(i) {
            var maxh = 0;
            var fixedh = $(this).height();
            var contenth = $("#" + Id + " .fixedContainer .fixedTable table tbody tr").eq(i).height();
            if (contenth > fixedh) {
                maxh = contenth;
            }
            else {
                maxh = fixedh;
            }
            //$(this).height(contenth);
            $(this).children("td").height(maxh);
            $("#" + Id + " .fixedContainer .fixedTable table tbody tr").eq(i).children("td").height(maxh);
        });

        //adjust the cell widths so the header/footer and table cells line up
        var htbale = $("#" + Id + " .fixedContainer ." + options.classHeader + " table");
        var ttable = $("#" + Id + " .fixedContainer .fixedTable table");
        var ccount = $("#" + Id + " .fixedContainer ." + options.classHeader + " table tr:first td").size();
        var widthArray = new Array();
        var totall = 0;

        $("#" + Id + " .fixedContainer ." + options.classHeader + " table tr:first td").each(function(pos) {
            var cwidth = $(this).width();
            $("#" + Id + " .fixedContainer .fixedTable table tbody td").each(function(i) {
                if (i % ccount == pos) {
                    if ($(this).width() > cwidth) {
                        cwidth = $(this).width();
                    }
                }
            });
            widthArray[pos] = cwidth;
            totall += (cwidth + 2);
        });

        $("#" + Id + " .fixedContainer ." + options.classHeader + " table").width(totall + 100);
        $("#" + Id + " .fixedContainer .fixedTable table").width(totall + 100);
        $("#" + Id + " .fixedContainer ." + options.classFooter + " table").width(totall + 100);
        for (i = 0; i < widthArray.length; i++) {
            $("#" + Id + " .fixedContainer ." + options.classHeader + " table tr td").each(function(j) {
                if (j % ccount == i) {
                    $(this).attr("width", widthArray[i] + "px");
                }
            });

            $("#" + Id + " .fixedContainer .fixedTable table tr td").each(function(j) {
                if (j % ccount == i) {
                    $(this).attr("width", widthArray[i] + "px");
                }
            });

            $("#" + Id + " .fixedContainer ." + options.classFooter + " table tr td").each(function(j) {
                if (j % ccount == i) {
                    $(this).attr("width", widthArray[i] + "px");
                }
            });
        }

        // mouse in/out fixedColumn's fixedtable, change background color.
        $("#" + Id + " ." + options.classColumn + " .fixedTable table tr").each(function(i) {
            $(this).mouseover(function() {
                $(this).children("td").css({
                    "background-color": fixedColumnhovercolor
                });
                var obj = $("#" + Id + " .fixedContainer .fixedTable table tr").eq(i);
                obj.children("td").css({
                    "background-color": hovercolor
                });
                obj.children("td").children("pre").css({
                    "background-color": hovercolor
                });
            });
            $(this).mouseout(function() {
                $(this).children("td").css({
                    "background-color": fixedColumnbackcolor
                });
                var obj = $("#" + Id + " .fixedContainer .fixedTable table tr").eq(i);
                obj.children("td").css({
                    "background-color": backcolor
                });
                obj.children("td").children("pre").css({
                    "background-color": backcolor
                });
            });
        });

        // mouse in/out fixedContainer's fixedtable, change background color.
        $("#" + Id + " .fixedContainer .fixedTable table tr").each(function(i) {
            $(this).mouseover(function() {
                $(this).children("td").css({
                    "background-color": hovercolor
                });
                $(this).children("td").children("pre").css({
                    "background-color": hovercolor
                });
                var obj = $("#" + Id + " ." + options.classColumn + " .fixedTable table tr").eq(i);
                obj.children("td").css({
                    "background-color": fixedColumnhovercolor
                });

            });
            $(this).mouseout(function() {
                $(this).children("td").css({
                    "background-color": backcolor
                });
                $(this).children("td").children("pre").css({
                    "background-color": backcolor
                });
                var obj = $("#" + Id + " ." + options.classColumn + " .fixedTable table tr").eq(i);
                obj.children("td").css({
                    "background-color": fixedColumnbackcolor
                });
            });
        });

        var contenttbH = $("#" + Id + " .fixedContainer .fixedTable table").height();
        if (contenttbH < maintbheight) {
            $("#" + Id + " ." + options.classColumn + " .fixedTable").height(contenttbH + 20);
            $("#" + Id + " .fixedContainer .fixedTable").height(contenttbH + 20);

            $("#" + Id + " .fixedContainer ." + options.classHeader).width($("#" + Id + " .fixedContainer ." + options.classHeader).width());
            $("#" + Id + " .fixedContainer ." + options.classFooter).width($("#" + Id + " .fixedContainer ." + options.classHeader).width());
        }
        else {
            //offset the footer by the height of the scrollbar so that it lines up right.
            $("#" + Id + " ." + options.classColumn + " > ." + options.classFooter).css({
                "position": "relative",
                "top": 16
            });
        }
    }

})(jQuery);
