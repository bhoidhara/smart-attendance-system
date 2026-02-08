document.addEventListener("DOMContentLoaded", () => {
    const verifyBtn = document.getElementById("verifyBtn");
    const markBtn = document.getElementById("markBtn");
    const msg = document.getElementById("message");

    const enrollmentInput = document.getElementById("enrollment");
    const nameInput = document.getElementById("name");
    const classInput = document.getElementById("class_name");
    const apiBase = document.body && document.body.dataset ? document.body.dataset.apiBase : "";

    let location = null;
    let locationVerified = false;
    let isSubmitting = false;
    let lastTap = 0;
    const deviceId = getOrCreateDeviceId();

    function setMessage(text, isError = false) {
        if (!msg) {
            return;
        }
        msg.textContent = text;
        msg.style.color = isError ? "#b00020" : "#1b5e20";
    }

    const queryParams = new URLSearchParams(window.location.search);
    const classFromQuery = queryParams.get("class");
    if (classFromQuery && classInput) {
        classInput.value = classFromQuery;
    }

    setMessage("");

    function getOrCreateDeviceId() {
        const key = "attendance_device_id";
        try {
            const existing = localStorage.getItem(key);
            if (existing) {
                return existing;
            }
            const newId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
            localStorage.setItem(key, newId);
            return newId;
        } catch (err) {
            return `fallback-${Date.now().toString(36)}`;
        }
    }

    function attachTap(el, handler) {
        if (!el) {
            return;
        }
        el.addEventListener("click", handler);
        el.addEventListener(
            "touchstart",
            (e) => {
                const now = Date.now();
                if (now - lastTap < 500) {
                    return;
                }
                lastTap = now;
                e.preventDefault();
                handler(e);
            },
            { passive: false }
        );
    }

    attachTap(verifyBtn, verifyLocation);
    attachTap(markBtn, sendAttendance);

    function verifyLocation() {
        if (!navigator.geolocation) {
            setMessage("Geolocation not supported", true);
            return;
        }

        if (!window.isSecureContext) {
            setMessage("Geolocation requires HTTPS or localhost.", true);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                location = {
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                };
                locationVerified = true;

                setMessage("Location verified.");
                markBtn.disabled = false;
            },
            (err) => {
                const reason = err && err.message ? err.message : "Location permission denied.";
                setMessage(reason, true);
            }
        );
    }

    function sendAttendance(e) {
        if (e && e.preventDefault) {
            e.preventDefault();
        }

        if (isSubmitting) {
            return;
        }

        if (!locationVerified) {
            setMessage("Verify location before marking attendance.", true);
            return;
        }

        const enrollment = enrollmentInput.value.trim();
        const name = nameInput.value.trim();
        const className = classInput.value.trim();

        if (!enrollment || !name || !className) {
            setMessage("Please fill all fields before marking attendance.", true);
            return;
        }

        const payload = {
            enrollment,
            name,
            class: className,
            lat: location.lat,
            lon: location.lon,
            device_id: deviceId
        };

        isSubmitting = true;

        const normalizedBase = apiBase ? apiBase.replace(/\/+$/, "") : "";
        const markUrl = normalizedBase ? `${normalizedBase}/mark` : "/mark";

        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        };

        const parseResponse = (r) =>
            r
                .text()
                .then((text) => {
                    try {
                        return JSON.parse(text);
                    } catch (err) {
                        return { error: text || `Server error (${r.status}).` };
                    }
                })
                .then((data) => ({ data, status: r.status, ok: r.ok }));

        const handleResult = ({ data, status, ok }) => {
            if (!ok || (data && data.error)) {
                const message = data && data.error ? data.error : `Server error (${status}).`;
                setMessage(message, true);
                return;
            }
            setMessage("Attendance marked successfully.");
            markBtn.disabled = true;
        };

        const tryFetch = (url) =>
            fetch(url, requestOptions)
                .then(parseResponse)
                .then(handleResult);

        tryFetch(markUrl)
            .catch(() => {
                if (normalizedBase) {
                    return tryFetch("/mark");
                }
                setMessage("Server error.", true);
            })
            .finally(() => {
                isSubmitting = false;
            });
    }
});
