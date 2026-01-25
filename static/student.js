import { initializeApp } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-app.js";
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-auth.js";

// 🔥 Firebase config (paste your config)
const firebaseConfig = {
  apiKey: "AIzaSyBSa6AKAJy0oZLumq-ZLnOkSnz-4UgndAA",
  authDomain: "attendance-project-39c42.firebaseapp.com",
  projectId: "attendance-project-39c42",
  appId: "1:119365803885:web:eaab4dafe3bc5277bb4464"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

window.recaptchaVerifier = new RecaptchaVerifier('recaptcha', {
    size: 'invisible'
}, auth);

let confirmationResult;

window.sendOTP = function(){
    const phone = document.getElementById("phone").value;
    if(!phone){ alert("Enter your mobile number!"); return; }

    signInWithPhoneNumber(auth, phone, window.recaptchaVerifier)
        .then(confirmation => {
            confirmationResult = confirmation;
            document.getElementById("otpDiv").style.display = "block";
            document.getElementById("msg").innerText = "OTP sent!";
        })
        .catch(error => { alert(error.message); });
}

window.verifyOTP = function(){
    const otp = document.getElementById("otp").value;
    if(!otp){ alert("Enter OTP!"); return; }

    confirmationResult.confirm(otp)
        .then(result => {
            navigator.geolocation.getCurrentPosition(pos => {
                fetch("/mark", {
                    method: "POST",
                    headers: {"Content-Type":"application/json"},
                    body: JSON.stringify({
                        phone: document.getElementById("phone").value,
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude
                    })
                }).then(r => r.json())
                  .then(data => alert(data.status=="ok"?"✅ Attendance Marked":"❌ Outside Class"));
            });
        })
        .catch(() => { alert("Wrong OTP"); });
}







