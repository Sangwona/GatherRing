document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelector('input[type="file"]').addEventListener('change', function() {
        if (this.files && this.files[0]) {
            if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i)) {
                alert('This type is not supported. Use these jpg, ,jpeg, png, gif');
                this.value = '';
            }
            else {
                const img = document.querySelector('.preview');
                img.onload = () => {
                    URL.revokeObjectURL(img.src);  // no longer needed, free memory
                }
                img.src = URL.createObjectURL(this.files[0]); // set src to blob url
            }
        }
    });
});
