document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search_input")
    const suggestions = document.getElementById("suggestions")
    var isHealth;

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase(); // Gets the users input and correctly formats
        suggestions.innerHTML = ""; 

        if (!query) return;

        // Checks for content which include the inputted search
        const matches = search_content.filter(content =>
            content.name.toLowerCase().includes(query)
        );  

        // Creates suggestions for each match for user to click
        matches.forEach(match => {
            // Creates a div element
            const div = document.createElement("div");
            div.textContent = match.name;
            div.classList.add("w3-bar-item", "w3-hover-light-grey");

            div.dataset.id = match.id // Id as attached data

            div.addEventListener("click", () => {
                input.value = match.name;

                if (isHealth)
                {
                    document.getElementById("health_info_id").value = div.dataset.id;
                    document.getElementById("existing_info").value = "True";
                }

                suggestions.innerHTML = "";
            });
            suggestions.appendChild(div);
        });
    });
});