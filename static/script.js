let mediaRecorder;
let audioChunks = [];
let stream;
let isRecording = false;

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptBox = document.getElementById("transcriptBox");
const jsonBox = document.getElementById("jsonBox");

// Helper to set UI to "Thinking" mode
const setProcessing = (isProcessing) => {
    if (isProcessing) {
        transcriptBox.classList.add("processing");
        jsonBox.classList.add("processing");
        transcriptBox.innerText = "Analyzing audio stream...";
        jsonBox.innerText = "Extracting structured entities...";
    } else {
        transcriptBox.classList.remove("processing");
        jsonBox.classList.remove("processing");
    }
};

/**
 * Maps the backend severity strings (Low, Medium, High) 
 * to specific CSS colors and labels for the UI.
 */
function getSeverityStyles(severity) {
    const s = (severity || "Low").toLowerCase();
    
    // Default: Low
    let styles = {
        bgColor: "rgba(16, 185, 129, 0.1)", // Light Green
        textColor: "#10b981",              // Bold Green
        label: "Low"
    };

    if (s === "high" || s === "critical") {
        styles = {
            bgColor: "rgba(239, 68, 68, 0.1)", // Light Red
            textColor: "#ef4444",              // Bold Red
            label: "High"
        };
    } else if (s === "medium" || s === "warning") {
        styles = {
            bgColor: "rgba(245, 158, 11, 0.1)", // Light Orange
            textColor: "#f59e0b",               // Bold Orange
            label: "Medium"
        };
    }
    
    return styles;
}

recordBtn.onclick = async () => {
    if (!isRecording) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                // UI State: Processing
                statusText.innerText = "⏳ AI is structuring your report...";
                statusText.style.color = "#2563eb"; 
                recordBtn.disabled = true;
                setProcessing(true);

                const blob = new Blob(audioChunks, { type: "audio/webm" });
                stream.getTracks().forEach(track => track.stop());

                const formData = new FormData();
                formData.append("audio", blob);

                try {
                    const response = await fetch("/upload_audio", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    // Stop Shimmer
                    setProcessing(false);

                    // Show transcript
                    transcriptBox.innerText = data.transcript || "No transcript generated.";

                    if (data.needs_clarification) {
                        jsonBox.innerHTML = `
                            <div style="color:#eab308; font-weight:bold; border-left: 4px solid #eab308; padding-left: 10px;">
                                ⚠️ Clarification Required
                            </div>
                            <p style="margin-top:10px;">${data.clarification_question}</p>
                        `;
                        statusText.innerText = "Status: Waiting for more info";
                        statusText.style.color = "#eab308";
                    } else {
                        const s = data.structured || {};
                        const styles = getSeverityStyles(s.severity);

                        // Beautifully formatted output with Dynamic Severity Colors
                        jsonBox.innerHTML = `
                            <div class="report-item"><strong>Reporter:</strong> ${s.reporter_name || "Unknown"}</div>
                            <div class="report-item"><strong>Department:</strong> ${s.department || "N/A"}</div>
                            <div class="report-item"><strong>Equipment:</strong> ${s.equipment || "N/A"}</div>
                            <div class="report-item"><strong>Location:</strong> ${s.location_or_unit || "N/A"}</div>
                            <div class="report-item"><strong>Incident:</strong> ${s.incident_summary || "N/A"}</div>
                            
                            <div class="report-item" style="margin-top:15px; padding: 12px; border-radius: 12px; background: ${styles.bgColor}; border: 1px solid ${styles.textColor}">
                                <strong style="color: ${styles.textColor}">Severity:</strong>
                                <span style="
                                    display:inline-block;
                                    padding:2px 12px;
                                    border-radius:999px;
                                    font-size:12px;
                                    font-weight:700;
                                    color:white;
                                    background:${styles.textColor};
                                    margin-left:8px;
                                    text-transform: uppercase;
                                ">
                                    ${styles.label}
                                </span>
                            </div>
                        `;

                        statusText.innerText = "✅ Report Generated Successfully";
                        statusText.style.color = "#10b981";
                    }

                    if (data.tts_audio_url) {
                        const audio = new Audio(data.tts_audio_url);
                        audio.play();
                    }

                    recordBtn.disabled = false;

                } catch (error) {
                    console.error(error);
                    setProcessing(false);
                    statusText.innerText = "❌ Error: Connection Failed";
                    statusText.style.color = "#ef4444";
                    recordBtn.disabled = false;
                }
            };

            mediaRecorder.start(250);
            recordBtn.innerHTML = "<span>⏹ Stop Recording</span>";
            recordBtn.classList.add("recording");
            statusText.innerText = "🔴 Listening... Speak clearly";
            statusText.style.color = "#ef4444";
            isRecording = true;

        } catch (error) {
            console.error(error);
            statusText.innerText = "Microphone access denied";
        }

    } else {
        mediaRecorder.stop();
        recordBtn.innerHTML = "<span>🎤 Start Recording</span>";
        recordBtn.classList.remove("recording");
        isRecording = false;
    }
};