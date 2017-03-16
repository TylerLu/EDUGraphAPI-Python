/*   
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
 */
$(document).ready(function () {
    $("#userinfolink").click(function (evt) {
        evt.stopPropagation ? evt.stopPropagation() : evt.cancelBubble = true;
        $("#userinfoContainer").toggle();
        $("#caret").toggleClass("transformcaret");
    });
    $(document).click(function () {
        $("#userinfoContainer").hide();
        $("#caret").removeClass("transformcaret");

    });

    $('.demo-helper-control .header').on('click', function () {
        console.log(12321);
        console.log($(this).closest('.demo-helper-control').html());
        $(this).closest('.demo-helper-control').toggleClass('collapsed');
    });

    $('.message-container').fadeOut(5000);
});