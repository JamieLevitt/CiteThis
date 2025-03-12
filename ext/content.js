function remove() {
  const selectors = [
      '[aria-label="Relevant people"]',
      '[aria-label="What’s happening"]'
  ];
  selectors.forEach(selector => {
      const elem = document.querySelector(selector);
      if (elem) {
          elem.remove();
      }
  });
}

 // Create a custom box to insert into the sidebar.
 const customBox = document.createElement("div");
 customBox.id = "custom-topic-box";
 customBox.style.border = "1px solid #ccc";
 customBox.style.padding = "10px";
 customBox.style.margin = "10px";
 customBox.style.backgroundColor = "#f9f9f9";

 // Create a dropdown container for topic buttons.
 const dropdownContainer = document.createElement("div");
 dropdownContainer.id = "topic-dropdown";
 dropdownContainer.style.marginBottom = "10px";
 customBox.appendChild(dropdownContainer);

 // Create and add a loading message.
 const loadingMessage = document.createElement("div");
 loadingMessage.id = "loading-message";
 loadingMessage.innerText = "Extension is loading...";
 customBox.appendChild(loadingMessage);

 // Insert the custom box into Twitter’s sidebar.
 const sidebar = document.querySelector('aside[role="complementary"]');
 if (sidebar) {
   sidebar.prepend(customBox);
 }

 fetch("https://api.example.com/tag_twitter_post?postId=123")
    .then(response => response.json())
    .then(data => {
      // Remove the loading message.
      loadingMessage.remove();

      // data is expected to be in the form:
      // { "taggedContent": "<div>...</div>", "topics": { "politics": [...], "sports": [...] } }
      // Create a button for each topic from the JSON response.
      if (data.topics) {
        Object.keys(data.topics).forEach(topic => {
          const btn = document.createElement("button");
          btn.innerText = topic;
          btn.style.marginRight = "5px";
          btn.style.backgroundColor = getPastelColor(topic);
          btn.style.border = "none";
          btn.style.padding = "5px 10px";
          btn.style.cursor = "pointer";

          // Toggle highlighting for all tagged words of this topic.
          btn.addEventListener("click", () => {
            const taggedEls = document.querySelectorAll(`span.topic-tag[data-topic="${topic}"]`);
            taggedEls.forEach(el => {
              // Toggle highlight: if background color is set, remove it; otherwise, set it.
              if (el.style.backgroundColor) {
                el.style.backgroundColor = "";
              } else {
                el.style.backgroundColor = getPastelColor(topic);
              }
            });
          });
          dropdownContainer.appendChild(btn);
        });
      }

      // Insert the tagged post content returned from the Python function.
      const contentDiv = document.createElement("div");
      // Expecting the Python service to return the tagged HTML under the key "taggedContent"
      contentDiv.innerHTML = data.taggedContent || "";
      customBox.appendChild(contentDiv);
    })
    .catch(err => {
      console.error("Error fetching tagged content:", err);
      loadingMessage.innerText = "Failed to load content.";
    });
});

// A simple deterministic pastel colour generator based on a seed string.
function getPastelColor(seed) {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 70%, 80%)`;
}