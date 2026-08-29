
// Animates metric percentage from 0 to its expected value
function animate(elementId, metricValue) {
    const element = document.getElementById(elementId);

    // Prevents crash when HTML element hasn't loaded in yet
    if (!element) {
        return window.dash_clientside.no_update;
    }

    const projectedValue = metricValue * 100;
    let currentValue = 0.00;

    // Increments displayed performance metric every millisecond
    const interval = setInterval(() => {
        currentValue += 0.51;

        if (currentValue >= projectedValue) {
            currentValue = projectedValue;
            clearInterval(interval);
        }

        element.textContent = `${currentValue.toFixed(2)}%`;
    }, 1);

    return window.dash_clientside.no_update;
}

// Runs animations for accuracy, precision, recall, f1-score, and roc-auc 
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    dashboard_animations: {

        animateAccuracy: function(metrics, selectedModel) {
            const stages = metrics[selectedModel]
            const lastStageName = Object.keys(stages).at(-1)

            return animate(
                "accuracy-score-value",
                stages[lastStageName]["accuracy"]
            );
        },

        animatePrecision: function(metrics, selectedModel) {
            const stages = metrics[selectedModel]
            const lastStageName = Object.keys(stages).at(-1)

            return animate(
                "precision-score-value",
                stages[lastStageName]["precision"]
            );
        },

        animateRecall: function(metrics, selectedModel) {
            const stages = metrics[selectedModel]
            const lastStageName = Object.keys(stages).at(-1)

            return animate(
                "recall-score-value",
                stages[lastStageName]["recall"]
            );
        },

        animateF1: function(metrics, selectedModel) {
            const stages = metrics[selectedModel]
            const lastStageName = Object.keys(stages).at(-1)

            return animate(
                "f1-score-value",
                stages[lastStageName]["f1"]
            );
        },

        animateRocAuc: function(metrics, selectedModel) {
            const stages = metrics[selectedModel]
            const lastStageName = Object.keys(stages).at(-1)

            return animate(
                "roc-auc-score-value",
                stages[lastStageName]["roc auc"]
            );
        }
    }
});

// Highlights corresponding characteristics on hover for easier readability and examination
document.addEventListener("mouseover", event => {
    const element = event.target.closest("[data-metric]");
    if (!element) return;

    const metric = element.dataset.metric;

    document
        .querySelectorAll(`[data-metric="${metric}"]`)
        .forEach(match => match.classList.add("highlight"));
});

// Removes highlight of the characteristics when user moves cursor off
document.addEventListener("mouseout", event => {
    const element = event.target.closest("[data-metric]");
    if (!element) return;

    const metric = element.dataset.metric;

    document
        .querySelectorAll(`[data-metric="${metric}"]`)
        .forEach(match => match.classList.remove("highlight"))
    }
)

// Removes identical features from profiles when there exist too many features
setTimeout(() => {
    // Collects all bullet points associated with a Profile Card
    const bullets = document.querySelectorAll("li[data-metric]");

    // Prevents feature removal if there are only 5 or less features
    if (bullets.length <= 10) {
        return;
    }

    const counts = {};

    // Tallies up the number of text instances in bullet points
    bullets.forEach(li => {
        const text = li.textContent;
        counts[text] = (counts[text] || 0) + 1;
    })

    // Removes the bullet points that don't distinguish between profiles
    bullets.forEach(li => {
        const text = li.textContent;
        if (counts[text] > 1) {
            li.remove();
        }
    })
}, 3_000)();
