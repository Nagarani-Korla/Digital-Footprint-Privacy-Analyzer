// ==================================================
// TRACEGUARD AI - FRONTEND JAVASCRIPT
// ==================================================


// ==================================================
// ANALYZE TEXT
// ==================================================

async function analyzeText() {

    const text =
        document.getElementById("userText").value;

    if (text.trim() === "") {

        alert(
            "Please enter some text to analyze."
        );

        return;
    }

    document.getElementById("loading")
        .classList.remove("hidden");

    document.getElementById("results")
        .classList.add("hidden");


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                "Backend request failed"
            );
        }


        const data =
            await response.json();


        // ==================================================
        // RISK SCORE
        // ==================================================

        document.getElementById("riskScore").textContent =
            data.risk_score;


        // ==================================================
        // RISK PROGRESS BAR
        // ==================================================

        const riskProgressBar =
            document.getElementById("riskProgressBar");

        riskProgressBar.style.width =
            data.risk_score + "%";


        // ==================================================
        // RISK LEVEL
        // ==================================================

        const riskLevel =
            document.getElementById("riskLevel");

        riskLevel.textContent =
            data.risk_level + " Risk";

        riskLevel.className =
            "risk-level";


        const scoreCircle =
            document.querySelector(".score-circle");

        scoreCircle.className =
            "score-circle";


        if (data.risk_level === "High") {

            riskLevel.classList.add(
                "risk-high"
            );

            scoreCircle.classList.add(
                "score-high"
            );

        } else if (data.risk_level === "Medium") {

            riskLevel.classList.add(
                "risk-medium"
            );

            scoreCircle.classList.add(
                "score-medium"
            );

        } else {

            riskLevel.classList.add(
                "risk-low"
            );

            scoreCircle.classList.add(
                "score-low"
            );
        }


        // ==================================================
        // RISK EXPLANATION
        // ==================================================

        const explanation =
            document.getElementById(
                "riskExplanation"
            );


        if (data.risk_level === "High") {

            explanation.textContent =
                "Your text contains multiple pieces of personal information that could be combined to identify you or reveal sensitive details.";

        } else if (data.risk_level === "Medium") {

            explanation.textContent =
                "Your text contains some personal information that may create privacy risks if shared publicly.";

        } else {

            explanation.textContent =
                "Your text contains limited personal information and currently shows a relatively low privacy risk.";
        }


        // ==================================================
        // DETECTED INFORMATION
        // ==================================================

        const detectedData =
            document.getElementById(
                "detectedData"
            );

        detectedData.innerHTML = "";


        const compoundRisks =
            data.detected_data.filter(
                item =>
                    item.type.includes(
                        "Exposure"
                    ) ||
                    item.type.includes(
                        "Correlation Risk"
                    ) ||
                    item.type.includes(
                        "Absence"
                    )
            );


        const normalData =
            data.detected_data.filter(
                item =>
                    !item.type.includes(
                        "Exposure"
                    ) &&
                    !item.type.includes(
                        "Correlation Risk"
                    ) &&
                    !item.type.includes(
                        "Absence"
                    )
            );


        normalData.forEach(item => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "data-item";


            const strong =
                document.createElement(
                    "strong"
                );

            strong.textContent =
                item.type;


            const value =
                document.createElement(
                    "span"
                );

            value.className =
                "value";

            value.textContent =
                item.value;


            const small =
                document.createElement(
                    "small"
                );

            small.textContent =
                "Risk: " + item.risk;


            div.appendChild(strong);
            div.appendChild(value);
            div.appendChild(small);

            detectedData.appendChild(div);

        });


        // ==================================================
        // COMPOUND RISKS
        // ==================================================

        const compoundRisksContainer =
            document.getElementById(
                "compoundRisks"
            );

        compoundRisksContainer.innerHTML =
            "";


        compoundRisks.forEach(item => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "compound-item";


            const strong =
                document.createElement(
                    "strong"
                );

            strong.textContent =
                "⚠️ " + item.type;


            const value =
                document.createElement(
                    "span"
                );

            value.className =
                "value";

            value.textContent =
                item.value;


            const small =
                document.createElement(
                    "small"
                );

            small.textContent =
                "Risk: " + item.risk;


            div.appendChild(strong);
            div.appendChild(value);
            div.appendChild(small);

            compoundRisksContainer.appendChild(
                div
            );

        });


        // ==================================================
        // STATISTICS
        // ==================================================

        document.getElementById(
            "detectedCount"
        ).textContent =
            normalData.length;


        const highRiskItems =
            data.detected_data.filter(
                item =>
                    item.risk === "High"
            );


        document.getElementById(
            "highRiskCount"
        ).textContent =
            highRiskItems.length;


        // ==================================================
        // RISK BREAKDOWN
        // ==================================================

        const riskBreakdown =
            document.getElementById(
                "riskBreakdown"
            );

        riskBreakdown.innerHTML =
            "";


        let rawRiskScore = 0;


        function addRiskItem(
            name,
            points
        ) {

            rawRiskScore += points;


            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "breakdown-item";


            const span =
                document.createElement(
                    "span"
                );

            span.textContent =
                name;


            const strong =
                document.createElement(
                    "strong"
                );

            strong.textContent =
                "+" + points;


            div.appendChild(span);
            div.appendChild(strong);

            riskBreakdown.appendChild(
                div
            );
        }


        // Email

        data.detected_data
            .filter(
                item =>
                    item.type === "Email"
            )
            .forEach(() => {

                addRiskItem(
                    "Email Exposure",
                    20
                );

            });


        // Phone

        data.detected_data
            .filter(
                item =>
                    item.type ===
                    "Phone Number"
            )
            .forEach(() => {

                addRiskItem(
                    "Phone Number Exposure",
                    40
                );

            });


        // Person

        data.detected_data
            .filter(
                item =>
                    item.type === "PERSON"
            )
            .forEach(() => {

                addRiskItem(
                    "Person Information",
                    5
                );

            });


        // Organization

        data.detected_data
            .filter(
                item =>
                    item.type ===
                    "ORGANIZATION"
            )
            .forEach(() => {

                addRiskItem(
                    "Organization Information",
                    10
                );

            });


        // Location

        data.detected_data
            .filter(
                item =>
                    item.type ===
                    "LOCATION"
            )
            .forEach(() => {

                addRiskItem(
                    "Location Exposure",
                    20
                );

            });


        // Date

        data.detected_data
            .filter(
                item =>
                    item.type === "DATE"
            )
            .forEach(() => {

                addRiskItem(
                    "Date Exposure",
                    15
                );

            });


        // Compound risks

        compoundRisks.forEach(item => {

            let points = 0;


            if (
                item.type ===
                "Location + Date Exposure"
            ) {

                points = 15;

            } else if (
                item.type ===
                "Phone + Location Exposure"
            ) {

                points = 20;

            } else if (
                item.type ===
                "Identity Correlation Risk"
            ) {

                points = 15;

            } else if (
                item.type ===
                "Absence Exposure"
            ) {

                points = 25;
            }


            addRiskItem(
                item.type,
                points
            );

        });


        document.getElementById(
            "rawRiskScore"
        ).textContent =
            rawRiskScore;


        document.getElementById(
            "finalRiskScore"
        ).textContent =
            data.risk_score +
            " / 100";


        // ==================================================
        // INFERENCE ANALYSIS
        // ==================================================

        const inferenceContainer =
            document.getElementById(
                "inferences"
            );

        inferenceContainer.innerHTML =
            "";


        if (
            data.inferences &&
            data.inferences.length > 0
        ) {

            data.inferences.forEach(
                item => {

                    const div =
                        document.createElement(
                            "div"
                        );

                    div.className =
                        "inference-item";


                    const strong =
                        document.createElement(
                            "strong"
                        );

                    strong.textContent =
                        "🔎 " +
                        item.title;


                    const value =
                        document.createElement(
                            "span"
                        );

                    value.className =
                        "value";

                    value.textContent =
                        item.type;


                    const description =
                        document.createElement(
                            "p"
                        );

                    description.textContent =
                        item.description;


                    const small =
                        document.createElement(
                            "small"
                        );

                    small.textContent =
                        "Risk: " +
                        item.risk;


                    div.appendChild(strong);
                    div.appendChild(value);
                    div.appendChild(description);
                    div.appendChild(small);


                    inferenceContainer.appendChild(
                        div
                    );

                }
            );

        } else {

            const noInference =
                document.createElement(
                    "div"
                );

            noInference.className =
                "no-inference";


            noInference.textContent =
                "No significant personal inferences detected.";


            inferenceContainer.appendChild(
                noInference
            );
        }


        // ==================================================
        // RECOMMENDATIONS
        // ==================================================

        const recommendations =
            document.getElementById(
                "recommendations"
            );

        recommendations.innerHTML =
            "";


        data.recommendations.forEach(
            item => {

                const div =
                    document.createElement(
                        "div"
                    );

                div.className =
                    "recommendation-item";


                div.textContent =
                    "🛡️ " + item;


                recommendations.appendChild(
                    div
                );

            }
        );


        // ==================================================
        // SHOW RESULTS
        // ==================================================

        document.getElementById(
            "loading"
        ).classList.add("hidden");


        document.getElementById(
            "results"
        ).classList.remove("hidden");


    } catch (error) {

        console.error(error);


        document.getElementById(
            "loading"
        ).classList.add("hidden");


        alert(
            "Unable to analyze. Check that the FastAPI backend is running."
        );
    }
}


// ==================================================
// PRIVACY TEXT SANITIZER
// ==================================================

async function sanitizeText() {

    const text =
        document.getElementById(
            "userText"
        )
        .value
        .trim();


    if (!text) {

        alert(
            "Please enter some text first."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/sanitize",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text: text
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Sanitization failed"
            );
        }


        const data =
            await response.json();


        document.getElementById(
            "sanitizedText"
        ).textContent =
            data.sanitized_text;


        document.getElementById(
            "sanitizedResult"
        ).classList.remove(
            "hidden"
        );


    } catch (error) {

        console.error(error);


        alert(
            "Unable to sanitize the text. " +
            "Make sure the FastAPI server is running."
        );
    }
}


// ==================================================
// COPY SANITIZED TEXT
// ==================================================

async function copySanitizedText() {

    const text =
        document.getElementById(
            "sanitizedText"
        ).textContent;


    if (!text) {

        alert(
            "There is no sanitized text to copy."
        );

        return;
    }


    try {

        await navigator.clipboard.writeText(
            text
        );


        alert(
            "Sanitized text copied!"
        );


    } catch (error) {

        console.error(error);


        alert(
            "Unable to copy sanitized text."
        );
    }
}