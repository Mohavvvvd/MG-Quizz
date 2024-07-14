
document.addEventListener("DOMContentLoaded", function() {
    let navLinks = document.querySelectorAll(".nav li a:not(.logout)");
    document.querySelector("iframe").src = "/welcome";
    navLinks.forEach(function(link) {
      link.addEventListener("click", function(event) {
        event.preventDefault();
        let href = link.getAttribute("href");
        document.querySelector("iframe").src = href;
      });
    });
  });