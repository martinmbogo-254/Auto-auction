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