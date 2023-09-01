document.addEventListener('DOMContentLoaded', function() {
    window.addEventListener('load', autoCompleteLocation);
});

function autoCompleteLocation() {
    const input = document.getElementById('api-location');
    if (input) {
        const autocomplete = new google.maps.places.Autocomplete(input);
        autocomplete.addListener('place_changed', () => {
            const place = autocomplete.getPlace();
            if (place.geometry) {
                document.getElementById('location-lat').value = place.geometry.location.lat();
                document.getElementById('location-lng').value = place.geometry.location.lng();
            }
        })
    }
    
}