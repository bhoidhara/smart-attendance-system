document.addEventListener('DOMContentLoaded', function(){

    const verifyBtn = document.getElementById('verifyBtn');
    const markBtn = document.getElementById('markBtn');
    const message = document.getElementById('message');

    // Read QR link parameters automatically
    const urlParams = new URLSearchParams(window.location.search);
    document.getElementById('enrollment').value = urlParams.get('enrollment') || '';
    document.getElementById('name').value = urlParams.get('name') || '';
    document.getElementById('class_name').value = urlParams.get('class_name') || '';

    verifyBtn.addEventListener('click', function(){
        const enrollment = document.getElementById('enrollment').value.trim();
        const name = document.getElementById('name').value.trim();
        const class_name = document.getElementById('class_name').value.trim();

        if(!enrollment || !name || !class_name){
            message.innerText = "Please fill all fields!";
            return;
        }

        if(!navigator.geolocation){
            message.innerText = "Geolocation not supported by your browser!";
            return;
        }

        navigator.geolocation.getCurrentPosition(function(position){
            const data = {
                enrollment: enrollment,
                name: name,
                class_name: class_name,
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };

            fetch('/verify_location',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify(data)
            })
            .then(res=>res.json())
            .then(res=>{
                message.innerText = res.message;
                if(res.status==='success'){
                    markBtn.disabled = false;
                }
            })
            .catch(err=>{
                console.error(err);
                message.innerText = "Error verifying location!";
            });

        }, function(error){
            message.innerText = "Unable to get your location!";
        });
    });

    markBtn.addEventListener('click', function(){
        const enrollment = document.getElementById('enrollment').value.trim();
        fetch('/mark_attendance',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({enrollment: enrollment})
        })
        .then(res=>res.json())
        .then(res=>{
            message.innerText = res.message;
            markBtn.disabled = true;
        })
        .catch(err=>{
            console.error(err);
            message.innerText = "Error marking attendance!";
        });
    });
});


