$(document).ready(function() {
    var onSignIn = function() {
        auth2.grantOfflineAccess({ prompt: "select_account" }).then(signInCallback);
    };
    $("#login-btn").on("click", onSignIn);
    var signInCallback = function(authResult) {
        if (authResult["code"]) {
            // Send the code to the server
            oAuthReq = $.ajax({
                type: "POST",
                url: "/gconnect?state="+tolearnState,
                // Always include an `X-Requested-With` header in every AJAX request,
                // to protect against CSRF attacks.
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                contentType: "application/octet-stream; charset=utf-8",
                processData: false,
                data: authResult["code"]
            });
            oAuthReq.then(function(result) {
                // redirect on client side
                // do not let user interact with UI
                $("#modalWait").toggleClass("modal-hide");
                if (result) {
                    $("#text").html("Signing in...");
                    setTimeout(function() {
                        window.location.replace("/cat/");
                    }, 3000);
                }
            }, function() {
                alert("Login failed");
            })
        } else {
            alert("Authorization failed");
        }
    };
});