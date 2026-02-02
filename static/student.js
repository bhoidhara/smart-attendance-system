document.addEventListener("DOMContentLoaded", function () {
    console.log("STUDENT JS LOADED");

    const enrollment = document.getElementById("enrollment");
    const name = document.getElementById("name");
    const className = document.getElementById("class_name");
    const verifyBtn = document.getElementById("verifyBtn");
    const markBtn = document.getElementById("markBtn");
    const message = document.getElementById("message");

    markBtn.disabled = true;

    verifyBtn.onclick = function () {
        if (!enrollment.value || !name.value || !className.value) {
            message.innerText = "Please fill all fields";
            return;
        }

        if (!navigator.geolocation) {
            message.innerText = "Location not supported";
            return;
        }

        message.innerText = "Verifying location...";

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                fetch("/verify_location", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        enrollment: enrollment.value,
                        name: name.value,
                        class_name: className.value,
                        latitude: pos.coords.latitude,
                        longitude: pos.coords.longitude
                    })
                })
                .then(res => res.json())
                .then(data => {
                    message.innerText = data.message;
                    if (data.status === "success") {
                        markBtn.disabled = false;
                    }
                })
                .catch(() => {
                    message.innerText = "Server error";
                });
            },
            () => {
                message.innerText = "Location permission denied";
            }
        );
    };

    markBtn.onclick = function () {
        fetch("/mark_attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                enrollment: enrollment.value
            })
        })
        .then(res => res.json())
        .then(data => {
            message.innerText = data.message;
            markBtn.disabled = true;
        })
        .catch(() => {
            message.innerText = "Attendance failed";
        });
    };
});
