/* ============================================
   DASHBOARD CHARTS - CHART.JS & LEAFLET.JS
   ============================================ */

// Chart.js color palette (professional corporate colors)
const chartColors = {
    primary: '#1e3a5f',
    secondary: '#2563eb',
    accent: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    lightGray: '#f3f4f6',
    mediumGray: '#e5e7eb',
    darkGray: '#6b7280',
};

// Color palette for multiple datasets
const colorPalettes = [
    '#1e3a5f', '#2563eb', '#06b6d4', '#10b981', '#f59e0b',
    '#ef4444', '#3b82f6', '#ec4899', '#8b5cf6', '#14b8a6',
    '#f97316', '#6366f1', '#a855f7', '#06b6d4', '#0ea5e9',
];

// Chart.js defaults
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu'";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#6b7280';
Chart.defaults.borderColor = '#e5e7eb';

// Get chart data from the DOM
function getChartData() {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement) {
        console.error('Chart data element not found');
        return null;
    }
    try {
        return JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error('Error parsing chart data:', error);
        return null;
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const data = getChartData();
    if (data) {
        initializeProjectsByCountryChart(data);
        initializeLanguageDistributionChart(data);
        initializeProjectsByYearChart(data);
        initializeRevenueByYearChart(data);
        initializeTopCountriesChart(data);
        initializeTopClientsChart(data);
        initializeProjectsPerMonthChart(data);
        initializeWorldMap(data);
    }
});

/* ============================================
   CHART 1: PROJECTS BY COUNTRY (Bar Chart)
   ============================================ */
function initializeProjectsByCountryChart(data) {
    const ctx = document.getElementById('projectsByCountryChart');
    if (!ctx) return;

    const chartData = data.projectsByCountry || [];
    const labels = chartData.map(item => item.country);
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Projects',
                data: counts,
                backgroundColor: colorPalettes.slice(0, labels.length),
                borderColor: colorPalettes.slice(0, labels.length),
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: colorPalettes.slice(0, labels.length),
                hoverBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return 'Projects: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return value;
                        }
                    }
                },
                y: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 2: LANGUAGE DISTRIBUTION (Pie Chart)
   ============================================ */
