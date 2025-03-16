/*chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "processPost") {
      fetch("http://127.0.0.1:5000/analyse_post", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ post_body: message.postText })
      })
      .then(response => response.json())
      .then(data => sendResponse(data))
      .catch(error => console.error("Error fetching API:", error));

      return true; // Keep message channel open for async response
  }
});
*/