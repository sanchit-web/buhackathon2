async function loadInventory() {
    const response = await fetch('/api/inventory');
    const data = await response.json();
    const inventoryList = document.getElementById('inventory-list');
    inventoryList.innerHTML = data.map(item => `
        <p>${item.product} (${item.location}): ${item.stock} units</p>
    `).join('');
}

async function loadForecast(productId) {
    const response = await fetch('/api/forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: productId })
    });
    const data = await response.json();
    const ctx = document.getElementById('forecastChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['6', '7', '8', '9', '10'],
            datasets: [{
                label: `Forecast for ${data.product}`,
                data: data.forecast,
                borderColor: 'blue',
                fill: false
            }]
        }
    });
}

async function loadAlerts() {
    const response = await fetch('/api/alerts');
    const data = await response.json();
    const alertsList = document.getElementById('alerts-list');
    alertsList.innerHTML = data.map(alert => `
        <p>${alert.product} (${alert.location}): ${alert.alert}</p>
    `).join('');
}

loadInventory();
loadForecast(1); // Example: Forecast for product ID 1
loadAlerts();
