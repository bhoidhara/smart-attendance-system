document.addEventListener('DOMContentLoaded', function () {
    console.log("student.js loaded");

    const verifyBtn = document.getElementById('verifyBtn');
    const markBtn = document.getElementById('markBtn');
    const message = document.getElementById('message');

    // safety check
    if (!verifyBtn || !markBtn) {
        console.error("Button IDs not found");
        return;
    }

    markBtn.disabled = true;

    // QR params auto fill
    const urlParams = new URLSearchParams(window.location.search);
    const enrollmentField = document.getElementById('enrollment');
    const nameField = document.getElementById('name');
    const classField = document.getElementById('class_name');

    if (enrollmentField) enrollmentField.value = urlParams.get('enrollment') || '';
    if (nameField) nameField.value = urlParams.get('name') || '';
    if (classField) classField.value = urlParams.get('class_name') || '';

    // VERIFY LOCATION
    verifyBtn.addEventListener('click', function () {
        const enrollment = enrollmentField.value.trim();
        const name = nameField.value.trim();
        const class_name = classField.value.trim();

        if (!enrollment || !name || !class_name) {
            message.innerText = "Please fill all fields";
            return;
        }

        if (!navigator.geolocation) {
            message.innerText = "Geolocation not supported";
            return;
        }

        message.innerText = "Checking location...";

        navigator.geolocation.getCurrentPosition(
            function (position) {
                fetch('/verify_location', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        enrollment,
                        name,
                        class_name,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    })
                })
                    .then(res => res.json())
                    .then(data => {
                        message.innerText = data.message;
                        if (data.status === 'success') {
                            markBtn.disabled = false;
                        }
                    })
                    .catch(() => {
                        message.innerText = "Server error";
                    });
            },
            function () {
                message.innerText = "Location permission denied";
            }
        );
    });

    // MARK ATTENDANCE
    markBtn.addEventListener('click', function () {
        const enrollment = enrollmentField.value.trim();

        fetch('/mark_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enrollment })
        })
            .then(res => res.json())
            .then(data => {
                message.innerText = data.message;
                markBtn.disabled = true;
            })
            .catch(() => {
                message.innerText = "Attendance error";
            });
    });
});
