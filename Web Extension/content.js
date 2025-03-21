(function() {
  // Store the current URL
  let currentUrl = location.href;

  // --- Monkey-patch history methods to dispatch a 'locationchange' event ---
  // This function patches history methods (pushState and replaceState) so that a custom event 'locationchange' is dispatched whenever these methods are called.
  const patchHistoryMethods = () => {
    // Helper function that wraps a given history method
    const wrapHistory = (type) => {
      // Save the original method (pushState or replaceState)
      const original = history[type];
      // Return a wrapped version that calls the original and then dispatches 'locationchange'
      return function() {
        const result = original.apply(this, arguments);
        window.dispatchEvent(new Event('locationchange'));
        return result;
      };
    };
    // Replace history.pushState and history.replaceState with wrapped versions
    history.pushState = wrapHistory('pushState');
    history.replaceState = wrapHistory('replaceState');
    // Listen for popstate events (triggered by browser navigation actions) and dispatch 'locationchange'
    window.addEventListener('popstate', () => {
      window.dispatchEvent(new Event('locationchange'));
    });
  };
  // Call the function to patch history methods
  patchHistoryMethods();

  // Logging helper function that prefixes logs with "[CiteThis]"
  const log = (msg) => {
    console.log("[CiteThis]", msg);
  };

  // Function to escape special characters in a string for use in a RegExp
  const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // Function to generate a pastel hue value based on an index among total items
  const generatePastelHue = (index, total) => (360 * (index / total));

  // Function to build a clickable link button for a given item
  const buildLinkButton = (item) => {
    // Create a button element
    const btn = document.createElement("button");
    // Assign a CSS class for styling
    btn.className = "citethis-link-button";
    // Set the button text from the item
    btn.textContent = item.text;
    // Add an event listener to open the link in a new tab when clicked
    btn.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevents the click event from triggering other click handlers (e.g., collapsing a topic)
      // Open the URL in a new window/tab; prepend "https://" if not already present
      window.open(item.url.startsWith("http") ? item.url : ("https://" + item.url), "_blank");
    });
    return btn;
  };

  // Function to build a section/area for a category of items (e.g., accounts, articles)
  // 'containerClass' is used to style the container (for example: "items-container scrollable accounts")
  const buildArea = (titleText, items, containerClass) => {
    // Create the main section div
    const section = document.createElement("div");
    section.className = "detail-section";

    // Create a header element with the provided title text
    const header = document.createElement("h4");
    header.textContent = titleText;
    section.appendChild(header);

    // Create a container div to hold the link buttons
    const container = document.createElement("div");
    container.className = containerClass;
    // Keep track of items already added to avoid duplicates
    const builtLabels = [];
    items.forEach(item => {
      // Check if this label has already been added
      if (!builtLabels.includes(item.text)) {
        container.appendChild(buildLinkButton(item));
        builtLabels.push(item.text);
      }
    });
    section.appendChild(container);
    return section;
  };

  // Function to build an expandable details area using API data (topics, entities, articles)
  const buildExpandableArea = (topicObj) => {
    // Create a container for topic details
    const details = document.createElement("div");
    details.className = "topic-details";

    // Initialize arrays to hold different types of items
    const accounts = [];
    const wikiArticles = [];
    const newsArticles = [];

    // Process entity data if available
    if (topicObj.entities && topicObj.entities.length > 0) {
      topicObj.entities.forEach(entity => {
        // If a Twitter URL exists, extract the username and add to accounts list
        if (entity.twitter_url && entity.twitter_url.trim() !== "") {
          const parts = entity.twitter_url.split("/").filter(p => p);
          if (parts.length > 0 && parts[parts.length - 1] !== "null") {
            accounts.push({
              text: "@" + parts[parts.length - 1],
              url: "https://x.com/" + parts[parts.length - 1]
            });
          }
        }
        // If a Wikipedia URL exists, format the title and add to wikiArticles list
        if (entity.wiki_url && entity.wiki_url.trim() !== "") {
          const title = entity.wiki_url.split("/wiki/")[1]?.replace(/_/g, " ") || entity.wiki_url;
          wikiArticles.push({
            text: title,
            url: entity.wiki_url
          });
        }
      });
    }

    // Process article data if available
    if (topicObj.articles && topicObj.articles.length > 0) {
      topicObj.articles.forEach(article => {
        if (article.url && article.url.trim() !== "") {
          const articleData = {
            text: `${article.source} - ${article.published}`,
            url: article.url
          };
          newsArticles.push(articleData);
        }
      });
    }

    // Build and append sections if there is data to display
    if (accounts.length > 0) {
      details.appendChild(buildArea("RELATED ACCOUNTS", accounts, "items-container scrollable hz-btns"));
    }
    if (wikiArticles.length > 0) {
      details.appendChild(buildArea("RELATED WIKIPEDIA ARTICLES", wikiArticles, "items-container scrollable hz-btns"));
    }
    if (newsArticles.length > 0) {
      details.appendChild(buildArea("NEWS ARTICLES", newsArticles, "items-container scrollable vr-btns"));
    }
    // If no details were found, show a message
    if (details.childNodes.length === 0) {
      details.textContent = "No additional details.";
    }
    return details;
  };

  // Function to build a topic button container that behaves like a radio button
  const buildTopicButton = (topicObj, originalTweetHTML, tweetDiv, hue) => {
    // Create a container div for the topic button
    const container = document.createElement("div");
    container.classList.add("topic-button-container");
    // Set a custom CSS property for the highlight hue
    container.style.setProperty("--highlight-hue", hue);

    // Create a header element with the topic title
    const header = document.createElement("h2");
    header.className = "topic-title";
    header.textContent = topicObj.topic;
    container.appendChild(header);

    // Build the expandable details area and append it to the container
    const detailsArea = buildExpandableArea(topicObj);
    container.appendChild(detailsArea);

    // Toggle the expanded state and update tweet highlighting when the topic button is clicked
    container.addEventListener("click", () => {
      if (container.classList.contains("expanded")) {
        // If already expanded, collapse it and restore the original tweet HTML
        container.classList.remove("expanded");
        tweetDiv.innerHTML = originalTweetHTML;
      } else {
        // Collapse any other expanded topic buttons
        document.querySelectorAll(".topic-button-container.expanded")
          .forEach(btn => btn.classList.remove("expanded"));
        // Expand the clicked topic button
        container.classList.add("expanded");
        // Reset tweet content before applying new highlights
        tweetDiv.innerHTML = originalTweetHTML;
        // Highlight all instances of the topic within the tweet text
        topicObj.instances.forEach(instance => {
          // Escape special RegExp characters in the instance string
          const escapedInstance = escapeRegExp(instance);
          // Create a RegExp to find whole word matches (case-insensitive)
          const regex = new RegExp(`\\b(${escapedInstance})\\b`, 'gi');
          // Replace matches with highlighted span elements styled with the generated hue
          tweetDiv.innerHTML = tweetDiv.innerHTML.replace(
            regex,
            `<span class="highlighted" style="--highlight-hue: ${hue}">$1</span>`
          );
        });
      }
    });
    return container;
  };

  // Function to wait until exactly 2 specific Twitter boxes (matching provided classes) are present on the page
  const twitterBoxClasses = 'div.css-175oi2r.r-kemksi.r-1kqtdi0.r-1867qdf.r-1phboty.r-rs99b7.r-1ifxtd0.r-1udh08x';
  const waitForTwoBoxes = (callback, timeout = 15000) => {
    const startTime = Date.now();
    // Function to repeatedly check for the presence of two boxes
    const checkBoxes = () => {
      const boxes = document.querySelectorAll(twitterBoxClasses);
      if (boxes.length === 2) {
        // When two boxes are found, execute the callback with these boxes
        callback(boxes);
      } else if (Date.now() - startTime > timeout) {
        // Log a message if timeout is reached
        log("Timeout reached while waiting for 2 boxes.");
      } else {
        // Otherwise, check again after 1 second
        setTimeout(checkBoxes, 1000);
      }
    };
    checkBoxes();
  };

  // Function to create and return a loading spinner element
  const createLoadingSpinner = () => {
    const spinner = document.createElement("div");
    spinner.className = "loading-spinner";
    return spinner;
  };

  // Function to create and return a status message element with provided text
  const createStatusMessage = (text) => {
    const message = document.createElement("div");
    message.className = "status-message";
    message.textContent = text;
    return message;
  };

  // Initialize the CiteThis feature
  const initCiteThis = () => {
    log("Initializing CiteThis for URL: " + location.href);
    // Remove an existing CiteThis box if it exists
    const oldBox = document.querySelector('#citethis-box');
    if (oldBox) { oldBox.remove(); }

    // Find the tweet text element (the main content of the tweet)
    const tweetDiv = document.querySelector('div[data-testid="tweetText"]');
    if (!tweetDiv) {
      // If not found, log the error and try initializing again after 1 second
      log("Tweet text element not found. Delaying initialization.");
      setTimeout(initCiteThis, 1000);
      return;
    }
    // Save the original tweet HTML so it can be restored later
    const originalTweetHTML = tweetDiv.innerHTML;

    // Wait for exactly 2 Twitter boxes to be available on the page
    waitForTwoBoxes((boxes) => {
      // Assign the two boxes to variables for clarity
      const relevantPeopleBox = boxes[0];
      const whatsHappeningBox = boxes[1];
      const parentContainer = relevantPeopleBox.parentNode;
      if (!parentContainer) {
        log("Parent container not found.");
        return;
      }

      // Create the main CiteThis container
      const citeBox = document.createElement("div");
      citeBox.id = "citethis-box";
      citeBox.className = "css-175oi2r r-kemksi r-1kqtdi0 r-1867qdf r-1phboty r-rs99b7 r-1ifxtd0 r-1udh08x";

      // Create and append the title element
      const title = document.createElement("h2");
      title.className = "cite-title";
      title.textContent = "CiteThis Sources";
      citeBox.appendChild(title);

      // Create a container for the items with an initial loading spinner
      const itemsContainer = document.createElement("div");
      itemsContainer.className = "cite-items";
      itemsContainer.appendChild(createLoadingSpinner());
      citeBox.appendChild(itemsContainer);

      // Insert the CiteThis box before the "What's happening" box
      parentContainer.insertBefore(citeBox, whatsHappeningBox);

      // Fetch topic data from the CiteThis API using a POST request
      fetch('https://citethis-api-142573238783.australia-southeast1.run.app/analyse_post', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'X-Force-Preflight': 'true'
        },
        body: JSON.stringify({ text: tweetDiv.outerHTML })
      })
      .then(response => response.json())
      .then(data => {
        // Clear the items container once data is received
        itemsContainer.innerHTML = "";
        // If topics are found in the data, build a topic button for each
        if (data.topics && data.topics.length > 0) {
          data.topics.forEach((topicObj, index) => {
            const hue = generatePastelHue(index, data.topics.length);
            const topicButton = buildTopicButton(topicObj, originalTweetHTML, tweetDiv, hue);
            itemsContainer.appendChild(topicButton);
          });
        } else {
          // If no topics were found, show a status message
          itemsContainer.appendChild(createStatusMessage("No related trends found."));
        }
      })
      .catch(error => {
        // In case of an error, clear the items container and display an error message
        itemsContainer.innerHTML = "";
        itemsContainer.appendChild(createStatusMessage("Error loading trends :("));
        console.error("Error:", error);
      });
    });
  };

  // Monitor URL changes for Single Page Application (SPA) navigation
  setInterval(() => {
    // If the URL has changed since the last check
    if (location.href !== currentUrl) {
      currentUrl = location.href;
      // Reinitialize the CiteThis feature for the new URL
      initCiteThis();
    }
  }, 1000);

  // Initial call to set up the CiteThis feature on page load
  initCiteThis();
})();
