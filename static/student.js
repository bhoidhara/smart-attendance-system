import { initializeApp } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-app.js";
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyBSa6AKAJy0oZLumq-ZLnOkSnz-4UgndAA",
  authDomain: "attendance-project-39c42.firebaseapp.com",
  projectId: "attendance-project-39c42",
  appId: "1:119365803885:web:eaab4dafe3bc5277bb4464"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

window.recaptchaVerifier = new RecaptchaVerifier('msg', {size:'invisible'}, auth);

let confirmation;

window.sendOTP = function(){
  const phone = document.getElementById("phone").value;
  signInWithPhoneNumber(auth, "+91"+phone, window.recaptchaVerifier)
    .then(r => {
      confirmation = r;
      document.getElementById("otpDiv").style.display="block";
      alert("OTP sent");
    });
}

window.verifyOTP = function(){
  const otp = document.getElementById("otp").value;
  confirmation.confirm(otp).then(()=>{
    navigator.geolocation.getCurrentPosition(pos=>{
      fetch("/mark",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          phone:document.getElementById("phone").value,
          lat:pos.coords.latitude,
          lon:pos.coords.longitude
        })
      }).then(r=>r.json()).then(d=>{
        alert(d.status=="ok"?"Attendance Marked":"Outside Class");
      });
    });
  });
}






