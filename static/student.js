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

        message.innerText = "Location will be verified (optional)...";

        // Optional: still get location if available
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    console.log("Lat:", pos.coords.latitude, "Lng:", pos.coords.longitude);
                },
                () => { console.log("Location not provided"); }
            );
        }

        // Always enable mark button
        markBtn.disabled = false;
        message.innerText = "You can now mark attendance";
    };

    markBtn.onclick = function () {
        fetch("/mark_attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                enrollment: enrollment.value,
                name: name.value,
                class_name: className.value
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

