/*   
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
 */
$(document).ready(function () {
    function bindShowDetail(tiles) {
        tiles.hover(function inFn(e) {
            $(this).children().last().show();
        }, function outFn(e) {
            $(this).children().last().hide();
        }).find(".detail #termdate").each(function (i, e) {
            var $e = $(e);
            var dateStr = $e.text();
            if (dateStr) {
                $e.text(moment.utc(dateStr).local().format('MMMM D YYYY'));
            }
        });
    };

    function hasSection(section, classes) {
        if (!(classes instanceof Array)) {
            return false;
        }
        var result = false;
        $.each(classes, function (i, s) {
            if (section.Email == s.Email) {
                return result = true;
            }
        });
        return result;
    }

    bindShowDetail($(".class-tiles .tile-container"));
    var tabname = '';
    if ($(".classes .filterlink-container .selected").length > 0) {
        tabname = $(".classes .filterlink-container .selected").attr("id");
    }
    showDemoHelper(tabname);


    $(".classes .filterlink-container .filterlink").click(function () {
        tabname = $(this).attr("id");
        showDemoHelper(tabname);
        search(true);
        var element = $(this);
        element.addClass("selected").siblings("a").removeClass("selected");
        var filterType = element.data("type");
        var tilesContainer = $(".classes .tiles-root-container");
        tilesContainer.removeClass(tilesContainer.attr("class").replace("tiles-root-container", "")).addClass(filterType + "-container");
    });

    $("#see-more  span").click(function () {
        search(true);
        var element = $(this);
        if (element.hasClass("disabled") || element.hasClass("nomore")) {
            return;
        }

        var schoolId = element.siblings("input#schoolid").val();
        var url = "/Schools/" + schoolId + "/Classes/Next";
        var nextLinkElement = element.siblings("input#nextlink");

        element.addClass("disabled");
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            data: { schoolId: schoolId, nextLink: nextLinkElement.val() },
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.error === "AdalException" || data.error === "Unauthorized") {
                    alert("Your current session has expired. Please click OK to refresh the page.");
                    window.location.reload(false);
                    return;
                }

                var tiles = element.parent().prev(".content");
                var newTiles = $();
                $.each(data.classes.value, function (i, c) {
                    var newTile = $('<div class="tile-container"></div>');
                    var tileContainer = newTile;
                    if (c.is_my) {
                        tileContainer = $('<a class="myclasslink" href="/Schools/' + schoolId + '/Classes/' + c.id + '"></a>').appendTo(newTile);
                    }
                    var tile = $('<div class="tile"><h5>' + c.display_name + '</h5><h2>' + c.code + '</h2></div>');
                    tile.appendTo(tileContainer);
                    var teachers = c.teachers.reduce(function (accu, cur) {
                        accu += '<h6>' + cur.display_name + '</h6>';
                        return accu;
                    }, '');
                    var tileDetail = $('<div class="detail" style="display: none;">' +
                                            '<h5>Course Number:</h5>' +
                                            '<h6>' + c.code + '</h6>' +
                                            '<h5>Teachers:</h5>' +
                                            teachers + 
                                            '<h5>Term Name:</h5>' +
                                            '<h6>' + c.term_name + '</h6>' +
                                            '<h5>Start/Finish Date:</h5>' +
                                            ((c.term_start_time || c.term_end_time) ?
                                            ('<h6><span id="termdate">' + c.term_start_time + '</span>' +
                                            '<span> - </span>' +
                                            '<span id="termdate">' + c.term_end_time + '</span>' +
                                            '</h6>') : '') +
                                        '</div>');
                    tileDetail.appendTo(newTile);
                    newTiles = newTiles.add(newTile);
                });
                newTiles.appendTo(tiles).hide().fadeIn("slow");
                bindShowDetail(newTiles);

                var newNextLink = data.classes.next_link;
                nextLinkElement.val(newNextLink);
                if (typeof (newNextLink) != "string" || newNextLink.length == 0) {
                    element.hide();
                }
                $(window).scrollTop($(document).height() - $(window).height())
            },
            complete: function () {
                element.removeClass("disabled");
            }
        });
    });

    $("#btnsearch").click(function () {
        search();
    });

    $('.txtsearch').on('keypress', function (e) {
        if (e.which === 13) {
            search();
        }
    });
    function search(isReset) {
        var queryString;
        if (isReset) {
            queryString = "";
            $(".txtsearch").val("");
        } else {
            queryString = $(".txtsearch").val();
        }
        if (queryString) {
            $(".tile-container h2").each(function () {
                if ($(this).text().search(new RegExp(queryString, "i")) < 0) {
                    $(this).closest(".tile-container").hide();
                } else {
                    $(this).closest(".tile-container").show();
                }
            });
        }
        else {
            $(".tile-container").show();
        }
    }
});
