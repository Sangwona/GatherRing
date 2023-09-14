document.addEventListener('DOMContentLoaded', function() {
    window.addEventListener('load', autoCompleteLocation);
    window.addEventListener('load', autoCompleteLocationCityPostalCode);
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

function autoCompleteLocationCityPostalCode() {
    const input = document.getElementById('location');
    if (input) {
        const options = {
            types: ['postal_code', 'locality', 'administrative_area_level_3']
          };
        const autocomplete = new google.maps.places.Autocomplete(input, options);
        autocomplete.addListener('place_changed', () => {
            const place = autocomplete.getPlace();
            if (place.geometry) {
                document.getElementById('location-lat').value = place.geometry.location.lat();
                document.getElementById('location-lng').value = place.geometry.location.lng();
            }
        })
    }
    
}