
async function loadDialogs() {
  const res = await fetch("/get_dialogs");
  const dialogs = await res.json();
  const container = document.getElementById("dialogs");
  container.innerHTML = "";

  dialogs.sort((a, b) => {
    if ((a.unread > 0) && (b.unread === 0)) return -1;
    if ((a.unread === 0) && (b.unread > 0)) return 1;

    const timeA = new Date(a.last_time.replace(" ", "T")).getTime() || 0;
    const timeB = new Date(b.last_time.replace(" ", "T")).getTime() || 0;
    return timeB - timeA;
  });

  if (dialogs.length === 0) {
	const emptyMessage = document.createElement("div");
	emptyMessage.textContent = window.TRANSLATIONS.no_dialogs;
	emptyMessage.className = "not-found-message text-shadow";
	container.appendChild(emptyMessage);
	return;
  }

  dialogs.forEach(d => {
    const link = document.createElement("a");
    link.href = `/chat_with/${d.username}`;
    link.className = "btn btn-lg w-100 text-start mb-3 d-flex align-items-center position-relative dialog-link";
    link.style.backgroundColor = "#111";
    link.style.color = "#fff";
    link.style.border = "2px solid #9a00ff";
    link.style.borderRadius = "12px";
    link.style.fontWeight = "bold";

    const avatar = document.createElement("img");
	avatar.src = (Array.isArray(d.avatar) && d.avatar[0]) ? d.avatar[0] : "/static/images/Sample_User_Icon.png";
    avatar.alt = "avatar";
    avatar.className = "dialog-avatar";
    avatar.style.border = "2px solid #9a00ff";

    if (d.unread > 0) {
      link.classList.add("unread-dialog");
      avatar.style.border = "2px solid #ffcc00";
      avatar.style.boxShadow = "0 0 10px #ffcc00aa";
    }

    const usernameText = document.createElement("span");
    usernameText.textContent = d.username;
    usernameText.style.fontSize = "1.1rem";
    usernameText.style.fontWeight = "600";
    usernameText.style.marginLeft = "5px";

    const textWrapper = document.createElement("div");
    textWrapper.appendChild(usernameText);

    link.appendChild(avatar);
    link.appendChild(textWrapper);

    if (d.unread > 0) {
      const badge = document.createElement("span");
      badge.className = "badge-unread";
      badge.textContent = d.unread > 99 ? "99+" : d.unread;
      link.appendChild(badge);
    }

    container.appendChild(link);
  });
}

window.addEventListener("DOMContentLoaded", loadDialogs);
