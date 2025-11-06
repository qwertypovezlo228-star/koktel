
let lastMessageId = 0;

async function loadMessages() {
  const res = await fetch(`/get_messages?username=${encodeURIComponent(receiver)}`);
  const data = await res.json();
  const chatBox = document.getElementById("chat-box");

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.clientHeight <= chatBox.scrollTop + 5;
  const newMessages = data.filter(msg => msg.id > lastMessageId);

  newMessages.forEach(msg => {
    chatBox.innerHTML += renderMessage(msg, true);
    lastMessageId = msg.id;
  });

  const messageRows = [...chatBox.querySelectorAll(".message-row")];
  for (let i = 0; i < messageRows.length; i++) {
    const current = messageRows[i];
    const next = messageRows[i + 1];
    const currentUser = current.dataset.username;
    const avatarDiv = current.querySelector(".avatar");

    if (!avatarDiv) continue;
    avatarDiv.style.visibility = (!next || next.dataset.username !== currentUser) ? "visible" : "hidden";
  }

  const unseenMessageIds = newMessages
    .filter(msg => msg.username !== currentUser && msg.is_read == 0)
    .map(msg => msg.id);

  if (unseenMessageIds.length > 0) {
    fetch("/mark_seen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_ids: unseenMessageIds })
    });
  }

  if (isScrolledToBottom && newMessages.length > 0) {
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

document.getElementById("chat-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const message = document.getElementById("message").value.trim();
  let media_urls = [];

  if (!message && selectedFiles.length === 0) return;

  if (selectedFiles.length > 0) {
    media_urls = await uploadMedia();
  }

  await fetch("/send_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      receiver: receiver,
      message: message,
      media_urls: media_urls,
      reply: replyTo
    }),
  });

  resetForm();
  loadMessages();
});

setInterval(loadMessages, 500);
window.onload = loadMessages;

