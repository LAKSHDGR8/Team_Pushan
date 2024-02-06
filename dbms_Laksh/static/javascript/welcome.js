document.addEventListener('DOMContentLoaded', function () {
    var signIn = document.getElementById('sign-in');
    var attempts = 0; // Counter for the number of attempts to hover
    var maxDistance = 1000; // Maximum distance the button can move from its original position

    // Store the original position of the sign-in
    var originalX = signIn.offsetLeft;
    var originalY = signIn.offsetTop;

    signIn.addEventListener('mouseenter', function (event) {
        if (attempts < 4) { // Allow it to move 3 times before staying put
            // Calculate a random delta within maxDistance pixels
            var deltaX = Math.random() * maxDistance - (maxDistance / 2);
            var deltaY = Math.random() * maxDistance - (maxDistance / 2);

            // Calculate new position based on the original position and random delta
            var newX = originalX + deltaX;
            var newY = originalY + deltaY;

            // Ensure the new position is within the viewport
            newX = Math.max(0, Math.min(newX, window.innerWidth - signIn.offsetWidth));
            newY = Math.max(0, Math.min(newY, window.innerHeight - signIn.offsetHeight));

            // Update the 'Sign In' position
            signIn.style.position = 'absolute'; // Use 'absolute' for positioning within its container
            signIn.style.left = newX + 'px';
            signIn.style.top = newY + 'px';
            
            attempts++; // Increment the attempt counter
        }
    });

    signIn.addEventListener('click', function () {
        if (attempts >= 3) {
            // Perform the sign-in action
            alert('Got me! Now you can sign in.');
            // Redirect the user or perform other actions here
        }
    });
});
