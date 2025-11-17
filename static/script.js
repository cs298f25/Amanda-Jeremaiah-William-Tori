// --- Global variable to store our raw data from the API ---
let allAthleteData = [];

// --- Helper Functions (KEEP - No changes) ---

function formatDate(date) {
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}
        
function getWeekStart(date = new Date()) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
    
    // --- FIX ---
    // Create a new Date object *and* set its time to midnight
    const weekStartDate = new Date(d.setDate(diff));
    weekStartDate.setHours(0, 0, 0, 0); // Set to 00:00:00.000
    return weekStartDate;
}
        
function formatDateForAPI(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// --- NEW HELPER ---
// Gets the day name (e.g., "Monday") from a Date object
function getDayName(date) {
    // Note: getDay() returns 0 for Sunday, 1 for Monday, etc.
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
}

// --- NEW "TRANSLATION" FUNCTION ---
// Takes the raw data and processes it for a specific week
function processDataForWeek(weekStart) {
    // The /data endpoint returns activities, which we've transformed into athletes.
    // This UI is for one athlete. Try to find Tori, otherwise use the last athlete added.
    let athlete = allAthleteData.find(a => 
        (a.first_name && a.first_name.toLowerCase() === 'tori') || 
        (a.first_name && a.last_name && `${a.first_name} ${a.last_name}`.toLowerCase().includes('tori'))
    );
    
    // If Tori not found, use the last athlete (most recently added)
    if (!athlete && allAthleteData.length > 0) {
        athlete = allAthleteData[allAthleteData.length - 1];
    }
    
    if (!athlete) {
        // Return an empty structure if no data
        return { goal: 0, daily_mileage: {}, total: 0, remaining: 0 };
    }

    const goal = athlete.mileage_goal || 0;
    const weeklyRuns = {
        'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0,
        'Friday': 0, 'Saturday': 0, 'Sunday': 0
    };
    let total = 0;

    // Calculate the end of the selected week (set to end of Sunday)
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6); // 6 days after Monday is Sunday
    weekEnd.setHours(23, 59, 59, 999); // Set to end of Sunday
    
    // Set weekStart to beginning of Monday
    const weekStartCopy = new Date(weekStart);
    weekStartCopy.setHours(0, 0, 0, 0);

    // Filter all the athlete's mileage for runs in this week
    if (!athlete.mileage || !Array.isArray(athlete.mileage)) {
        console.warn("Athlete mileage is not an array:", athlete);
        return { goal: goal, daily_mileage: weeklyRuns, total: 0, remaining: goal };
    }
    
    console.log(`Processing ${athlete.mileage.length} activities for week ${weekStartCopy.toISOString().split('T')[0]} to ${weekEnd.toISOString().split('T')[0]}`);
    
    athlete.mileage.forEach(run => {
        if (!run.date) {
            console.warn("Activity missing date:", run);
            return;
        }
        // Parse the date - handle both date strings and ensure proper parsing
        let runDate;
        if (typeof run.date === 'string') {
            // If it's already a date string, parse it
            runDate = new Date(run.date + 'T00:00:00');
        } else {
            runDate = new Date(run.date);
        }
        runDate.setHours(0, 0, 0, 0);
        
        // Check if the run date is within the selected week
        if (runDate >= weekStartCopy && runDate <= weekEnd) {
            const dayName = getDayName(runDate);
            const distance = parseFloat(run.distance) || 0;
            weeklyRuns[dayName] += distance;
            total += distance;
            console.log(`Added ${distance} miles on ${dayName} (${run.date})`);
        }
    });

    const remaining = Math.max(0, goal - total);

    // Return the *exact* data structure that populateTable expects
    return {
        goal: goal,
        daily_mileage: weeklyRuns,
        total: total,
        remaining: remaining
    };
}
        
// --- RENAMED & REWRITTEN ---
// This function NO LONGER fetches. It just triggers the UI update.
function displaySelectedWeek() {
    const status = document.getElementById('status');
    const weekSelect = document.getElementById('weekSelect');
    const selectedValue = weekSelect.value;
    
    // Hide status (loading is already done)
    status.style.display = 'none';
    
    try {
        let weekStart;
        if (selectedValue === 'current') {
            weekStart = getWeekStart();
        } else {
            // Parse the date from the dropdown's value
            weekStart = new Date(selectedValue + 'T00:00:00');
        }
        
        // 1. "Translate" the raw data into a weekly summary
        const weeklyData = processDataForWeek(weekStart);
        
        // Debug: Log the weekly data
        console.log("Weekly data for week starting:", weekStart, weeklyData);
        console.log("Total mileage:", weeklyData.total);
        
        // 2. Populate the table with that summary
        populateTable(weeklyData, weekStart);
        
    } catch (error) {
        status.className = 'status error';
        status.style.display = 'block';
        status.textContent = `Error displaying week data: ${error.message}.`;
        console.error("Error in displaySelectedWeek:", error);
    }
}
        
