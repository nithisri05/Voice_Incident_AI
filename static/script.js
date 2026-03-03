let mediaRecorder;
let audioChunks = [];
let stream;
let isRecording = false;

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptBox = document.getElementById("transcriptBox");
const jsonBox = document.getElementById("jsonBox");

let confirmButton = null;

recordBtn.onclick = async () => {

    if (!isRecording) {

        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {

            const blob = new Blob(audioChunks, { type: "audio/webm" });
            stream.getTracks().forEach(track => track.stop());

            const formData = new FormData();
            formData.append("audio", blob);

            statusText.innerText = "Processing...";

            const response = await fetch("/upload_audio", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            transcriptBox.innerText = data.transcript || "";

            if (data.needs_clarification) {
                jsonBox.innerText =
                    "⚠ Clarification Needed:\n\n" +
                    data.clarification_question +
                    "\n\nPlease record again.";
                statusText.innerText = "Waiting for clarification...";
                return;
            }

            // Show structured JSON
            jsonBox.innerText =
                "📋 Extracted Report:\n\n" +
                JSON.stringify(data.structured, null, 2);

            // Play TTS if available
            if (data.tts_audio_url) {
                const audio = new Audio(data.tts_audio_url);
                audio.play();
            }

            // If awaiting confirmation
            if (data.awaiting_confirmation) {

                if (confirmButton) confirmButton.remove();

                confirmButton = document.createElement("button");
                confirmButton.innerText = "Confirm & Save Report";
                confirmButton.style.marginTop = "20px";
                confirmButton.style.padding = "10px 20px";
                confirmButton.style.fontSize = "16px";

                confirmButton.onclick = async () => {

                    const confirmResponse = await fetch("/confirm_report", {
                        method: "POST"
                    });

                    const confirmData = await confirmResponse.json();

                    jsonBox.innerText +=
                        "\n\n✅ " + confirmData.status;

                    confirmButton.remove();
                };

                jsonBox.appendChild(confirmButton);
            }

            statusText.innerText = "Done";
        };

        mediaRecorder.start(250);
        recordBtn.innerText = "Stop Recording";
        statusText.innerText = "Recording...";
        isRecording = true;

    } else {

        mediaRecorder.stop();
        recordBtn.innerText = "Start Recording";
        isRecording = false;
    }
};