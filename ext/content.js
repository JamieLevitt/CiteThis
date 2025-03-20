(function() {
  let currentUrl = location.href;

  // --- Monkey-patch history methods to dispatch a 'locationchange' event ---
  (function() {
    const _wr = function(type) {
      const orig = history[type];
      return function() {
        const rv = orig.apply(this, arguments);
        window.dispatchEvent(new Event('locationchange'));
        return rv;
      };
    };
    history.pushState = _wr('pushState');
    history.replaceState = _wr('replaceState');
    window.addEventListener('popstate', function(){
      window.dispatchEvent(new Event('locationchange'));
    });
  })();

  // Logging helper.
  function log(msg) {
    console.log("[CiteThis]", msg);
  }

  // Escape RegExp special characters.
  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Generate a pastel color and return both the color and its hue.
  // Pastel color: hsl(hue, 70%, 80%)
  function generatePastelColor(index, total) {
    const hue = Math.floor(index * (360 / total));
    return { pastel: `hsl(${hue}, 70%, 80%)`, hue: hue };
  }

  // Build a link button for detail items.
  // Every link element is rendered as a button with class "citethis-link-button".
  function buildLinkButton(item) {
    const btn = document.createElement("button");
    btn.className = "citethis-link-button";
    btn.textContent = item.text;
    btn.addEventListener("click", () => {
      window.open(item.url.startsWith("http") ? item.url : ("https://" + item.url), "_blank");
    });
    return btn;
  }

  // Build an area/section for a given category.
  // containerClass is provided (for example: "items-container scrollable accounts")
  function buildArea(titleText, items, containerClass) {
    const section = document.createElement("div");
    section.className = "detail-section";
    const header = document.createElement("h4");
    header.textContent = titleText;
    section.appendChild(header);
    const container = document.createElement("div");
    container.className = containerClass;
    let built_labels = [];
    items.forEach(item => {
      console.log(item.text)
      if (built_labels.includes(item.text) != true) {
        const btn = buildLinkButton(item);
        container.appendChild(btn);}
        built_labels.push(item.text)
    });
    section.appendChild(container);
    return section;
  }

  // Build an expandable details area from the API data.
  function buildExpandableArea(topicObj) {
    const details = document.createElement("div");
    details.className = "topic-details";

    let accounts = [];
    let wikiArticles = [];
    let priorityArticles = [];
    let newsArticles = [];

    // Collect data from entities.
    if (topicObj.entities && topicObj.entities.length > 0) {
      topicObj.entities.forEach(entity => {
        if (entity.twitter_url && entity.twitter_url.trim() !== "") {
          let parts = entity.twitter_url.split("/").filter(p => p);
          if (parts.length > 0) {
            accounts.push({
              text: "@" + parts[parts.length - 1],
              url: "https://x.com/" + parts[parts.length - 1]
            });
          }
        }
        if (entity.wiki_url && entity.wiki_url.trim() !== "") {
          let title = entity.wiki_url.split("/wiki/")[1]?.replace(/_/g, " ") || entity.wiki_url;
          wikiArticles.push({
            text: title,
            url: entity.wiki_url
          });
        }
      });
    }
    // Collect articles data.
    if (topicObj.articles && topicObj.articles.length > 0) {
      topicObj.articles.forEach(article => {
        if (article.url && article.url.trim() !== "") {
          const articleData = {
            text: `${article.source} - ${article.published.split(" ")[0]}`,
            url: article.url
          };
          if (article.priority) {
            priorityArticles.push(articleData);
          } else {
            newsArticles.push(articleData);
          }
        }
      });
    }

    // Build sections using the same layout for accounts and wiki (scrollable area).
    if (accounts.length > 0) {
      details.appendChild(buildArea("RELATED ACCOUNTS", accounts, "items-container scrollable accounts"));
    }
    if (wikiArticles.length > 0) {
      details.appendChild(buildArea("RELATED WIKIPEDIA ARTICLES", wikiArticles, "items-container scrollable wiki"));
    }
    // Priority articles: vertical list, non-scrollable.
    if (priorityArticles.length > 0) {
      details.appendChild(buildArea("PRIORITY NEWS ARTICLES", priorityArticles, "items-container priority"));
    }
    // News articles: vertical list in a scrollable area.
    if (newsArticles.length > 0) {
      details.appendChild(buildArea("NEWS ARTICLES", newsArticles, "items-container scrollable news"));
    }
    if (details.childNodes.length === 0) {
      details.textContent = "No additional details.";
    }
    return details;
  }

  // Build a topic button container that acts like a radio button.
  function buildTopicButton(topicObj, originalTweetHTML, tweetDiv, index) {
    const container = document.createElement("div");
    container.classList.add("topic-button-container");
    // Create a header for the topic.
    const header = document.createElement("h2");
    header.className = "topic-title";
    header.textContent = topicObj.topic;
    container.appendChild(header);
    // Append the expandable details area.
    const detailsArea = buildExpandableArea(topicObj);
    container.appendChild(detailsArea);

    // Click behavior: toggle expanded state and update tweet text highlighting.
    container.addEventListener("click", () => {
      if (container.classList.contains("expanded")) {
        container.classList.remove("expanded");
        tweetDiv.innerHTML = originalTweetHTML;
      } else {
        document.querySelectorAll(".topic-button-container.expanded").forEach(btn => btn.classList.remove("expanded"));
        container.classList.add("expanded");
        tweetDiv.innerHTML = originalTweetHTML;
        topicObj.instances.forEach(instance => {
          const escapedInstance = escapeRegExp(instance);
          const regex = new RegExp(`\\b(${escapedInstance})\\b`, 'gi');
          tweetDiv.innerHTML = tweetDiv.innerHTML.replace(
            regex,
            `<span class="highlighted">$1</span>`
          );
        });
      }
    });
    return container;
  }

  // Wait until exactly 2 divs with Twitter's classes exist.
  const twitterBoxClasses = 'div.css-175oi2r.r-kemksi.r-1kqtdi0.r-1867qdf.r-1phboty.r-rs99b7.r-1ifxtd0.r-1udh08x';
  function waitForTwoBoxes(callback, timeout = 15000) {
    const startTime = Date.now();
    function check() {
      const boxes = document.querySelectorAll(twitterBoxClasses);
      log("Found " + boxes.length + " boxes matching selector: " + twitterBoxClasses);
      if (boxes.length === 2) {
        callback(boxes);
      } else if (Date.now() - startTime > timeout) {
        log("Timeout reached while waiting for 2 boxes.");
      } else {
        setTimeout(check, 1000);
      }
    }
    check();
  }

  // Main initialization function.
  function initCiteThis() {
    log("Initializing CiteThis for URL: " + location.href);
    const oldBox = document.querySelector('#citethis-box');
    if (oldBox) { oldBox.remove(); }

    const tweetDiv = document.querySelector('div[data-testid="tweetText"]');
    if (!tweetDiv) {
      log("Tweet text element not found. Delaying initialization.");
      setTimeout(initCiteThis, 1000);
      return;
    }
    const originalTweetHTML = tweetDiv.innerHTML;
    log("Tweet HTML saved.");

    waitForTwoBoxes((boxes) => {
      log("Two boxes found. Inserting CiteThis box.");
      const relevantPeopleBox = boxes[0];
      const whatsHappeningBox = boxes[1];
      const parentContainer = relevantPeopleBox.parentNode;
      if (!parentContainer) {
        log("Parent container not found.");
        return;
      }
      // Create the main container using Twitter's classes.
      const citeBox = document.createElement("div");
      citeBox.id = "citethis-box";
      citeBox.className = "css-175oi2r r-kemksi r-1kqtdi0 r-1867qdf r-1phboty r-rs99b7 r-1ifxtd0 r-1udh08x";
      // Create a title element.
      const title = document.createElement("h2");
      title.className = "cite-title";
      title.textContent = "CiteThis Sources";
      citeBox.appendChild(title);
      // Create a container for topic buttons.
      const itemsContainer = document.createElement("div");
      itemsContainer.className = "cite-items";
      citeBox.appendChild(itemsContainer);

      parentContainer.insertBefore(citeBox, whatsHappeningBox);

      // Fetch topic data from your Flask API.
      fetch('https://citethis-api-142573238783.australia-southeast1.run.app/analyse_post', {
        method: 'POST',
        mode: 'cors', // ensure CORS mode is enabled
        headers: {
          'Content-Type': 'application/json',
          'X-Force-Preflight': 'true'  // custom header to trigger a preflight request
        },
        body: JSON.stringify({ text: tweetDiv.outerHTML })
      })
      .then(response => response.json())
      .then(data => {
        log("API response received.");
        itemsContainer.innerHTML = "";
        const topics = data.topics;
        topics.forEach((topicObj, index) => {
          const topicButton = buildTopicButton(topicObj, originalTweetHTML, tweetDiv, index);
          itemsContainer.appendChild(topicButton);
        });
      })
      .catch(error => {
        itemsContainer.textContent = "Error loading topics.";
        console.error("Error:", error);
      });
    });
  }


  // Monitor URL changes for SPA navigation.
  setInterval(() => {
    if (location.href !== currentUrl) {
      currentUrl = location.href;
      log("URL changed, reinitializing CiteThis.");
      initCiteThis();
    }
  }, 1000);

  // Initial call.
  initCiteThis();
})();
