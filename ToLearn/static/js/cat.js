$(document).ready(function() {
    var Modal = function() {
        this.id = undefined;
        this.newName = undefined;
        this.oldName = undefined;
    };
    Modal.prototype = {
        setId: function(sId) {
            this.id = sId;
        },
        setNewName: function(sNewName) {
            this.newName = sNewName;
        },
        setOldName: function(sOldName) {
            this.oldName = sOldName;
        },
        reset: function() {
            this.id = undefined;
            this.newName = undefined;
            this.oldName = undefined;
        }
    };
    var modal = new Modal();
    var submitDelete = function() {
        var url = "/cat/" + modal.id + "/delete/";
        debugger;
        deleteCatReq = $.ajax({
            type: "POST",
            url: url,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            contentType: "application/json",
            processData: false
        });
        deleteCatReq.then(function(result) {
            debugger;
            if (result) {
                modal.reset();
                window.location.href = "/cat/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            debugger;
            $("#errorDelete").html(jqXHR.responseJSON.error);
        });
    };
    var submitCreate = function() {
        var url = "/cat/create/";
        var data = {
            "newName": modal.newName
        };
        if (data.newName === "" || !data.newName){
            $("#errorCreate").html("Please specify a name");
            return;
        }
        createCatReq = $.ajax({
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
        createCatReq.then(function(result) {
            debugger;
            if (result) {
                console.log("Create successful!");
                modal.reset();
                $("#modalCreate").toggleClass("modal-hide");
                window.location.href = "/cat/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            $("#errorCreate").html(jqXHR.responseJSON.error);
        });
    };
    var submitRename = function() {
        var url = "/cat/" + modal.id + "/edit/";
        var data = {
            "id": modal.id,
            "oldName": modal.oldName,
            "newName": modal.newName
        };
        if (data.newName === "" || !data.newName){
            $("#errorRename").html("Please specify a name");
            return;
        }
        renameCatReq = $.ajax({
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
        renameCatReq.then(function(result) {
            debugger;
            if (result) {
                console.log("Rename successful!");
                // reset rename modal
                modal.reset();
                $("#inputRename").val("");
                // close modal
                $("#modalRename").toggleClass("modal-hide");
                // redirect
                window.location.href = "/cat/";
            }
        }, function(jqXHR, textStatus, errorThrown) {
            debugger;
            $("#errorRename").html(jqXHR.responseJSON.error);
        });
    };
    $(".cat-rename").on("click", function(e) {
        // reset model data
        modal.reset();
        // identify category id
        var $cat = $(e.target).closest(".cat");
        var oldName = $cat.attr("data-name");
        var id = $cat.attr("data-id");
        modal.setId(id);
        modal.setOldName(oldName);
        var $input = $("#inputRename");
        $input.val(oldName);
        $("#modalRename").toggleClass("modal-hide");
    });
    $("#cancelRename").on("click", function(e) {
        // reset rename modal
        modal.reset();
        $("#errorRename").text("");
        $("#inputRename").val("");
        // close modal
        $("#modalRename").toggleClass("modal-hide");
    });
    $("#saveRename").on("click", function(e) {
        modal.setNewName($("#inputRename").val());
        // check if newName = oldName
        if (modal.newName !== modal.oldName) {
            submitRename();
        }
	else{
	    // no changes to save
            modal.reset();
            $("#inputRename").val("");
	    $("#modalRename").toggleClass("modal-hide");
	}
    });
    $("#addNewCat").on("click", function(e) {
        modal.reset();
        $("#modalCreate").toggleClass("modal-hide");
    });
    $("#cancelCreate").on("click", function(e) {
        modal.reset();
        $("#errorCreate").text("");
        $("#inputCreate").val("");
        $("#modalCreate").toggleClass("modal-hide");
    })
    $("#saveCreate").on("click", function(e) {
        modal.setNewName($("#inputCreate").val());
        // server side: check if category exists
        submitCreate();
    });
    $(".cat-delete").on("click", function(e) {
        var $cat = $(e.target).closest(".cat");
        var id = $cat.attr("data-id");
        modal.setId(id);
        $("#modalDelete").toggleClass("modal-hide");
    });
    $("#cancelDelete").on("click", function(e) {
        modal.reset()
        $("#errorDelete").text("");
        $("#modalDelete").toggleClass("modal-hide");
    })
    $("#saveDelete").on("click", function(e) {
        submitDelete();
    });
});
