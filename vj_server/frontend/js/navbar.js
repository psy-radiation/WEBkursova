function loadNavbar() {
  fetch("/static/navbar.html")
    .then(res => res.text())
    .then(html => {
      const container = document.getElementById("navbar-container");
      container.innerHTML = html;

      // Ждём пока DOM обновится и только потом вызываем updateAuthLinks
      setTimeout(updateAuthLinks, 0);
    });
}

function updateAuthLinks() {
  const token = localStorage.getItem("token");
  const container = document.getElementById("auth-links");

  if (!container) {
    console.log("⚠️ auth-links не найден");
    return;
  }
  if (token) {
    container.innerHTML = `
      <a href="/profile.html">👤 Профіль</a>
      <a href="/upload.html">⬆️ Завантажити</a>
      <a href="#" onclick="logout()">🚪 Вихід</a>
    `;
  } else {
    container.innerHTML = `
      <a href="/login.html">🔐 Вхід</a>
      <a href="/register.html">📝 Реєстрація</a>
    `;
  }
}

function logout() {
  localStorage.removeItem("token");
  location.href = "/login.html";
}

document.addEventListener("DOMContentLoaded", loadNavbar);
