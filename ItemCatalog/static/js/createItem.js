$(document).ready(function() {
    /* template for resources */
    var num_id = 0;
    var generateTemplate = function() {
        var templ = `<li class="rsrc-li">
                    <div class="rsrc-box">
                        <form class="form-align">
                        <p>
                        <label for="gen_rsrc_${num_id}_name" class="mandatory">Name</label>
                        <input type="text" id="gen_rsrc_${num_id}_name" value=""><br>
                        </p>
                        <p>
                        <label for="gen_rsrc_${num_id}_url">URL</label>
                        <input type="text" id="gen_rsrc_${num_id}_url" value="">
                        </p>
                        </form>
                        <div class="rsrc-box-del">
                            <i class="fa fa-minus-square-o" aria-hidden="true"></i>
                            <span class="rsrc-del">Remove resource</span>
                        </div>
                    </div>
                </li>`;
        num_id += 1;
        return templ;
    }

    var getData = function() {
        var data = {};
        data.name = $("#itm-name").val();
        data.descr = $("#itm-desc").val();
        data.done = $("#itm-done").is(":checked");
        data.rsrc = [];
        var rsrc = {};
        var $rsrc = $("#rsrc-list").find("li");
        $rsrc.each(function(index, elem) {
            debugger;
            var $rsrcBox = $($(elem).children(".rsrc-box")[0]);
            var $name = $($rsrcBox.find("input")[0]);
            var $url = $($rsrcBox.find("input")[1]);
            rsrc = {};
            rsrc.name = $name.val();
            rsrc.url = $url.val();
            if (rsrc.name !== "" && rsrc.name) {
                data.rsrc.push(rsrc);
            }
        });
        return data;
    };
    var checkData = function(data) {
        if (data.name === "" || !data.name) {
            return false;
        }
        return true;
    }
    var onAddRsrc = function(e) {
        debugger;
        $newElem = $("#rsrc-list").append(generateTemplate());
        $rmvSpan = $newElem.children().last().find(".rsrc-del");
        $rmvSpan.on("click", onDelRsrc);
    };
    var onDelRsrc = function(e) {
        $($(e.target).closest(".rsrc-li")).remove();
    };
    var onCreateItem = function(e) {
        debugger;
        var data = getData();
        if (!checkData(data)) {
            // error handling
            $("#errorMsgItmSave").html("Could not save item");
            return;
        }
        var url = "/cat/" + categoryId + "/item/create/";
        saveItemReq = $.ajax({
            type: "POST",
            url: url,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            contentType: "application/json",
            processData: false,
            dataType: "json",
            data: JSON.stringify(data)
        });
        saveItemReq.then(function(result) {
            debugger;
            if (result) {
                console.log("Save successful!");
                window.location.href = "/cat/" + categoryId + "/item/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            $("#errorMsgItmSave").html(jqXHR.responseJSON.error);
        });
    };
    $("#addRsrc").on("click", onAddRsrc);
    $("#createItem").on("click", onCreateItem);
});