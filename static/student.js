document.addEventListener("DOMContentLoaded", function(){
    const enrollment = document.getElementById("enrollment");
    const name = document.getElementById("name");
    const className = document.getElementById("class_name");
    const verifyBtn = document.getElementById("verifyBtn");
    const markBtn = document.getElementById("markBtn");
    const message = document.getElementById("message");

    markBtn.disabled = true;

    verifyBtn.onclick = function(){
        if(!enrollment.value || !name.value || !className.value){
            message.innerText = "Please fill all fields";
            return;
        }

        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition(
                function(position){
                    // optional location, ignore PPI
                    markBtn.disabled = false;
                    message.innerText="Location verified, you can now mark attendance";
                },
                function(err){
                    markBtn.disabled=false;
                    message.innerText="Location not available, still you can mark attendance";
                }
            );
        }else{
            markBtn.disabled=false;
            message.innerText="Location not supported, you can mark attendance";
        }
    }

    markBtn.onclick = function(){
        fetch("/mark_attendance",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                enrollment: enrollment.value,
                name: name.value,
                class_name: className.value
            })
        }).then(res=>res.json())
        .then(data=>{
            message.innerText=data.message;
            markBtn.disabled=true;
        }).catch(()=>{
            message.innerText="Error marking attendance";
        })
    }
});


