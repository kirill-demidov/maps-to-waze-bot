// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Expand the WebApp to full height
    tg.expand();
    
    // Enable closing confirmation
    tg.enableClosingConfirmation();
    
    // Apply Telegram theme
    applyTelegramTheme();
    
    // Initialize event listeners
    initializeEventListeners();
});

function applyTelegramTheme() {
    if (tg.themeParams) {
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
        document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
    }
}

function initializeEventListeners() {
    const form = document.getElementById('converterForm');
    const locationBtn = document.getElementById('locationBtn');
    const openWazeBtn = document.getElementById('openWazeBtn');
    const shareBtn = document.getElementById('shareBtn');
    
    form.addEventListener('submit', handleFormSubmit);
    locationBtn.addEventListener('click', handleLocationRequest);
    openWazeBtn.addEventListener('click', handleOpenWaze);
    shareBtn.addEventListener('click', handleShare);
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const input = document.getElementById('input').value.trim();
    const convertBtn = document.getElementById('convertBtn');
    
    if (!input) {
        showError('Please enter a Google Maps link or coordinates');
        return;
    }
    
    convertBtn.disabled = true;
    convertBtn.textContent = 'Converting...';
    
    try {
        const coordinates = extractCoordinates(input);
        
        if (!coordinates) {
            throw new Error('Could not extract valid coordinates from input');
        }
        
        const wazeUrl = generateWazeLink(coordinates.lat, coordinates.lng);
        showResult(coordinates, wazeUrl);
        
        // Notify Telegram that conversion is complete
        tg.HapticFeedback.notificationOccurred('success');
        
    } catch (error) {
        showError(error.message);
        tg.HapticFeedback.notificationOccurred('error');
    } finally {
        convertBtn.disabled = false;
        convertBtn.textContent = 'Convert to Waze';
    }
}

function handleLocationRequest() {
    const locationBtn = document.getElementById('locationBtn');
    
    if (navigator.geolocation) {
        locationBtn.disabled = true;
        locationBtn.textContent = 'Getting location...';
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                document.getElementById('input').value = `${lat}, ${lng}`;
                
                locationBtn.disabled = false;
                locationBtn.textContent = '📍 Use My Location';
                
                tg.HapticFeedback.impactOccurred('light');
            },
            function(error) {
                showError('Could not get your location: ' + error.message);
                locationBtn.disabled = false;
                locationBtn.textContent = '📍 Use My Location';
                tg.HapticFeedback.notificationOccurred('error');
            }
        );
    } else {
        showError('Geolocation is not supported by this browser');
    }
}

function handleOpenWaze() {
    const wazeUrl = document.getElementById('openWazeBtn').dataset.wazeUrl;
    if (wazeUrl) {
        tg.openLink(wazeUrl);
    }
}

function handleShare() {
    const wazeUrl = document.getElementById('shareBtn').dataset.wazeUrl;
    const coordinates = document.getElementById('coordinates').textContent;
    
    if (wazeUrl) {
        const shareText = `📍 Location: ${coordinates}\\n🚗 Open in Waze: ${wazeUrl}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Waze Navigation Link',
                text: shareText,
                url: wazeUrl
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareText).then(() => {
                tg.showAlert('Link copied to clipboard!');
            });
        }
    }
}

function extractCoordinates(text) {
    // Try to extract from Google Maps URL
    const urlCoords = extractCoordinatesFromGoogleMaps(text);
    if (urlCoords) return urlCoords;
    
    // Try to extract DMS coordinates
    const dmsCoords = parseDMSCoordinates(text);
    if (dmsCoords) return dmsCoords;
    
    // Try to extract decimal coordinates
    const decimalCoords = parseDecimalCoordinates(text);
    if (decimalCoords) return decimalCoords;
    
    return null;
}

function extractCoordinatesFromGoogleMaps(url) {
    try {
        // Pattern for @lat,lng format
        const coordsPattern = /@(-?\\d+\\.?\\d*),(-?\\d+\\.?\\d*)/;
        const match = url.match(coordsPattern);
        
        if (match) {
            const lat = parseFloat(match[1]);
            const lng = parseFloat(match[2]);
            return { lat, lng };
        }
        
        // Pattern for ll parameter
        const urlObj = new URL(url);
        const ll = urlObj.searchParams.get('ll');
        if (ll) {
            const coords = ll.split(',');
            if (coords.length === 2) {
                const lat = parseFloat(coords[0]);
                const lng = parseFloat(coords[1]);
                if (!isNaN(lat) && !isNaN(lng)) {
                    return { lat, lng };
                }
            }
        }
        
        // Pattern for q parameter with coordinates
        const q = urlObj.searchParams.get('q');
        if (q) {
            const coordsMatch = q.match(/(-?\\d+\\.?\\d*),(-?\\d+\\.?\\d*)/);
            if (coordsMatch) {
                const lat = parseFloat(coordsMatch[1]);
                const lng = parseFloat(coordsMatch[2]);
                return { lat, lng };
            }
        }
        
        return null;
    } catch (error) {
        return null;
    }
}

function parseDMSCoordinates(text) {
    // Pattern for DMS format: degrees°minutes'seconds"direction
    const dmsPattern = /(\\d+)°(\\d+)'([\\d.]+)"([NSEW])\\s*(\\d+)°(\\d+)'([\\d.]+)"([NSEW])/;
    const match = text.match(dmsPattern);
    
    if (match) {
        try {
            // First coordinate (latitude)
            const latDeg = parseInt(match[1]);
            const latMin = parseInt(match[2]);
            const latSec = parseFloat(match[3]);
            const latDir = match[4];
            
            // Second coordinate (longitude)
            const lngDeg = parseInt(match[5]);
            const lngMin = parseInt(match[6]);
            const lngSec = parseFloat(match[7]);
            const lngDir = match[8];
            
            // Convert to decimal
            const lat = dmsToDecimal(latDeg, latMin, latSec, latDir);
            const lng = dmsToDecimal(lngDeg, lngMin, lngSec, lngDir);
            
            return { lat, lng };
        } catch (error) {
            return null;
        }
    }
    
    return null;
}

function parseDecimalCoordinates(text) {
    const coordPattern = /(-?\\d+\\.?\\d*),\\s*(-?\\d+\\.?\\d*)/;
    const match = text.match(coordPattern);
    
    if (match) {
        try {
            const lat = parseFloat(match[1]);
            const lng = parseFloat(match[2]);
            
            // Validate coordinate ranges
            if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
                return { lat, lng };
            }
        } catch (error) {
            return null;
        }
    }
    
    return null;
}

function dmsToDecimal(degrees, minutes, seconds, direction) {
    let decimal = degrees + minutes/60 + seconds/3600;
    if (direction === 'S' || direction === 'W') {
        decimal = -decimal;
    }
    return decimal;
}

function generateWazeLink(lat, lng) {
    return `https://waze.com/ul?ll=${lat},${lng}&navigate=yes`;
}

function showResult(coordinates, wazeUrl) {
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const coordinatesSpan = document.getElementById('coordinates');
    const openWazeBtn = document.getElementById('openWazeBtn');
    const shareBtn = document.getElementById('shareBtn');
    
    coordinatesSpan.textContent = `${coordinates.lat.toFixed(6)}, ${coordinates.lng.toFixed(6)}`;
    openWazeBtn.dataset.wazeUrl = wazeUrl;
    shareBtn.dataset.wazeUrl = wazeUrl;
    
    errorDiv.classList.remove('show');
    resultDiv.classList.add('show');
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    
    resultDiv.classList.remove('show');
    errorDiv.classList.add('show');
    
    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}