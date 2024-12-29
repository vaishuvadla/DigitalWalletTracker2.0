document.addEventListener('DOMContentLoaded', function () {
    fetch('/dashboard-data')
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);
            createCharts(data);
        })
        .catch(error => console.error('Error:', error));
});

function createCharts(data) {
    updateSavingsSuggestions(data.savings_suggestions);
    updateSpendingAlerts(data.alerts);
    createCombinedTransactionsChart(data);
    createYearlyComparisonCharts(data.monthly_comparison);
    createEnhancedTimeIntervalChart(data.top_time_intervals);
    createInflowOutflowChart(data);
}

//savings chart
function updateSavingsSuggestions(suggestions) {
    const list = document.getElementById('savings-suggestions-list');
    list.innerHTML = Object.entries(suggestions)
        .map(([category, amount], index) => `
            <div class="metric-card">
                <div class="metric-header">
                    <h4>${category}</h4>
                    <div class="metric-icon">💰</div>
                </div>
                <div class="metric-value">₹${amount.toFixed(2)}</div>
                <div class="metric-label">Potential Savings</div>
            </div>
        `).join('');
}

//spending chart
function updateSpendingAlerts(alerts) {
    const list = document.getElementById('spending-alerts-list');
    list.innerHTML = alerts.map(alert => `
        <div class="alert-metric">
            <div class="alert-header">
                <div class="alert-icon">⚠️</div>
                <div class="alert-timestamp">Now</div>
            </div>
            <div class="alert-message">${alert}</div>
        </div>
    `).join('');
}

//credit and debit chart
function createCombinedTransactionsChart(data) {
    const ctx = document.getElementById('combined-transactions-chart').getContext('2d');
    let activeChart = 'credit';
    
    // Sort transactions by date
    const creditData = {
        dates: [...data.credit_chart_data.dates].sort(),
        amounts: [...data.credit_chart_data.amounts]
    };
    const debitData = {
        dates: [...data.debit_chart_data.dates].sort(),
        amounts: [...data.debit_chart_data.amounts]
    };

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: creditData.dates,
            datasets: [{
                label: 'Credit Transactions',
                data: creditData.amounts,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0, // Prevent label rotation
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });

    // Add click handlers for the tabs
    document.querySelectorAll('.chart-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const type = tab.dataset.chart;
            if (type === activeChart) return;

            document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeChart = type;

            chart.data.labels = type === 'credit' ? creditData.dates : debitData.dates;
            chart.data.datasets[0] = {
                label: `${type.charAt(0).toUpperCase() + type.slice(1)} Transactions`,
                data: type === 'credit' ? creditData.amounts : debitData.amounts,
                borderColor: type === 'credit' ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)',
                backgroundColor: type === 'credit' ? 'rgba(75, 192, 192, 0.1)' : 'rgba(255, 99, 132, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4
            };
            chart.update();
        });
    });
}

//time interval
function createEnhancedTimeIntervalChart(data) {
    // Process data to create time ranges
    const processedData = data.map(d => {
        const hour = parseInt(d.time.split(':')[0]);
        return {
            range: `${hour}:00 - ${hour + 1}:00`,
            count: d.transaction_count
        };
    });

    const ctx = document.getElementById('timeIntervalChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: processedData.map(d => d.range),
            datasets: [{
                label: 'Transactions',
                data: processedData.map(d => d.count),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true
                    },
                    ticks: {
                        maxRotation: 0, // Prevent label rotation
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Additional functions remain the same...

function createYearlyComparisonCharts(data) {
    // Group data by year
    const groupedByYear = data.reduce((acc, item) => {
        const year = new Date(item.date).getFullYear();
        if (!acc[year]) acc[year] = [];
        acc[year].push(item);
        return acc;
    }, {});

    // Create year tabs
    const yearTabs = document.getElementById('yearTabs');
    const chartsContainer = document.getElementById('yearlyChartsContainer');
    yearTabs.innerHTML = ''; // Clear existing tabs
    
    Object.keys(groupedByYear).sort().forEach((year, index) => {
        // Create tab button (changed from div to button)
        const tab = document.createElement('button');
        tab.className = `year-tab ${index === 0 ? 'active' : ''}`;
        tab.textContent = year;
        yearTabs.appendChild(tab);

        // Create chart container
        const chartDiv = document.createElement('div');
        chartDiv.className = 'yearly-chart';
        chartDiv.style.display = index === 0 ? 'block' : 'none';
        
        const canvas = document.createElement('canvas');
        chartDiv.appendChild(canvas);
        chartsContainer.appendChild(chartDiv);

        // Create chart
        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: groupedByYear[year].map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleString('default', { month: 'long' });
                }),
                datasets: [{
                    label: `Monthly Spending ${year}`,
                    data: groupedByYear[year].map(item => item.amount),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Add tab click event
        tab.addEventListener('click', () => {
            // Update active tab
            document.querySelectorAll('.year-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show selected chart
            document.querySelectorAll('.yearly-chart').forEach(c => c.style.display = 'none');
            chartDiv.style.display = 'block';
        });
    });
}

function createInflowOutflowChart(data) {
    const ctx = document.getElementById('inflow-outflow-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Inflows', 'Outflows'],
            datasets: [{
                data: [data.inflows, data.outflows],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true, // Changed to true
            plugins: {
                legend: {
                    position: 'right', // Move legend to the right
                    labels: {
                        boxWidth: 12, // Smaller legend boxes
                        padding: 10 // Less padding
                    }
                }
            }
        }
    });
}