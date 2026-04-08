let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptBox = document.getElementById("transcriptBox");
const jsonBox = document.getElementById("jsonBox");

recordBtn.onclick = async () => {

    if (!isRecording) {

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {

            statusText.innerText = "Processing...";

            const blob = new Blob(audioChunks, { type: "audio/webm" });
            const formData = new FormData();
            formData.append("audio", blob);

            const res = await fetch("/upload_audio", {
                method: "POST",
                body: formData
            });

            const data = await res.json();

            transcriptBox.innerText = data.transcript;

            if (data.needs_clarification) {
                jsonBox.innerHTML = `
                    <b>⚠️ Clarification</b><br>
                    ${data.clarification_question}
                `;
                statusText.innerText = "Waiting for input...";
            } else {
                const s = data.structured;

                jsonBox.innerHTML = `
                    <b>Reporter:</b> ${s.reporter_name}<br>
                     <b>Department:</b> ${s.department || "-"}<br>
                    <b>Equipment:</b> ${s.equipment}<br>
                    <b>Location:</b> ${s.location_or_unit}<br>
                    <b>Incident:</b> ${s.incident_summary}<br>
                    <b>Severity:</b> ${s.severity}<br>
                    <b>Confidence:</b> ${s.confidence}%<br>
                    <b>Action:</b> ${s.suggested_action}
                `;

                statusText.innerText = "✅ Done";
            }
        };

        mediaRecorder.start(250);
        recordBtn.innerText = "Stop Recording";
        statusText.innerText = "Listening...";
        isRecording = true;

    } else {
        mediaRecorder.stop();
        recordBtn.innerText = "Start Recording";
        isRecording = false;
    }
};