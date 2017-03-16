/*   
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
 */
BingMapHelper = {};
BingMapHelper.BingMap = {
    displayPin: function (latitude, longitude, bingMapKey) {
        var map = new Microsoft.Maps.Map(document.getElementById('myMap'), {
            credentials: bingMapKey,
            center: new Microsoft.Maps.Location(latitude, longitude),
            mapTypeId: Microsoft.Maps.MapTypeId.road,
            showMapTypeSelector: false,
            zoom: 10
        });
        var pushpin = new Microsoft.Maps.Pushpin(map.getCenter(), null);
        map.entities.push(pushpin);
    }
};

$(document).ready(function () {
    var bingMapKey = $("#BingMapKey").val();
    if (bingMapKey) {
        $(".bingMapLink").click(function (evt) {
            evt.stopPropagation ? evt.stopPropagation() : evt.cancelBubble = true;
            var lat = $(this).attr("lat");
            var lon = $(this).attr("lon");
            if (lat && lon) {
                BingMapHelper.BingMap.displayPin(lat, lon, bingMapKey);
                var offset = $(this).offset();
                $("#myMap").offset({ top: offset.top - 50, left: offset.left + 50 }).css({ width: "200px", height: "200px" }).show();
            }
        });
        $(document).click(function () {
            $("#myMap").offset({ top: 0, left: 0 }).hide();
        });
    }

});
