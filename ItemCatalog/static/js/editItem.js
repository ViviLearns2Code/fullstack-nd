$(document).ready(function() {
    /* template for resources */
    var iNumID = 0;
    var aDelRsrcDB = [];
    var generateTemplate = function() {
        var templ = `<li class="rsrc-li">
                	<div class="rsrc-box">
            			<form class="form-align">
                    	<p>
                    	<label for="gen_rsrc_${iNumID}_name" class="mandatory">Name</label>
                    	<input type="text" id="gen_rsrc_${iNumID}_name" value="">
                    	</p>
                    	<p>
                    	<label for="gen_rsrc_${iNumID}_url">URL</label>
                    	<input type="text" id="gen_rsrc_${iNumID}_url" value="">
                		<p>
                		</form>
	                	<div class="rsrc-box-del">
    	                	<i class="fa fa-minus-square-o" aria-hidden="true"></i>
                            <span class="rsrc-del">Remove resource</span>
        	    		</div>
                	</div>
            	</li>`;
        iNumID += 1;
        return templ;
    }
    var getData = function() {
        var data = {};
        data.name = $("#itm-name").val();
        data.descr = $("#itm-desc").val();
        data.done = $("#itm-done").is(":checked");
        data.rsrc = [];
        data.delRsrc = aDelRsrcDB;
        var rsrc = {};
        var $rsrc = $("#rsrc-list").find("li");
        $rsrc.each(function(idx, elem) {
            // returned results are in document order
            // check if rsrc existed before
            var $rsrcBox = $($(elem).children(".rsrc-box")[0]);
            var $name = $($rsrcBox.find("input")[0]);
            var $url = $($rsrcBox.find("input")[1]);
            rsrc = {};
            if ($name.attr("data-orgval") && $url.attr("data-orgval")!==undefined) {
                var oldName = $name.attr("data-orgval");
                var newName = $name.val();
                var oldURL = $url.attr("data-orgval");
                var newURL = $url.val();
                if (oldName !== newName || oldURL !== newURL) {
                    debugger;
                    rsrc.id = $name.attr("id").split("_")[1];
                    rsrc.oldName = oldName;
                    rsrc.newName = newName;
                    rsrc.oldURL = oldURL;
                    rsrc.newURL = newURL;
                    data.rsrc.push(rsrc);
                }
            } else if ($name.val() !== "") {
                // new rsrc
                rsrc.id = undefined;
                rsrc.oldName = undefined;
                rsrc.oldURL = undefined;
                rsrc.newName = $name.val();
                rsrc.newURL = $url.val();
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
    var onDelRsrcDB = function(e) {
        var id = $(e.target).closest("li").attr("data-id");
        aDelRsrcDB.push(id);
        $($(e.target).closest(".rsrc-li")[0]).remove();
    }
    var onSaveItem = function(e) {
        var data = getData();
        if (!checkData(data)) {
            // error handling
            $("#errorMsgItmSave").html("Could not save");
            return;
        }
        debugger;
        var url = "/cat/" + categoryId + "/item/" + itemId + "/edit/";
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
                aDelRsrcDB.length = 0;
                window.location.href = "/cat/" + categoryId + "/item/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            $("#errorMsgItmSave").html(jqXHR.responseJSON.error);
        });
    };
    $("#addRsrc").on("click", onAddRsrc);
    $("#saveItem").on("click", onSaveItem);
    $("#rsrc-list").find(".rsrc-db-del").on("click", onDelRsrcDB);
});