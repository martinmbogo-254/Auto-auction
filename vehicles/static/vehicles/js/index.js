function countdownTimer(endDate) {
    const countDownDate = new Date(endDate).getTime();

    // Update the count down every 1 second
    const interval = setInterval(function() {
        const now = new Date().getTime();
        const distance = countDownDate - now;

        // Time calculations for days, hours, minutes and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the result in the element with id="countdown"
        document.getElementById("countdown").innerHTML = 
            days + "d " + hours + "h " + minutes + "m " + seconds + "s ";

        // If the count down is over, write some text 
        if (distance < 0) {
            clearInterval(interval);
            document.getElementById("countdown").innerHTML = "Auction Has Ended";
            document.getElementById("bidbtn").style.display = 'none';

        }
    }, 1000);
}

// Initialize the countdown timer
countdownTimer(auctionEndDate);


document.addEventListener("DOMContentLoaded", function() {
    const spinner = document.getElementById('spinner');
    spinner.classList.remove('d-none');  // Show spinner

    window.addEventListener("load", function() {
        spinner.classList.add('d-none');  // Hide spinner when page fully loads
    });
});
   // Toggle mobile menu
   document.getElementById('menu-toggle').addEventListener('click', function () {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');

    mobileMenu.classList.toggle('hidden');
    if (mobileMenu.classList.contains('hidden')) {
        menuIcon.classList.remove('fa-times');
        menuIcon.classList.add('fa-bars');
    } else {
        menuIcon.classList.remove('fa-bars');
        menuIcon.classList.add('fa-times');
    }
});

// Show/hide the message modal
document.addEventListener("DOMContentLoaded", function () {
    const messageModal = document.getElementById('messageModal');
    const closeModal = document.getElementById('closeModal');

    {% if messages %}
        messageModal.classList.remove('hidden');
    {% endif %}

    closeModal.addEventListener('click', function () {
        messageModal.classList.add('hidden');
    });
});

// Show/hide the loading spinner
document.addEventListener("DOMContentLoaded", function () {
    const loader = document.getElementById('loader');

    // Show spinner on page load
    loader.classList.remove('hidden');

    // Hide spinner when page fully loads
    window.addEventListener('load', function () {
        loader.classList.add('hidden');
    });
});

    // Function to show the spinner and update button text
        function showSpinner() {
        const spinner = document.getElementById('spinner');
        const buttonText = document.getElementById('buttonText');
        
        spinner.classList.remove('hidden'); // Show the spinner
        buttonText.textContent = 'Loading...'; // Change button text
        }

        // Function to hide the spinner and reset button text
        function hideSpinner() {
        const spinner = document.getElementById('spinner');
        const buttonText = document.getElementById('buttonText');
        
        spinner.classList.add('hidden'); // Hide the spinner
        buttonText.textContent = 'Submit Bid'; // Reset button text
        }

        // Example: Simulate loading when the button is clicked
        document.getElementById('submitButton').addEventListener('click', function() {
        showSpinner(); // Show spinner when loading starts

        // Simulate a loading process (e.g., an API call)
        setTimeout(() => {
            hideSpinner(); // Hide spinner when loading is done
        }, 3000); // Replace this with your actual loading logic
        });
        let currentImageIndex = 0;
        const images = [
            {% for image in vehicle.vehicleimage_set.all %}
            "{{ image.image.url }}",
            {% endfor %}
        ];

        // Function to update the main image
        function updateMainImage() {
            const mainImage = document.getElementById('main-image');
            mainImage.src = images[currentImageIndex];
        }

        // Show next image
        function nextImage() {
            currentImageIndex = (currentImageIndex + 1) % images.length;
            updateMainImage();
        }

        // Show previous image
        function prevImage() {
            currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
            updateMainImage();
        }

        // Show specific image from thumbnail
        function showImage(index) {
            currentImageIndex = index;
            updateMainImage();
        }

        // Modal functionality
        function openModal(imageSrc) {
            const modal = document.getElementById('image-modal');
            const modalImage = document.getElementById('modal-image');
            modalImage.src = imageSrc;
            modal.classList.remove('hidden');
        }

        function closeModal() {
            const modal = document.getElementById('image-modal');
            modal.classList.add('hidden');
        }
                // Function to format number with commas
       