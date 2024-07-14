window.addEventListener("DOMContentLoaded", function() {
    const b = document.getElementById("si");
    const loginForm = document.getElementsByClassName("login-form")[0];
    const signupForm = document.getElementsByClassName("signup-form")[0];
    const backToLoginButton = document.getElementById("back");
  
    b.addEventListener("click", function() {
      loginForm.classList.toggle("hidden");
      signupForm.classList.toggle("hidden");
    });
  
    backToLoginButton.addEventListener("click", function() {
      loginForm.classList.toggle("hidden");
      signupForm.classList.toggle("hidden");
    });
  });