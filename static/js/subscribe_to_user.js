
function setDisplay(className, display) {
  document.querySelectorAll(`.${className}`).forEach(btn => {
    btn.style.display = display;
  });
}

function subscribeToUser(user_id, visibleDisplay = "flex") {
  setDisplay(`subscribe-${user_id}`, "none");
  setDisplay(`unsubscribe-${user_id}`, visibleDisplay);
  fetch(`/api/subscribe/${user_id}`);
}

function unsubscribeFromUser(user_id, visibleDisplay = "flex") {
  setDisplay(`unsubscribe-${user_id}`, "none");
  setDisplay(`subscribe-${user_id}`, visibleDisplay);
  fetch(`/api/unsubscribe/${user_id}`);
}

