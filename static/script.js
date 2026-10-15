const planner = document.getElementById("planner");
const form = document.getElementById("budgetForm");

const homeFields = document.getElementById("homeFields");
const partyFields = document.getElementById("partyFields");
const jewelryFields = document.getElementById("jewelryFields");

const resultSection = document.getElementById("resultSection");
const result = document.getElementById("result");

const submitButton = document.getElementById("submitButton");
const copyButton = document.getElementById("copyButton");

function updatePlannerFields() {
    const selected = planner.value;

    homeFields.hidden = selected !== "home";
    partyFields.hidden = selected !== "party";
    jewelryFields.hidden = selected !== "jewelry";
}

planner.addEventListener("change", updatePlannerFields);

updatePlannerFields();

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const budget = Number(
        document.getElementById("budget").value
    );

    if (!Number.isFinite(budget) || budget <= 0) {
        alert("Please enter a valid budget.");
        return;
    }

    const details = {
        planner: planner.value,
        budget: budget,
        preferences:
            document.getElementById("preferences").value
    };

    if (planner.value === "home") {
        details.room_type =
            document.getElementById("room_type").value;
    }

    if (planner.value === "party") {
        details.guests =
            Number(document.getElementById("guests").value);

        details.occasion =
            document.getElementById("occasion").value;
    }

    if (planner.value === "jewelry") {
        details.jewelry_type =
            document.getElementById("jewelry_type").value;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Generating recommendations...";

    resultSection.hidden = false;
    result.textContent = "Please wait...";

    try {
        const response = await fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(details)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Could not get recommendations."
            );
        }

        result.textContent =
            data.recommendation ||
            data.result ||
            JSON.stringify(data, null, 2);

    } catch (error) {
        result.textContent =
            "Unable to get recommendations. Please check the server and try again.\n\n" +
            error.message;

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Get Recommendations";
    }
});

copyButton.addEventListener("click", async function () {
    try {
        await navigator.clipboard.writeText(
            result.textContent
        );

        alert("Recommendations copied!");

    } catch {
        alert("Copy is unavailable in this browser.");
    }
});
