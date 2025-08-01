// LocalStorage key
const STORAGE_KEY = 'ecrin_sleep_records';

// Uygulama state
let records = [];

// DOM elementleri
const form = document.getElementById('sleepForm');
const wakeupHourInput = document.getElementById('wakeupHour');
const wakeupMinuteInput = document.getElementById('wakeupMinute');
const recordsList = document.getElementById('recordsList');
const warningMessage = document.getElementById('warningMessage');
const timeDiffText = document.getElementById('timeDiffText');

// Sayfa yüklendiğinde kayıtları yükle
document.addEventListener('DOMContentLoaded', () => {
    // Check if it's a new day
    checkAndResetForNewDay();
    
    loadRecords();
    displayRecords();
    updateTimeDifference(); // Initialize time difference
    setInterval(updateTimeDifference, 1000); // Update every second
});

// Check if it's a new day and reset records
function checkAndResetForNewDay() {
    const today = new Date().toDateString();
    const lastReset = localStorage.getItem('ecrin_last_reset');
    
    if (lastReset !== today) {
        // New day - clear all records
        records = [];
        saveRecords();
        localStorage.setItem('ecrin_last_reset', today);
    }
}

// Form submit
form.addEventListener('submit', (e) => {
    e.preventDefault();
    saveRecord();
});

// Kayıt yükleme
function loadRecords() {
    const stored = localStorage.getItem(STORAGE_KEY);
    records = stored ? JSON.parse(stored) : [];
}

// Kayıt kaydetme
function saveRecords() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

// Şu anki saati input'lara yazdırma
function setCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    
    document.getElementById('wakeupHour').value = hours;
    document.getElementById('wakeupMinute').value = minutes;
}

// Save wake-up record
function saveRecord() {
    const now = new Date();
    let hour = parseInt(document.getElementById('wakeupHour').value);
    let minute = parseInt(document.getElementById('wakeupMinute').value);
    
    if (isNaN(hour) || isNaN(minute)) {
        // If no time is entered, do nothing.
        // This prevents an alert when the button is clicked with empty inputs.
        return;
    }

    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
        // Invalid time range, do nothing silently.
        return;
    }
    
    const newRecord = {
        id: Date.now(),
        hour: hour,
        minute: minute,
        timestamp: new Date().toISOString()
    };
    
    records.unshift(newRecord);
    saveRecords();
    
    // Clear form
    document.getElementById('wakeupHour').value = '';
    document.getElementById('wakeupMinute').value = '';
    
    displayRecords();
    updateTimeDifference();
}

// Display wake-up records
function displayRecords() {
    if (records.length === 0) {
        recordsList.innerHTML = '<p class="text-gray-500 text-center py-8">Henüz kayıt bulunmuyor</p>';
        return;
    }
    
    recordsList.innerHTML = '';
    
    records.forEach((record, index) => {
        const card = document.createElement('div');
        card.className = 'bg-gray-50 rounded-lg p-4 mb-4';
        
        card.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <p class="text-indigo-600">Uyanma: <span class="font-bold">${record.hour.toString().padStart(2, '0')}:${record.minute.toString().padStart(2, '0')}</span></p>
                    <p class="text-xs text-gray-500">${new Date(record.timestamp).toLocaleString('tr-TR')}</p>
                </div>
                <button onclick="deleteRecord(${record.id})" 
                        class="bg-red-500 hover:bg-red-600 text-white p-2 rounded">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        recordsList.appendChild(card);
    });
}

// Kayıt silme
function deleteRecord(id) {
    if (confirm('Bu kaydı silmek istediğinizden emin misiniz?')) {
        records = records.filter(record => record.id !== id);
        saveRecords();
        displayRecords();
        updateTimeDifference();
    }
}

// Update time difference since last wake-up
function updateTimeDifference() {
    if (records.length === 0) {
        timeDiffText.textContent = '--';
        warningMessage.classList.add('hidden');
        return;
    }
    
    const latestRecord = records[0];
    
    // Create a date object for the wake-up time (today's date + recorded time)
    const wakeUp = new Date();
    wakeUp.setHours(latestRecord.hour, latestRecord.minute, 0, 0);
    
    const now = new Date();
    const diffMs = now - wakeUp;
    
    if (diffMs > 0) {
        const totalMinutes = Math.floor(diffMs / (1000 * 60));
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        timeDiffText.textContent = `${hours} saat ${minutes} dakika oldu`;
        
        // Show warning if 3+ hours passed
        if (hours >= 3) {
            warningMessage.classList.remove('hidden');
        } else {
            warningMessage.classList.add('hidden');
        }
    } else {
        // If wake-up time is in the future (shouldn't happen normally)
        timeDiffText.textContent = 'Henüz uyanmamışsın';
        warningMessage.classList.add('hidden');
    }
}