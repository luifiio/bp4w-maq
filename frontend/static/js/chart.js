// Chart.js configuration and initialization
let tempChart, pressureChart, throttleChart;
const MAX_DATA_POINTS = 100; // Keep last 100 data points

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
});

function initCharts() {
    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: '#666',
                    font: {
                        size: 11,
                        family: "'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Time (s)',
                    color: '#999',
                    font: {
                        size: 10,
                        family: "'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }
                },
                grid: {
                    color: '#e5e5e5'
                },
                ticks: {
                    color: '#999',
                    font: {
                        size: 10
                    }
                }
            },
            y: {
                grid: {
                    color: '#e5e5e5'
                },
                ticks: {
                    color: '#999',
                    font: {
                        size: 10
                    }
                }
            }
        }
    };

    // Temperature chart
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Coolant Temp (°C)',
                    data: [],
                    borderColor: '#1a1a1a',
                    backgroundColor: 'rgba(26, 26, 26, 0.1)',
                    borderWidth: 1.5,
                    tension: 0.4
                },
                {
                    label: 'Oil Temp (°C)',
                    data: [],
                    borderColor: '#666',
                    backgroundColor: 'rgba(102, 102, 102, 0.1)',
                    borderWidth: 1.5,
                    tension: 0.4
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: '#999',
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });

    // Pressure chart
    const pressureCtx = document.getElementById('pressureChart').getContext('2d');
    pressureChart = new Chart(pressureCtx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Oil Pressure (PSI)',
                data: [],
                borderColor: '#1a1a1a',
                backgroundColor: 'rgba(26, 26, 26, 0.1)',
                borderWidth: 1.5,
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Pressure (PSI)',
                        color: '#999',
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });

    // Throttle chart
    const throttleCtx = document.getElementById('throttleChart').getContext('2d');
    throttleChart = new Chart(throttleCtx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Throttle Position (%)',
                data: [],
                borderColor: '#1a1a1a',
                backgroundColor: 'rgba(26, 26, 26, 0.1)',
                borderWidth: 1.5,
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Position (%)',
                        color: '#999',
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(data) {
    if (!data || !data.timestamp) return;
    
    const timestamp = data.timestamp;
    
    // Update temperature chart
    if (data.coolant_temp !== null && data.coolant_temp !== undefined) {
        addDataPoint(tempChart, 0, timestamp, data.coolant_temp);
    }
    if (data.oil_temp !== null && data.oil_temp !== undefined) {
        addDataPoint(tempChart, 1, timestamp, data.oil_temp);
    }
    
    // Update pressure chart
    if (data.oil_pressure !== null && data.oil_pressure !== undefined) {
        addDataPoint(pressureChart, 0, timestamp, data.oil_pressure);
    }
    
    // Update throttle chart
    if (data.throttle_position !== null && data.throttle_position !== undefined) {
        addDataPoint(throttleChart, 0, timestamp, data.throttle_position);
    }
}

// Helper to add data point and maintain max length
function addDataPoint(chart, datasetIndex, x, y) {
    const dataset = chart.data.datasets[datasetIndex];
    
    // Add new point
    dataset.data.push({ x, y });
    
    // Remove old points if exceeding max
    if (dataset.data.length > MAX_DATA_POINTS) {
        dataset.data.shift();
    }
    
    // Update chart
    chart.update('none'); // 'none' mode for performance (no animation)
}