function initializeLanguageDistributionChart(data) {
    const ctx = document.getElementById('languageDistributionChart');
    if (!ctx) return;

    const chartData = data.languageDistribution || [];
    const languageNames = data.languageNames || {};
    
    const labels = chartData.map(item => {
        const langCode = item.language;
        return languageNames[langCode] || langCode;
    });
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colorPalettes,
                borderColor: '#ffffff',
                borderWidth: 3,
                hoverOffset: 10,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '500', size: 12 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 3: PROJECTS BY YEAR (Line Chart)
   ============================================ */
function initializeProjectsByYearChart(data) {
    const ctx = document.getElementById('projectsByYearChart');
    if (!ctx) return;

    const chartData = data.projectsByYear || [];
    const labels = chartData.map(item => item.year);
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projects Created',
                data: counts,
                borderColor: chartColors.primary,
                backgroundColor: 'rgba(30, 58, 95, 0.05)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                hoverBackgroundColor: chartColors.primary,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    },
                    ticks: {
                        stepSize: 1,
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 3B: REVENUE BY YEAR (Bar Chart in €)
   ============================================ */
function initializeRevenueByYearChart(data) {
    const ctx = document.getElementById('revenueByYearChart');
    if (!ctx) return;

    const chartData = data.revenueByYear || [];
    
    // Handle empty data
    if (!chartData || chartData.length === 0) {
        console.warn('No revenue data available for chart');
        // Display a message in the canvas
        const canvas = document.getElementById('revenueByYearChart');
        canvas.parentElement.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:400px;color:#999;font-size:16px;">No revenue data available</div>';
        return;
    }
    
    const labels = chartData.map(item => item.year);
    const revenues = chartData.map(item => item.revenue);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue (EUR €)',
                data: revenues,
                borderColor: '#06b6d4',
                backgroundColor: 'rgba(6, 182, 212, 0.6)',
                borderWidth: 2,
                borderRadius: 6,
                hoverBackgroundColor: '#0891b2',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return '€ ' + context.parsed.y.toLocaleString('de-DE', { 
                                minimumFractionDigits: 2, 
                                maximumFractionDigits: 2 
                            });
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return '€ ' + value.toLocaleString('de-DE', { 
                                minimumFractionDigits: 0 
                            });
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 4: TOP 10 COUNTRIES (Bar Chart)
   ============================================ */
function initializeTopCountriesChart(data) {
    const ctx = document.getElementById('topCountriesChart');
    if (!ctx) return;

    const chartData = data.topCountries || [];
    const labels = chartData.map(item => item.country);
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projects',
                data: counts,
                backgroundColor: chartColors.success,
                borderColor: chartColors.success,
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: '#0d9488',
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return 'Projects: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    }
                },
                y: {
                    grid: {
                        display: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 5: TOP 10 CLIENTS (Horizontal Bar)
   ============================================ */
function initializeTopClientsChart(data) {
    const ctx = document.getElementById('topClientsChart');
    if (!ctx) return;

    const chartData = data.topClients || [];
    const labels = chartData.map(item => {
        const label = item.client_info || 'Unknown';
        return label.length > 30 ? label.substring(0, 30) + '...' : label;
    });
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projects',
                data: counts,
                backgroundColor: chartColors.accent,
                borderColor: chartColors.accent,
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: '#0891b2',
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return 'Projects: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    }
                },
                y: {
                    grid: {
                        display: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   CHART 6: PROJECTS PER MONTH (Area Chart)
   ============================================ */
function initializeProjectsPerMonthChart(data) {
    const ctx = document.getElementById('projectsPerMonthChart');
    if (!ctx) return;

    const chartData = data.projectsPerMonth || [];
    const labels = chartData.map(item => {
        const date = new Date(item.month);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });
    const counts = chartData.map(item => item.count);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projects Created',
                data: counts,
                borderColor: chartColors.secondary,
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: chartColors.secondary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600', size: 13 },
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 },
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false,
                    },
                    ticks: {
                        stepSize: 1,
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

/* ============================================
   MAP: WORLD MAP (Leaflet.js)
   ============================================ */
function initializeWorldMap(data) {
    const mapElement = document.getElementById('worldMap');
    if (!mapElement) return;

    // Initialize map centered on world
    const map = L.map(mapElement).setView([20, 0], 2);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 1,
    }).addTo(map);

    // Get country data
    const countryData = data.countryData || {};
    const maxProjects = Math.max(...Object.values(countryData), 1);

    // Country coordinates (approximate)
    const countryCoordinates = {
        'Germany': [51.1657, 10.4515],
        'United States': [37.0902, -95.7129],
        'United Kingdom': [55.3781, -3.4360],
        'France': [46.2276, 2.2137],
        'India': [20.5937, 78.9629],
        'China': [35.8617, 104.1954],
        'Japan': [36.2048, 138.2529],
        'Brazil': [-14.2350, -51.9253],
        'Mexico': [23.6345, -102.5528],
        'Canada': [56.1304, -106.3468],
        'Australia': [-25.2744, 133.7751],
        'South Africa': [-30.5595, 22.9375],
        'Saudi Arabia': [23.8859, 45.0792],
        'UAE': [23.4241, 53.8478],
        'Singapore': [1.3521, 103.8198],
        'Malaysia': [4.2105, 101.6964],
        'Thailand': [15.8700, 100.9925],
        'Vietnam': [14.0583, 108.2772],
        'Indonesia': [-0.7893, 113.9213],
        'Philippines': [12.8797, 121.7740],
    };

    // Add circles for each country with projects
    Object.entries(countryData).forEach(([country, count]) => {
        const coords = countryCoordinates[country];
        if (coords) {
            const radius = Math.sqrt(count) * 50000; // Proportional circle size
            const opacity = 0.5 + (count / maxProjects) * 0.5;

            const circle = L.circle(coords, {
                color: chartColors.primary,
                fillColor: chartColors.secondary,
                fillOpacity: opacity,
                weight: 2,
                radius: radius,
                dashArray: '5, 5'
            }).bindPopup(`<strong>${country}</strong><br>Projects: ${count}`);

            circle.addTo(map);
        }
    });

    // Fit map to bounds
    map.fitBounds([[-85, -180], [85, 180]]);
}

// Responsive charts
window.addEventListener('resize', function() {
    // Charts automatically resize due to responsive: true option
});

console.log('Dashboard charts initialized successfully');
