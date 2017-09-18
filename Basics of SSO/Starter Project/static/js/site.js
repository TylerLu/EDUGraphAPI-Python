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




});
