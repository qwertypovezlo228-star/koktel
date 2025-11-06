
let selectedFiles = [];
let replyTo = "";

function showImageModal(url) {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const downloadLink = document.getElementById("download-link");

  if (modal && modalImg && downloadLink) {
    modal.style.display = "flex";
    modalImg.src = url;
    downloadLink.href = url;
  }
}

function closeModal() {
  const modal = document.getElementById("image-modal");
  if (modal) {
    modal.style.display = "none";
    const modalImg = document.getElementById("modal-img");
    if (modalImg) {
      modalImg.src = "";
    }
  }
}

function setReply(text) {
  replyTo = text;
  const replyDiv = document.getElementById("reply-to");
  if (replyDiv) {
    replyDiv.innerHTML = `
      <span class="reply-author">${window.TRANSLATIONS.reply_to_prefix}</span>
      <span class="reply-text">${text}</span>
      <span class="cancel-reply" onclick="cancelReply()">×</span>
    `;
    replyDiv.style.display = "flex";
  }
}

function cancelReply() {
  replyTo = "";
  const replyDiv = document.getElementById("reply-to");
  if (replyDiv) {
    replyDiv.style.display = "none";
    replyDiv.innerHTML = "";
  }
}

function resetForm() {
  const messageInput = document.getElementById("message");
  const mediaInput = document.getElementById("media");
  const replyDiv = document.getElementById("reply-to");
  const previewContainer = document.getElementById("media-preview-container");

  if (messageInput) messageInput.value = "";
  if (mediaInput) mediaInput.value = null;
  if (replyDiv) {
    replyDiv.style.display = "none";
    replyDiv.innerHTML = "";
  }
  if (previewContainer) previewContainer.innerHTML = "";

  selectedFiles = [];
  replyTo = "";
}

function handleMediaSelection(files) {
  const previewContainer = document.getElementById("media-preview-container");
  if (!previewContainer) return;

  for (let file of files) {
    selectedFiles.push(file);
    const url = URL.createObjectURL(file);

    const thumb = document.createElement("div");
    thumb.classList.add("media-thumb");

    const img = document.createElement("img");
    img.src = url;

    const removeBtn = document.createElement("button");
    removeBtn.innerHTML = "×";
    removeBtn.className = "remove-btn";
    removeBtn.onclick = () => {
      previewContainer.removeChild(thumb);
      selectedFiles = selectedFiles.filter(f => f !== file);
    };

    thumb.appendChild(img);
    thumb.appendChild(removeBtn);
    previewContainer.appendChild(thumb);
  }

  document.getElementById("media").value = "";
}

async function uploadMedia(files = selectedFiles) {
  if (!files || files.length === 0) return [];

  const formData = new FormData();
  for (let file of files) {
    formData.append("files[]", file);
  }

  const res = await fetch("/upload_media_chat", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  document.getElementById("media-preview-container").innerHTML = "";
  selectedFiles = [];

  return data.urls || [];
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: userTimeZone
  });
}

function renderMessage(msg, isPrivate = false) {
  let html = `<div class="message-row" data-username="${msg.username}">`;

  if (msg.show_avatar) {
    html += `<div class="avatar"><a href="/profile/${msg.username}"><img src="${msg.avatar_url}" alt="${msg.username}"></a></div>`;
  } else {
    html += `<div class="avatar" style="visibility:hidden;"><img src="${msg.avatar_url}" alt="${msg.username}"></div>`;
  }

  html += `<div class="message-bubble">`;
  html += `<div class="message-text-wrapper">`
  if (msg.show_username) {
    html += `<div class="message-username"><a class="text-primary fw-semibold" style="text-decoration: none;" href="/profile/${msg.username}">${msg.username}</a></div>`;
  }

  if (msg.media_urls && msg.media_urls.length > 0) {
    msg.media_urls.forEach(url => {
      html += `<img class="message-image" src="${url}" onclick="showImageModal('${url}')">`;
    });
  }

  if (msg.reply || msg.reply_to) {
    html += `<div class="reply-box"><span class="icon">󱞩</span> ${msg.reply || msg.reply_to}</div>`;
  }

  html += `<div class="message-text">${msg.message}</div></div>`;

  const timeStr = formatTimestamp(msg.timestamp);

  html += ` 
    <div class="message-meta-wrapper">
		<div class="message-meta">
		  <span class="timestamp">${timeStr}</span>
		  <span class="reply-btn" onclick="setReply('${msg.message}')">
			<span class="icon">󱞥</span>
		  </span>
		</div>
    </div>`;

  html += `</div></div>`;
  return html;
}

document.addEventListener("DOMContentLoaded", () => {
  const mediaInput = document.getElementById('media');
  if (mediaInput) {
    mediaInput.addEventListener('change', function () {
      handleMediaSelection(this.files);
    });
  }

  const modal = document.getElementById("image-modal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
  }

  const closeBtn = document.querySelector(".close-btn");
  if (closeBtn) {
    closeBtn.addEventListener("click", closeModal);
  }
});

