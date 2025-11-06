
async function loadSupportMessages() {
  const res = await fetch("/admin/api/get_support_messages");
  const messages = await res.json();
  const container = document.getElementById("messages");
  container.innerHTML = "";

  messages.sort((a, b) => {
    if ((a.unread > 0) && (b.unread === 0)) return -1;
    if ((a.unread === 0) && (b.unread > 0)) return 1;

    const timeA = new Date(a.last_time.replace(" ", "T")).getTime() || 0;
    const timeB = new Date(b.last_time.replace(" ", "T")).getTime() || 0;
    return timeB - timeA;
  });

  if (messages.length === 0) {
    const emptyMessage = document.createElement("div");
    emptyMessage.textContent = window.TRANSLATIONS.no_messages_found;
    emptyMessage.className = "not-found-message text-shadow";
    container.appendChild(emptyMessage);
    return;
  }

  messages.forEach(m => {
    const link = document.createElement("a");
    link.href = `/admin/support_message/${encodeURIComponent(m.id)}`;
    link.className = "btn btn-lg w-100 text-start mb-3 d-flex align-items-center position-relative dialog-link";
    if (m.unread > 0) {
      link.classList.add("unread-dialog");
    }
    link.style.backgroundColor = "#111";
    link.style.color = "#fff";
    link.style.border = "2px solid #9a00ff";
    link.style.borderRadius = "12px";
    link.style.fontWeight = "bold";
    link.style.padding = "10px";

    const leftWrapper = document.createElement("div");
    leftWrapper.style.display = "flex";
    leftWrapper.style.flexDirection = "column";
    leftWrapper.style.overflow = "hidden";
    leftWrapper.style.flex = "1";
    leftWrapper.style.minWidth = "0";

    const nameText = document.createElement("div");
    nameText.textContent = m.contact;
    nameText.style.fontSize = "1.1rem";
    nameText.style.fontWeight = "600";
    nameText.style.whiteSpace = "nowrap";
    nameText.style.overflow = "hidden";
    nameText.style.textOverflow = "ellipsis";

    const msgPreview = document.createElement("div");
    msgPreview.textContent = m.last_message || "";
    msgPreview.style.fontSize = "0.9rem";
    msgPreview.style.opacity = "0.7";
    msgPreview.style.whiteSpace = "nowrap";
    msgPreview.style.overflow = "hidden";
    msgPreview.style.textOverflow = "ellipsis";

    leftWrapper.appendChild(nameText);
    leftWrapper.appendChild(msgPreview);

    const rightWrapper = document.createElement("div");
    rightWrapper.style.display = "flex";
    rightWrapper.style.flexDirection = "column";
    rightWrapper.style.alignItems = "flex-end";
    rightWrapper.style.marginLeft = "10px";

    const dateDiv = document.createElement("div");
    if (m.last_time) {
      const dateObj = new Date(m.last_time.replace(" ", "T"));
      const now = new Date();
      let formatted = "";

      if (dateObj.toDateString() === now.toDateString()) {
        formatted = dateObj.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      } else {
        formatted = dateObj.toLocaleDateString();
      }

      dateDiv.textContent = formatted;
      dateDiv.style.fontSize = "0.8rem";
      dateDiv.style.opacity = "0.6";
    }

    rightWrapper.appendChild(dateDiv);

    if (m.unread > 0) {
      const badge = document.createElement("span");
      badge.className = "badge-unread";
      badge.textContent = "!";
      badge.style.marginTop = "5px";
      rightWrapper.appendChild(badge);
    }

    link.appendChild(leftWrapper);
    link.appendChild(rightWrapper);

    container.appendChild(link);
  });
}

window.addEventListener("DOMContentLoaded", loadSupportMessages);

