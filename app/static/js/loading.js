document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
        document.getElementById("loading-screen").classList.remove("w3-hide");
    });
});

window.addEventListener("load", () => {
    document.getElementById("loading-screen").classList.add("w3-hide");
})