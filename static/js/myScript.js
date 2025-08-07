window.addEventListener("load", function () {
    const loader =document.querySelector(".full-screen");
    if (loader) loader.style.display = "none";
  });

const forms = document.getElementsByTagName("form");

for (let form of forms) {
  form.addEventListener("submit", () => {
    const loader = document.querySelector(".full-screen");
    if (loader) loader.style.display = "flex";
  });
}

//Notification logic
setTimeout(() => {
  const notif = document.querySelector('.container .notification');
  if (notif) {
    notif.style.right = '-500px';
    notif.style.transition = 'right 0.5s ease';
    setTimeout(() => {
      notif.style.display = 'none';
    }, 500);
  }
}, 5000);

//Notification logic for login
setTimeout(() => {
  const notif = document.querySelector('.notification');
  if (notif) {
    notif.style.right = '-500px';
    notif.style.transition = 'right 0.5s ease';
    setTimeout(() => {
      notif.style.display = 'none';
    }, 500);
  }
}, 5000);


// Profile popup dialog box

const profile_btn = document.getElementById("edit_profile");
const box = document.querySelector(".profile_picture_update_bg");
const exit_btn = document.querySelector(".x");

if (profile_btn && box) {
  profile_btn.addEventListener("click", () => {
    box.classList.remove("hide");
    box.style.animation = "popup 0.3s ease-in-out";
  });
}

if (exit_btn && box) {
  exit_btn.addEventListener("click", () => {
    box.classList.add("hide");
    box.style.animation = "none";
  });
}

// Mark as completed popup logic
function showCompletedPopup() {
    document.getElementById('popupOverlay').classList.add('show');
    document.getElementById('popupCompletedBox').classList.add('show');
}

function showCancelPopup() {
    document.getElementById('popupOverlay').classList.add('show');
    document.getElementById('popupCancelBox').classList.add('show');
}

function showDeletePopup() {
    document.getElementById('popupOverlay').classList.add('show');
    document.getElementById('popupDeleteBox').classList.add('show');
}


function hidePopup() {
    document.getElementById('popupCompletedBox').classList.remove('show');
    document.getElementById('popupCancelBox').classList.remove('show');
    document.getElementById('popupDeleteBox').classList.remove('show');
    document.getElementById('popupOverlay').classList.remove('show');
}

