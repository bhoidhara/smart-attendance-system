let STUDENT = {};

function verify(){
    STUDENT.enroll = document.getElementById("enroll").value;
    STUDENT.name = document.getElementById("name").value;
    STUDENT.class = document.getElementById("class").value;

    navigator.geolocation.getCurrentPosition(pos=>{
        fetch("/verify", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({
                lat: pos.coords.latitude,
                lon: pos.coords.longitude
            })
        }).then(r=>r.json()).then(d=>{
            if(d.status=="inside"){
                document.getElementById("msg").innerHTML="Location verified ✅";
                document.getElementById("markBox").style.display="block";
            } else {
                document.getElementById("msg").innerHTML="Outside campus ❌";
            }
        });
    });
}

function mark(){
    fetch("/mark",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(STUDENT)
    }).then(r=>r.json()).then(d=>{
        alert("Attendance marked!");
    });
}







