// document.addEventListener('DOMContentLoaded', function () {
//   const form = document.getElementById('signup-form');
//   const password = document.getElementById('password');
//   const confirmPassword = document.getElementById('confirmPassword');
//   const errorMsg = document.getElementById('errorMsg');
//   const errorMessages = document.getElementById('error-messages');
//   const radios = document.getElementsByName('user-type');
//
//   form.addEventListener('submit', function (e) {
//     e.preventDefault();
//
//     errorMsg.style.display = 'none';
//     errorMessages.textContent = '';
//
//     if (password.value !== confirmPassword.value) {
//       errorMsg.style.display = 'block';
//       return;
//     }
//
//     let selectedUserType = null;
//     for (let radio of radios) {
//       if (radio.checked) {
//         selectedUserType = radio.value;
//         break;
//       }
//     }
//
//     if (!selectedUserType) {
//       errorMessages.textContent = "Please select a user type.";
//       return;
//     }
//
//     // Get user input values
//     const firstName = form.querySelector('input[name="First Name"]').value;
//     const lastName = form.querySelector('input[name="Last Name"]').value;
//     const email = form.querySelector('input[name="Email"]').value.toLowerCase();
//     const userPassword = password.value;
//
//     // Get existing users or initialize array
//     const users = JSON.parse(localStorage.getItem("users")) || [];
//
//     // Check for duplicate email
//     const existingUser = users.find(user => user.email === email);
//     if (existingUser) {
//       errorMessages.textContent = "An account with this email already exists.";
//       return;
//     }
//
//     // Add new user
//     const newUser = {
//       firstName,
//       lastName,
//       email,
//       password: userPassword,
//       userType: selectedUserType
//     };
//
//     users.push(newUser);
//     localStorage.setItem("users", JSON.stringify(users));
//
//     // Also set current session info
//     sessionStorage.setItem("userType", selectedUserType);
//     sessionStorage.setItem("loggedInUser", email);
//     localStorage.setItem("isLoggedIn", "true");
//
//     // Redirect
//     window.location.href = "/home/adminDashboard/";
//   });
// });
// signup.js
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

