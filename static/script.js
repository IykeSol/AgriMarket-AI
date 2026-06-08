// Tab Switching Logic
document.querySelectorAll('.nav-item').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all
        document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(`${tabId}-tab`).classList.add('active');
    });
});

// Dynamic Units based on Commodity
const unitsMap = {
    'Rice': ['50kg Bag', '25kg Bag'],
    'Groundnut Oil': ['25 Litres', '5 Litres'],
    'Tomato': ['Big Basket', 'Small Basket'],
    'Maize': ['50kg Bag'],
    'Yam': ['100 Tubers', 'Single Tuber']
};

const itemSelect = document.getElementById('item');
const unitSelect = document.getElementById('unit');

itemSelect.addEventListener('change', () => {
    const selectedItem = itemSelect.value;
    const validUnits = unitsMap[selectedItem];
    
    unitSelect.innerHTML = ''; // Clear current options
    
    validUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit;
        option.textContent = unit;
        unitSelect.appendChild(option);
    });
});

// Form Submission
document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('form-submit-btn');
    const resultPanel = document.getElementById('form-result');
    const priceVal = document.getElementById('form-price-val');
    const metaVal = document.getElementById('form-weather-meta');
    const summaryVal = document.getElementById('form-analysis-summary');
    
    submitBtn.textContent = 'Running Model...';
    submitBtn.disabled = true;
    summaryVal.classList.add('hidden');
    
    const data = {
        Item: itemSelect.value,
        Unit: unitSelect.value,
        Location: document.getElementById('location').value,
        Year: parseInt(document.getElementById('year').value),
        Month: parseInt(document.getElementById('month').value),
        USD_NGN_Rate: parseFloat(document.getElementById('usd_rate').value),
        Fuel_Price_NGN: parseFloat(document.getElementById('fuel').value),
        Fertilizer_Price_NGN: parseFloat(document.getElementById('fertilizer').value),
        Market_Demand: document.getElementById('demand').value
    };

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.detail || 'Prediction failed. Ensure model is trained.');
        }
        
        const json = await res.json();
        
        priceVal.textContent = json.predicted_price_ngn.toLocaleString(undefined, {minimumFractionDigits: 2});
        metaVal.textContent = `Based on: Temp ${json.temperature_c}°C, Rain ${json.rainfall_mm}mm. ${json.weather_source}`;
        
        if (json.analysis_summary) {
            summaryVal.innerHTML = json.analysis_summary.replace(/\n/g, '<br>');
            summaryVal.classList.remove('hidden');
        }
        
        resultPanel.classList.remove('hidden');
        
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        submitBtn.textContent = 'Run Model';
        submitBtn.disabled = false;
    }
});

// Chat Logic
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const chatSubmitBtn = document.getElementById('chat-submit-btn');

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    bubble.innerHTML = text; // allow basic html
    
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;
    
    // Add user msg
    appendMessage(query, 'user');
    chatInput.value = '';
    
    // Loading state
    chatInput.disabled = true;
    chatSubmitBtn.disabled = true;
    
    // Create loading bubble
    const loadingId = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'system');
    msgDiv.id = loadingId;
    msgDiv.innerHTML = `<div class="message-bubble"><em>Analyzing market intelligence...</em></div>`;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const json = await res.json();
        
        // Remove loading
        document.getElementById(loadingId).remove();
        
        if (json.response) {
            appendMessage(json.response.replace(/\n/g, '<br>'), 'system');
        } else {
            appendMessage("I couldn't process that request.", 'system');
        }
        
    } catch (err) {
        document.getElementById(loadingId).remove();
        appendMessage("An error occurred connecting to the backend API.", 'system');
    } finally {
        chatInput.disabled = false;
        chatSubmitBtn.disabled = false;
        chatInput.focus();
    }
});
