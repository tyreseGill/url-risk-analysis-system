
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

        animateAccuracy: function(metrics) {
            return animate(
                "accuracy-score-value",
                metrics["Accuracy Score"]
            );
        },

        animatePrecision: function(metrics) {
            return animate(
                "precision-score-value",
                metrics["Precision Score"]
            );
        },

        animateRecall: function(metrics) {
            return animate(
                "recall-score-value",
                metrics["Recall Score"]
            );
        },

        animateF1: function(metrics) {
            return animate(
                "f1-score-value",
                metrics["F1-Score"]
            );
        },

        animateRocAuc: function(metrics) {
            return animate(
                "roc-auc-score-value",
                metrics["Roc-Auc Score"]
            );
        }
    }
});
