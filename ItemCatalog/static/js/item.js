$(document).ready(function() {
    var submitDeleteItem = function(itemID) {
        var url = "/cat/" + categoryID + "/item/" + itemID + "/delete/";
        debugger;
        deleteItmReq = $.ajax({
            type: "POST",
            url: url,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            contentType: "application/json",
            processData: false
        });
        deleteItmReq.then(function(result) {
            debugger;
            if (result) {
                window.location.href = "/cat/" + categoryID + "/item/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            debugger;
            $("#errorItmDelete").html(jqXHR.responseJSON.error);
        });
    };
    $(".item-del").on("click", function(e) {
        var itemID = $(e.target).closest(".item").attr("data-id");
        submitDeleteItem(itemID);
        // prevent bubbling
        return false;
    });
    // accordion
    $("#item-list").find(".item-header").on("click", function(e) {
        debugger;
        if ($(e.target).closest(".item-btn")[0]) {
            return;
        }
        $(e.target).closest(".item").toggleClass("hide-content");
    });
    // filter completed items
    $("#hideDone").on("click", function() {
        $("[data-done='True']").toggleClass("hide-whole-item")
    });
});