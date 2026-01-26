let DATA = {};

function verify(){
DATA.enroll=document.getElementById("enroll").value;
DATA.name=document.getElementById("name").value;
DATA.class=document.getElementById("class").value;

if(!navigator.geolocation){
 alert("Location not supported");
 return;
}

navigator.geolocation.getCurrentPosition(function(pos){

fetch("/verify",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
lat:pos.coords.latitude,
lon:pos.coords.longitude
})
})
.then(r=>r.json())
.then(d=>{
if(d.status=="inside"){
document.getElementById("msg").innerHTML="Location OK ✅";
document.getElementById("markBox").style.display="block";
}else{
document.getElementById("msg").innerHTML="Outside Campus ❌";
}
});
},
function(){
alert("Location permission denied");
});
}

function mark(){
fetch("/mark",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify(DATA)
})
.then(r=>r.json())
.then(d=>{
alert("Attendance marked!");
});
}








