document.addEventListener("DOMContentLoaded", () => {
  const headings = document.querySelectorAll("article h1, article h2, article h3, article h4");
  const tocLinks = document.querySelectorAll(".toc a");

  const activateLink = (id) => {
    tocLinks.forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + id));
  };

  window.addEventListener("scroll", () => {
    let currentId = "";
    headings.forEach(h => {
      const rect = h.getBoundingClientRect();
      if (rect.top < window.innerHeight / 2) {
        currentId = h.id;
      }
    });
    if (currentId) activateLink(currentId);
  });
});
