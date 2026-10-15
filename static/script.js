const planner = document.getElementById("planner");
const form = document.getElementById("budgetForm");

const homeFields = document.getElementById("homeFields");
const partyFields = document.getElementById("partyFields");
const jewelryFields = document.getElementById("jewelryFields");

const guestsInput = document.getElementById("guests");
const eventTypeInput = document.getElementById("event_type");

const resultSection = document.getElementById("resultSection");
const result = document.getElementById("result");

const submitButton = document.getElementById("submitButton");
const copyButton = document.getElementById("copyButton");

const imageInput = document.getElementById("outfit_image");

function updatePlannerFields() {
    const selected = planner.value;

    homeFields.hidden = selected !== "home";
    partyFields.hidden = selected !== "party";
    jewelryFields.hidden = selected !== "jewelry";

    guestsInput.required = selected === "party";
    eventTypeInput.required = selected === "party";
}

planner.addEventListener("change", updatePlannerFields);

updatePlannerFields();

form.addEventListener("submit", function (event) {
    const budget = Number(
        document.getElementById("budget").value
    );

    if (!Number.isFinite(budget) || budget <= 0) {
        event.preventDefault();
        alert("Please enter a budget greater than zero.");
        return;
    }

    if (
        planner.value === "jewelry" &&
        imageInput.files.length > 0
    ) {
        const image = imageInput.files[0];

        if (image.size > 5 * 1024 * 1024) {
            event.preventDefault();
            alert("Please upload an image smaller than 5 MB.");
            return;
        }
    }

    submitButton.disabled = true;
    submitButton.textContent = "Generating recommendations...";
});

copyButton.addEventListener("click", async function () {
    try {
        await navigator.clipboard.writeText(result.innerText);

        alert("Recommendations copied successfully!");

    } catch (error) {
        alert(
            "Copy is unavailable in this browser. Please select and copy the text manually."
        );
    }
});
