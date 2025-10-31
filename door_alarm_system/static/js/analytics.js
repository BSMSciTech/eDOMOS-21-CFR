// Analytics page JavaScript
function initializeCharts(eventsData, daysData) {
    // Initialize pie chart for event types
    const eventTypeCtx = document.getElementById('eventTypeChart').getContext('2d');
    new Chart(eventTypeCtx, {
        type: 'pie',
        data: {
            labels: eventsData.labels,
            datasets: [{
                label: 'Event Count',
                data: eventsData.data,
                backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)']
            }]
        },
        options: { 
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Initialize line chart for events per day
    const eventDayCtx = document.getElementById('eventDayChart').getContext('2d');
    new Chart(eventDayCtx, {
        type: 'line',
        data: {
            labels: daysData.labels,
            datasets: [{
                label: 'Events per Day',
                data: daysData.data,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)'
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
}
