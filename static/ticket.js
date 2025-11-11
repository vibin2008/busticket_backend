window.onload = function(){
    const params = new URLSearchParams(window.location.search)
    const status = params.get("txStatus")
    var tic = document.getElementById("front")
    var unsuccess = document.getElementById("unsuccessful")
    if (status == "SUCCESS"){
        tic.style.display = "inline-block"
        unsuccess.style.display = "none"
    }
    else{
        tic.style.display = "none"
        unsuccess.style.display = "inline-block"
    }
}

function open_wa(){
                var url = window.location.href
                const message = encodeURIComponent("Here is your ticket: " + url)
                window.location.href = "https://wa.me/?text=Here is your ticket"+message                
            }