// --- KEEP (No changes) ---
// This function is perfect as-is, since we feed it the
// exact data structure it expects.
function populateTable(data, weekStart) {
    const tableBody = document.getElementById('mileageTableBody');
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const dailyMileage = data.daily_mileage || {};
    
    let total = 0;
    
    // Update each day row
    days.forEach((day, index) => {
        const row = tableBody.rows[index];
        const date = new Date(weekStart);
        date.setDate(date.getDate() + index);
        
        row.cells[1].textContent = formatDate(date);
        
        const mileage = dailyMileage[day] || 0;
        const mileageCell = row.cells[2];
        
        if (mileage > 0) {
            mileageCell.textContent = mileage.toFixed(2);
            mileageCell.className = 'mileage-value';
            total += mileage;
        } else {
            mileageCell.textContent = '--';
            mileageCell.className = 'mileage-value empty';
        }
    });
    
    // Update total row
    const totalCell = document.getElementById('totalMileage');
    totalCell.textContent = total.toFixed(2);
    
    // Update summary cards
    const goal = data.goal || 0;
    document.getElementById('goalValue').textContent = goal.toFixed(2);
    document.getElementById('goalDisplay').textContent = goal.toFixed(2);
    document.getElementById('completedMileage').textContent = total.toFixed(2);
    
    const remaining = Math.max(0, goal - total);
    document.getElementById('remainingMileage').textContent = remaining.toFixed(2);
}

// --- NEW FUNCTION ---
// Transforms flat list of activities into grouped athlete structure
function transformActivitiesToAthletes(activities) {
    if (!activities || activities.length === 0) {
        return [];
    }
    
    // Group activities by athlete_id
    const activitiesByAthlete = {};
    activities.forEach(activity => {
        const athleteId = activity.athlete_id;
        if (!activitiesByAthlete[athleteId]) {
            activitiesByAthlete[athleteId] = [];
        }
        activitiesByAthlete[athleteId].push(activity);
    });
    
    // Create athlete objects with their activities
    const athletes = Object.keys(activitiesByAthlete).map(athleteId => {
        return {
            athlete_id: parseInt(athleteId),
            mileage: activitiesByAthlete[athleteId],
            mileage_goal: 0, // Default, will be updated if we fetch athlete info
            first_name: null,
            last_name: null
        };
    });
    
    return athletes;
}

// --- REWRITTEN ---
// This is the new main function that runs on page load.
async function initializePage() {
    const status = document.getElementById('status');
    const weekSelect = document.getElementById('weekSelect');

    // Show loading status
    status.className = 'status loading';
    status.style.display = 'block';
    status.textContent = 'Loading athlete data from /data...';

    try {
        // 1. Fetch activities from /data endpoint
        const response = await fetch('/data'); // This returns flat list of activities
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const activities = await response.json(); // Get flat list of activities
        
        // Check if we got any data
        if (!activities || activities.length === 0) {
            throw new Error("No activity data found from /data endpoint.");
        }
        
        // 2. Transform activities into athlete structure
        allAthleteData = transformActivitiesToAthletes(activities);
        
        // 3. Try to fetch athlete metadata to enrich the data
        try {
            const athletesResponse = await fetch('/athletes'); // Assuming this endpoint exists, or we'll create it
            if (athletesResponse.ok) {
                const athletesInfo = await athletesResponse.json();
                // Merge athlete info with activities
                allAthleteData = allAthleteData.map(athlete => {
                    const athleteInfo = athletesInfo.find(a => a.athlete_id === athlete.athlete_id);
                    if (athleteInfo) {
                        return {
                            ...athlete,
                            first_name: athleteInfo.first_name,
                            last_name: athleteInfo.last_name,
                            mileage_goal: athleteInfo.mileage_goal || 0,
                            long_run_goal: athleteInfo.long_run_goal || 0
                        };
                    }
                    return athlete;
                });
            }
        } catch (e) {
            // If we can't fetch athlete info, continue with defaults
            console.log("Could not fetch athlete metadata, using defaults");
        }
        
        // Check if we have any athlete data after transformation
        if (!allAthleteData || allAthleteData.length === 0) {
            throw new Error("No athlete data found after processing activities.");
        }
        
        // Debug: Log the transformed data
        console.log("Transformed athlete data:", allAthleteData);
        console.log("First athlete mileage count:", allAthleteData[0]?.mileage?.length || 0);

        // 2. Populate week dropdown (same as before)
        const currentWeekStart = getWeekStart();
        for (let i = 1; i <= 4; i++) {
            const weekDate = new Date(currentWeekStart);
            weekDate.setDate(weekDate.getDate() - (7 * i));
            const option = document.createElement('option');
            option.value = formatDateForAPI(weekDate);
            option.textContent = `Week of ${formatDate(weekDate)}`;
            weekSelect.appendChild(option);
        }
        
        // 3. Add event listener
        weekSelect.addEventListener('change', displaySelectedWeek);

        // 4. Load the data for the current week (using the data we just fetched)
        displaySelectedWeek();
        
        // Hide loading status after successful load
        status.style.display = 'none';

    } catch (error) {
        status.className = 'status error';
        status.style.display = 'block';
        status.textContent = `Error loading data: ${error.message}. Is the backend server running?`;
        console.error("Error in initializePage:", error);
    }
}

// Start everything when the page loads
window.addEventListener('DOMContentLoaded', initializePage);