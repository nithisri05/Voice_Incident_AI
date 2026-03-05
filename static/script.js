let mediaRecorder;
let audioChunks = [];
let stream;
let isRecording = false;

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptBox = document.getElementById("transcriptBox");
const jsonBox = document.getElementById("jsonBox");

recordBtn.onclick = async () => {

    if (!isRecording) {

        try {

            stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {

                statusText.innerText = "Processing report...";
                recordBtn.disabled = true;

                const blob = new Blob(audioChunks, { type: "audio/webm" });

                const formData = new FormData();
                formData.append("audio", blob);

                try {

                    const response = await fetch("/upload_audio", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    transcriptBox.innerText = data.transcript || "";

                    if (data.needs_clarification) {

                        jsonBox.innerHTML = `
                            <b>Clarification Needed</b><br><br>
                            ${data.clarification_question}
                        `;

                        statusText.innerText = "Waiting for clarification";
                        recordBtn.disabled = false;
                        return;
                    }

                    const s = data.structured;
                  

                    let html = "";

                    for (const key in s) {

                      if (s[key] && s[key] !== "") {

                           const label = key
                             .replace("_"," ")
                             .replace("_"," ")
                             .toUpperCase();

                            html += `<b>${label}:</b> ${s[key]}<br><br>`;
                         }

                }

                 jsonBox.innerHTML = html;

                    jsonBox.innerHTML = `
                        <b>Equipment:</b> ${s.equipment}<br><br>
                        <b>Location:</b> ${s.location_or_unit}<br><br>
                        <b>Incident:</b> ${s.incident_summary}<br><br>
                        <b>Date:</b> ${s.incident_date}<br><br>
                        <b>Time:</b> ${s.incident_time}<br><br>
                        <b>Severity:</b> ${s.severity || "-"}
                    `;

                    if (data.tts_audio_url) {
                        const audio = new Audio(data.tts_audio_url);
                        audio.play();
                    }

                    statusText.innerText = "Report recorded successfully";
                    recordBtn.disabled = false;

                } catch (error) {

                    console.error(error);
                    statusText.innerText = "Processing failed";
                    recordBtn.disabled = false;
                }
            };

            mediaRecorder.start();

            recordBtn.innerText = "Stop Recording";
            statusText.innerText = "Recording... Speak clearly";
            isRecording = true;

        } catch (error) {

            console.error(error);
            statusText.innerText = "Microphone access denied";
        }

    } else {

        mediaRecorder.stop();

        stream.getTracks().forEach(track => track.stop());

        recordBtn.innerText = "Start Recording";
        isRecording = false;
    }
};