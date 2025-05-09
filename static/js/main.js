document.addEventListener('DOMContentLoaded', function() {
    const rideForm = document.getElementById('rideForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const matchFound = document.getElementById('matchFound');
    const suggestions = document.getElementById('suggestions');
    const initialState = document.getElementById('initialState');
    let demandChart = null;

    // Set default datetime to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('dropTime').value = now.toISOString().slice(0, 16);

    function validateForm() {
        const cabId = document.getElementById('cabId').value.trim();
        const pickup = document.getElementById('pickup').value;
        const drop = document.getElementById('drop').value;
        const dropTime = document.getElementById('dropTime').value;

        if (!cabId) {
            alert('Please enter a valid Cab ID');
            return false;
        }

        if (!pickup) {
            alert('Please select a pickup location');
            return false;
        }

        if (!drop) {
            alert('Please select a drop location');
            return false;
        }

        if (pickup === drop) {
            alert('Pickup and drop locations cannot be the same');
            return false;
        }

        if (!dropTime) {
            alert('Please select a drop time');
            return false;
        }

        return true;
    }

    rideForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        // Show loading spinner
        loadingSpinner.style.display = 'block';
        resultsSection.style.display = 'none';
        
        const formData = {
            cab_id: document.getElementById('cabId').value,
            pickup: document.getElementById('pickup').value,
            drop: document.getElementById('drop').value,
            drop_time: new Date(document.getElementById('dropTime').value).toISOString()
        };

        console.log('Form Data:', formData);

        try {
            const response = await fetch('/complete_ride', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            console.log('Response:', response);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error');
            }

            const data = await response.json();
            
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            resultsSection.style.display = 'block';

            if (data.status === 'match found') {
                displayMatch(data.ride_details);
            } else {
                displaySuggestions(data.suggested_zones);
            }
        } catch (error) {
            console.error('Error:', error);
            loadingSpinner.style.display = 'none';
            alert(`Error: ${error.message || 'Something went wrong'}`);
        }
    });

    function displayMatch(matches) {
        matchFound.style.display = 'block';
        suggestions.style.display = 'none';
        initialState.style.display = 'none';
        
        // Create matches display
        const matchesHTML = matches.map(match => {
            const matchTime = new Date(match.pickup_time);
            const formattedTime = matchTime.toLocaleString();
            
            return `
                <div class="match-item fade-in">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Return Trip Option</h5>
                        <span class="badge bg-success">Available</span>
                    </div>
                    <div class="match-stats">
                        <div class="stat-item">
                            <div class="stat-value">${match.pickup}</div>
                            <div class="stat-label">Pickup</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${match.drop}</div>
                            <div class="stat-label">Drop</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${match.time_difference_minutes}</div>
                            <div class="stat-label">Wait (mins)</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${match.passengers}</div>
                            <div class="stat-label">Passengers</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        document.getElementById('matchDetails').innerHTML = `
            <h5 class="mb-4">${matches.length} Return Trip${matches.length > 1 ? 's' : ''} Found</h5>
            ${matchesHTML}
        `;

        // Create bar chart for matches
        const ctx = document.createElement('canvas');
        document.getElementById('matchChart').innerHTML = '';
        document.getElementById('matchChart').appendChild(ctx);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: matches.map(m => `${m.pickup} → ${m.drop}`),
                datasets: [
                    {
                        label: 'Wait Time (minutes)',
                        data: matches.map(m => m.time_difference_minutes),
                        backgroundColor: 'rgba(76, 201, 240, 0.7)',
                        borderColor: 'rgba(76, 201, 240, 1)',
                        borderWidth: 2,
                        borderRadius: 8
                    },
                    {
                        label: 'Passengers',
                        data: matches.map(m => m.passengers),
                        backgroundColor: 'rgba(67, 97, 238, 0.7)',
                        borderColor: 'rgba(67, 97, 238, 1)',
                        borderWidth: 2,
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Return Trip Comparison',
                        font: {
                            size: 16,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    function displaySuggestions(suggestedZones) {
        matchFound.style.display = 'none';
        suggestions.style.display = 'block';
        initialState.style.display = 'none';

        // Create bar chart
        const ctx = document.createElement('canvas');
        document.getElementById('demandChart').innerHTML = '';
        document.getElementById('demandChart').appendChild(ctx);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: suggestedZones.map(zone => zone.zone),
                datasets: [{
                    label: 'Demand Score',
                    data: suggestedZones.map(zone => zone.score),
                    backgroundColor: [
                        'rgba(67, 97, 238, 0.7)',
                        'rgba(76, 201, 240, 0.7)',
                        'rgba(247, 37, 133, 0.7)'
                    ],
                    borderColor: [
                        'rgba(67, 97, 238, 1)',
                        'rgba(76, 201, 240, 1)',
                        'rgba(247, 37, 133, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Predicted Demand by Zone',
                        font: {
                            size: 16,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        title: {
                            display: true,
                            text: 'Demand Score'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

        // Create zones list
        const zonesHTML = suggestedZones.map((zone, index) => `
            <div class="suggestion-item fade-in" style="animation-delay: ${index * 0.1}s">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="zone-badge bg-${index === 0 ? 'primary' : index === 1 ? 'info' : 'warning'}">
                            <i class="fas fa-map-marker-alt me-2"></i>${zone.zone}
                        </span>
                    </div>
                    <div class="demand-score">
                        ${zone.score.toFixed(2)}
                        <small class="text-muted ms-2">demand score</small>
                    </div>
                </div>
            </div>
        `).join('');

        document.getElementById('zonesList').innerHTML = zonesHTML;
    }

    // Add form validation styles
    document.querySelectorAll('.form-control, .form-select').forEach(element => {
        element.addEventListener('invalid', function(e) {
            e.preventDefault();
            this.classList.add('is-invalid');
        });

        element.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
}); 