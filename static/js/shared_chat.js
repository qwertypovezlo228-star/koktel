
let lastMessageCount = 0;

async function loadSharedMessages() {
  const res = await fetch("/get_shared_messages");
  if (!res.ok) return;

  const data = await res.json();
  const chatBox = document.getElementById("chat-box");

  if (data.length === lastMessageCount) return;

  const atBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 100;

  chatBox.innerHTML = "";

  data.forEach(msg => {
    chatBox.innerHTML += renderMessage(msg, false);
  });

  lastMessageCount = data.length;

  if (atBottom) {
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = document.getElementById("message").value.trim();
  let media_urls = [];

  if (!message && selectedFiles.length === 0) return;

  if (selectedFiles.length > 0) {
    media_urls = await uploadMedia();
  }

  await fetch("/send_shared_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      media_urls: media_urls,
      reply_to: replyTo
    }),
  });

  resetForm();
  loadSharedMessages();
});

setInterval(loadSharedMessages, 500);
window.onload = loadSharedMessages;

