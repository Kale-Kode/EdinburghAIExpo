// Function to fast-forward to a specific timestamp
const goToTimestamp = (seconds) => {
    const youtubePlayer = document.querySelector('video');
    if (youtubePlayer) {
      youtubePlayer.currentTime = seconds;
      console.log(`Fast-forwarding to ${seconds} seconds`);
    }
  };
  
  // Listen for messages from the extension popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'goToTimestamp') {
      goToTimestamp(message.seconds);
    }
  });