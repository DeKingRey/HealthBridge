document.addEventListener("DOMContentLoaded", () => {
    const btns = document.querySelectorAll(".fa-eye");
    const passwordFields = document.querySelectorAll(".password");

    btns.forEach((btn, index) => {
        btn.addEventListener("click", ()=> {
            const isPassword = passwordFields[index].type === "password";
            passwordFields[index].type = isPassword ? "text" : "password"

            btn.classList.toggle("fa-eye", !isPassword);
            btn.classList.toggle("fa-eye-slash", isPassword);
        });
    });
});