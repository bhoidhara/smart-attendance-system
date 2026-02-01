let locationVerified = false;

document.getElementById('verifyLocation').addEventListener('click', verifyLocation);
document.getElementById('markAttendance').addEventListener('click', markAttendance);

function verifyLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation not supported on this device/browser. Please use a mobile device or contact your teacher for manual attendance.");
        return;
    }

    // Request location with options for better accuracy
    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;

            // Parul University range (adjust RANGE if needed for laptops with Wi-Fi-based location)
            const PARUL_LAT = 22.2886;
            const PARUL_LON = 73.3622;
            const RANGE = 0.01; // 0.01 degrees ~ 1km; increase to 0.05 for laptops if inaccurate

            if (Math.abs(lat - PARUL_LAT) > RANGE || Math.abs(lon - PARUL_LON) > RANGE) {
                alert("Location not verified (outside Parul University). If using a laptop, location may be inaccurate—contact teacher.");
                return;
            }

            alert("Location verified! You can now mark attendance.");
            locationVerified = true;
            document.getElementById('markAttendance').disabled = false;
        },
        err => {
            // Handle errors specifically for laptops/mobiles
            let errorMsg = "Geolocation error: ";
            switch (err.code) {
                case err.PERMISSION_DENIED:
                    errorMsg += "Location access denied. Enable it in browser settings.";
                    break;
                case err.POSITION_UNAVAILABLE:
                    errorMsg += "Location unavailable (common on laptops without GPS). Contact teacher for override.";
                    break;
                case err.TIMEOUT:
                    errorMsg += "Location request timed out. Try again.";
                    break;
                default:
                    errorMsg += err.message;
            }
            alert(errorMsg);
        },
        {
            enableHighAccuracy: true, // Better accuracy on mobiles
            timeout: 10000, // 10 seconds timeout
            maximumAge: 300000 // Use cached location for 5 minutes
        }
    );
}

function markAttendance() {
    if (!locationVerified) {
        alert("Verify location first!");
        return;
    }

    const name = document.getElementById("name").value.trim();
    const enrollment = document.getElementById("enrollment").value.trim();
    const classValue = document.getElementById("class").value.trim();

    if (!name || !enrollment || !classValue) {
        alert("Please fill all fields.");
        return;
    }

    const data = { name, enrollment, class: classValue };

    fetch("/mark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(r => {
        if (!r.ok) throw new Error(`Server error: ${r.status}`);
        return r.json();
    })
    .then(d => alert(d.msg))
    .catch(err => alert("Error marking attendance: " + err.message));
}