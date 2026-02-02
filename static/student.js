document.addEventListener('DOMContentLoaded', function () {

    const verifyBtn = document.getElementById('verifyBtn');
    const markBtn = document.getElementById('markBtn');
    const message = document.getElementById('message');

    markBtn.disabled = true;

    verifyBtn.addEventListener('click', function () {

        const enrollment = document.getElementById('enrollment').value.trim();
        const name = document.getElementById('name').value.trim();
        const class_name = document.getElementById('class_name').value.trim();

        if (!enrollment || !name || !class_name) {
            message.innerText = "Please fill all fields";
            return;
        }

        if (!navigator.geolocation) {
            message.innerText = "Location not supported";
            return;
        }

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
                    if (data.status === "success") {
                        markBtn.disabled = false;
                    }
                })
                .catch(() => {
                    message.innerText = "Location verification failed";
                });

            },
            function () {
                message.innerText = "Unable to fetch location";
            }
        );
    });

    markBtn.addEventListener('click', function () {

        const enrollment = document.getElementById('enrollment').value;
        const name = document.getElementById('name').value;
        const class_name = document.getElementById('class_name').value;

        fetch('/mark_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enrollment, name, class_name })
        })
        .then(res => res.json())
        .then(data => {
            message.innerText = data.message;
            markBtn.disabled = true;
        })
        .catch(() => {
            message.innerText = "Error marking attendance";
        });
    });

});

