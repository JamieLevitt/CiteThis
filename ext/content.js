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
      
      // Use selectors based on your HTML:
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

  // Generate a pastel color using HSL; evenly spaced hues.
  function generatePastelColor(index, total) {
    const hue = Math.floor(index * (360 / total));
    return `hsl(${hue}, 70%, 80%)`;
  }

  // Helper: extract wiki title from a wiki URL.
  function extractWikiTitle(url) {
    const parts = url.split("/wiki/");
    if (parts.length > 1) {
      return parts[1].replace(/_/g, " ");
    }
    return url;
  }

  // Create a section with a title and list of hyperlinks.
  // items is an array of objects: for "handle", each item is a string;
  // for "wiki" and "article", each item is an object {url, text}.
  function createSection(titleText, items, type) {
    const section = document.createElement("div");
    section.className = "topic-section";
    const header = document.createElement("h3");
    header.textContent = titleText;
    section.appendChild(header);
    
    const list = document.createElement("ul");
    items.forEach(item => {
      const li = document.createElement("li");
      const link = document.createElement("a");
      if (type === "handle") {
        // item is a string, e.g. "@username"
        link.textContent = item;
        link.href = "https://x.com/" + item.substring(1);
      } else if (type === "wiki") {
        // item is an object { url, text }
        link.textContent = item.text;
        link.href = item.url;
      } else if (type === "article") {
        // For articles, display a combination of source and published date if available.
        link.textContent = item.text;
        link.href = item.url;
      }
      link.target = "_blank";
      li.appendChild(link);
      list.appendChild(li);
    });
    section.appendChild(list);
    return section;
  }

  // Main logic: wait for elements, then insert our custom topic UI.
  waitForElements(({ tweetDiv, relevantBox, whatsHappeningBox }) => {
    // Create the container for our topic box.
    const topicBox = document.createElement("div");
    topicBox.className = "custom-box";
    topicBox.innerText = "Loading topics...";
    log("Inserting topic box into sidebar.");
    
    // Insert the topic box before the "What's happening" section.
    whatsHappeningBox.parentNode.insertBefore(topicBox, whatsHappeningBox);
    
    // Extract the tweet HTML (we want the innerHTML, not just text, for proper tagging).
    const tweetHTML = tweetDiv.outerHTML;
    log("Tweet HTML extracted.");
    
    // Send the tweet content to your Flask API endpoint.
    fetch('http://localhost:5000/analyse_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ post_body: tweetHTML })
    })
    .then(response => response.json())
    .then(data => {
      log("API response received.");
      // Assume the API returns an object:
      // { topics: [ { topic, entities, articles } ], tagged: "<tagged html>" }
      
      // Replace the tweet content with the tagged HTML.
      const tweetContainer = document.createElement("div");
      tweetContainer.innerHTML = data.tagged;
      tweetDiv.parentNode.replaceChild(tweetContainer, tweetDiv);
      
      // Clear the topicBox and build our UI.
      topicBox.innerHTML = "";
      
      // Build the dropdown (a row of buttons) for each topic.
      const dropdown = document.createElement("div");
      dropdown.className = "topic-dropdown";
      
      // Prepare arrays to aggregate related links.
      const handles = [];
      const wikiLinks = [];
      const articleLinks = [];
      
      const topics = data.topics;
      const topicColorMapping = {};
      topics.forEach((topicObj, index) => {
        // Generate a pastel color for this topic.
        const pastelColor = generatePastelColor(index, topics.length);
        topicColorMapping[topicObj.topic] = pastelColor;
        
        // Create a button for this topic.
        const button = document.createElement("button");
        button.className = "topic-button";
        button.style.backgroundColor = pastelColor;
        button.textContent = topicObj.topic;
        button.addEventListener("click", () => {
          // Clear previous highlights.
          tweetContainer.querySelectorAll("[data-topic]").forEach(el => {
            el.style.backgroundColor = "";
          });
          // Highlight words in the tweet tagged with this topic.
          tweetContainer.querySelectorAll(`[data-topic="${topicObj.topic}"]`).forEach(el => {
            el.style.backgroundColor = pastelColor;
          });
        });
        dropdown.appendChild(button);
        
        // Aggregate related info from entities.
        topicObj.entities.forEach(entity => {
          if (entity.twitter_url) {
            let parts = entity.twitter_url.split("/");
            let handle = "@" + parts[parts.length - 1];
            handles.push(handle);
          }
          if (entity.wiki_url) {
            wikiLinks.push({
              url: entity.wiki_url,
              text: extractWikiTitle(entity.wiki_url)
            });
          }
        });
        
        // Aggregate articles.
        topicObj.articles.forEach(article => {
          // If the article has a source and published date, combine them;
          // otherwise, default to the URL.
          let display = article.source 
                        ? `${article.source} (${article.published})`
                        : article.url;
          articleLinks.push({
            url: article.url,
            text: display
          });
        });
      });
      
      // Remove duplicate entries.
      const uniqueHandles = Array.from(new Set(handles));
      const uniqueWikiLinks = Array.from(new Map(wikiLinks.map(item => [item.url, item])).values());
      const uniqueArticleLinks = Array.from(new Map(articleLinks.map(item => [item.url, item])).values());
      
      // Create a scrollable info area.
      const infoContainer = document.createElement("div");
      infoContainer.className = "topic-info-container";
      
      const handlesSection = createSection("Relevant Handles", uniqueHandles, "handle");
      const wikiSection = createSection("Relevant Wikipedia Articles", uniqueWikiLinks, "wiki");
      const articlesSection = createSection("Relevant articles", uniqueArticleLinks, "article");
      
      infoContainer.appendChild(handlesSection);
      infoContainer.appendChild(wikiSection);
      infoContainer.appendChild(articlesSection);
      
      // Append the dropdown and info area to the topicBox.
      topicBox.appendChild(dropdown);
      topicBox.appendChild(infoContainer);
    })
    .catch(error => {
      topicBox.innerText = "Error loading topics.";
      console.error("Error:", error);
    });
  });
})();
