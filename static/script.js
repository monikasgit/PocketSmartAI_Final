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


// Show the correct fields for each planner

function updatePlannerFields() {

    const selected = planner.value;

    homeFields.hidden = selected !== "home";

    partyFields.hidden = selected !== "party";

    jewelryFields.hidden = selected !== "jewelry";

    guestsInput.required = selected === "party";

    eventTypeInput.required = selected === "party";
}


// Listen for planner changes

planner.addEventListener(
    "change",
    updatePlannerFields
);


// Initialize planner fields

updatePlannerFields();


// Validate the form before submission

form.addEventListener("submit", function (event) {

    const budgetInput = document.getElementById("budget");

    const budget = Number(budgetInput.value);

    if (!Number.isFinite(budget) || budget <= 0) {

        event.preventDefault();

        alert("Please enter a budget greater than zero.");

        budgetInput.focus();

        return;
    }


    // Validate the number of guests

    if (planner.value === "party") {

        const guests = Number(guestsInput.value);

        if (!Number.isInteger(guests) || guests < 1) {

            event.preventDefault();

            alert("Please enter at least one guest.");

            guestsInput.focus();

            return;
        }
    }


    // Validate the optional image

    if (
        planner.value === "jewelry" &&
        imageInput.files.length > 0
    ) {

        const image = imageInput.files[0];

        if (!image.type.startsWith("image/")) {

            event.preventDefault();

            alert("Please select a valid image.");

            return;
        }


        if (image.size > 5 * 1024 * 1024) {

            event.preventDefault();

            alert("Please upload an image smaller than 5 MB.");

            return;
        }
    }


    // Show loading status

    submitButton.disabled = true;

    submitButton.textContent =
        "Generating recommendations...";

});


// Copy the recommendations

copyButton.addEventListener(
    "click",
    async function () {

        const textToCopy = result.innerText.trim();

        if (!textToCopy) {

            alert("No recommendations available to copy.");

            return;
        }


        try {

            await navigator.clipboard.writeText(textToCopy);

            alert("Recommendations copied successfully!");

        } catch (error) {

            alert(
                "Copy is unavailable in this browser. " +
                "Please select and copy the text manually."
            );

        }

    }
);
