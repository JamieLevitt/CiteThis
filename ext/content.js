(function() {
  // Debug logging helper
  function log(msg) {
    console.log("[TopicTagger]", msg);
  }

  // Wait for tweet and sidebar elements to load using a MutationObserver.
  function waitForElements(callback, timeout = 15000) {
    const startTime = Date.now();
    const observer = new MutationObserver(() => {
      const tweetDiv = document.querySelector('div[data-testid="tweetText"]');
      const sidebar = document.querySelector('div[data-testid="sidebarColumn"]');
      
      if (!tweetDiv) {
        log("Tweet text not found yet.");
      } else {
        log("Tweet text found.");
      }
      
      if (!sidebar) {
        log("Sidebar container not found yet.");
      }
      
      // Use the precise selectors from your HTML
      let relevantBox = sidebar ? sidebar.querySelector('aside[aria-label="Relevant people"]') : null;
      let whatsHappeningBox = sidebar ? sidebar.querySelector('section[aria-labelledby="accessible-list-1"]') : null;
      
      if (!relevantBox) {
        log("Relevant people box not found yet.");
      } else {
        log("Relevant people box found.");
      }
      
      if (!whatsHappeningBox) {
        log("What's happening section not found yet.");
      } else {
        log("What's happening section found.");
      }
      
      if (tweetDiv && sidebar && relevantBox && whatsHappeningBox) {
        observer.disconnect();
        callback({ tweetDiv, relevantBox, whatsHappeningBox });
      } else if (Date.now() - startTime > timeout) {
        observer.disconnect();
        log("Timeout reached; required elements not found.");
      }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Main logic: insert the topic box and fetch topics from the API.
  waitForElements(({ tweetDiv, relevantBox, whatsHappeningBox }) => {
    // Create a new box with the custom CSS class.
    const topicBox = document.createElement("div");
    topicBox.className = "custom-box";
    topicBox.innerText = "Loading topics...";
    log("Inserting topic box between Relevant people and What's happening.");

    // Insert the topic box before the "What's happening" section.
    whatsHappeningBox.parentNode.insertBefore(topicBox, whatsHappeningBox);

    // Extract the tweet text.
    const postBody = tweetDiv.innerText;
    log("Post body extracted: " + postBody.substring(0, 50) + "...");

    // Send the tweet content to your Flask API endpoint.
    fetch('http://127.0.0.1:5000/analyse_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ post_body: postBody })
    })
    .then(response => response.json())
    .then(data => {
      log("API response received.");
      log(data);
      if (data.topics && Array.isArray(data.topics) && data.topics.length > 0) {
        // Create an unordered list of topics.
        const ul = document.createElement("ul");
        data.topics.forEach(topicObj => {
          const li = document.createElement("li");
          li.textContent = topicObj.topic;
          ul.appendChild(li);
        });
        topicBox.innerHTML = "";
        topicBox.appendChild(ul);
      } else {
        topicBox.innerText = "No topics found.";
      }
    })
    .catch(error => {
      log("Error fetching topics: " + error);
      topicBox.innerText = "Error loading topics.";
    });
  });
})();
