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

document.addEventListener('DOMContentLoaded', function() {
    const makeFilter = document.getElementById('make-filter');
    const modelFilter = document.getElementById('model-filter');
    const yomFilter = document.getElementById('yom-filter');
    const transmissionFilter = document.getElementById('transmission-filter');
    const vehicleCards = document.querySelectorAll('.vehicle-card');
    const noResultsMessage = document.getElementById('no-results');

    function filterVehicles() {
        const makeValue = makeFilter.value.toLowerCase();
        const modelValue = modelFilter.value.toLowerCase();
        const yomValue = yomFilter.value.toLowerCase();
        const transmissionValue = transmissionFilter.value.toLowerCase();

        let visibleCards = 0;

        vehicleCards.forEach(card => {
            const make = card.dataset.make.toLowerCase();
            const model = card.dataset.model.toLowerCase();
            const yom = card.dataset.yom.toLowerCase();
            const transmission = card.dataset.transmission.toLowerCase();

            const matchMake = !makeValue || make === makeValue;
            const matchModel = !modelValue || model === modelValue;
            const matchYOM = !yomValue || yom === yomValue;
            const matchTransmission = !transmissionValue || transmission === transmissionValue;

            if (matchMake && matchModel && matchYOM && matchTransmission) {
                card.style.display = 'block';
                visibleCards++;
            } else {
                card.style.display = 'none';
            }
        });

        noResultsMessage.classList.toggle('hidden', visibleCards > 0);
    }

    makeFilter.addEventListener('change', filterVehicles);
    modelFilter.addEventListener('change', filterVehicles);
    yomFilter.addEventListener('change', filterVehicles);
    transmissionFilter.addEventListener('change', filterVehicles);
});

 // JavaScript to toggle mobile menu visibility
 const menuToggleButton = document.getElementById('menu-toggle');
 const mobileMenu = document.getElementById('mobile-menu');

 menuToggleButton.addEventListener('click', () => {
   mobileMenu.classList.toggle('hidden');
 });
 let currentImageIndex = 0;
 const images = [
     "https://pictures.porsche.com/rtt/iris?COSY-EU-100-1711coMvsi60AAt5FwcmBEgA4qP8iBUDxPE3Cb9pNXkBuNYdMGF4tl3U0%25z8rMHIspMBvMZq6G5OtgSv31nBJaA4qh4NSEGewirQ91wRmWBi2Ch7gVdcQT3UlhDfluNspAnPpw2iZJyNZcsctBvoT%25Ff8dXFyg%25PED6uvqMN9nReRv%25o4y7z9V6F%25vUqJbspAnPT05iZJyNKA9ctBvoqwUf8dXFOcvPED6u%25bSN9jZsVu57Zx5%259BkWwDLFRfH438nhVEeZJ",
     "https://media.ed.edmunds-media.com/land-rover/defender/2025/oem/2025_land-rover_defender_2dr-suv_90-p300-s_fq_oem_1_1600.jpg"
 ];
 
 // Function to update the main image
 function updateMainImage() {
    const mainImage = document.getElementById('main-image');
    mainImage.classList.add('hidden'); // Fade out
    setTimeout(() => {
        mainImage.src = images[currentImageIndex];
        mainImage.classList.remove('hidden'); // Fade in
    }, 500); // Match the transition duration
}
 // Show next image
 function nextImage() {
     currentImageIndex = (currentImageIndex + 1) % images.length; // Cycle to next image
     updateMainImage();
 }
 
 // Show previous image
 function prevImage() {
     currentImageIndex = (currentImageIndex - 1 + images.length) % images.length; // Cycle to previous image
     updateMainImage();
 }
 
 // Open modal (optional, if you still want the modal functionality)
 function openModal(imageSrc) {
     const modal = document.getElementById('image-modal');
     const modalImage = document.getElementById('modal-image');
     modalImage.src = imageSrc;
     modal.classList.remove('hidden');
     currentImageIndex = images.indexOf(imageSrc); // Update current index
 }
 
 // Close modal (optional, if you still want the modal functionality)
 function closeModal() {
     const modal = document.getElementById('image-modal');
     modal.classList.add('hidden');
 }