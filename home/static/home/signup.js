document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const errorMsg = document.getElementById("errorMsg");

  form.addEventListener("submit", function (e) {
    if (password.value !== confirmPassword.value) {
      errorMsg.style.display = "block";
      e.preventDefault();
    } else {
      errorMsg.style.display = "none";
    }
  });
});

