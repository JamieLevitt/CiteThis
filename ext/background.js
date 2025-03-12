const API_URL = "https://your-api.com/trending";
const ANALYZE_URL = "https://your-api.com/analyse_tweet";

async function fetchTrendingTopics() {
  let lastFetch = await chrome.storage.local.get("citethis_lastFetch");
  let now = Date.now();

  if (!lastFetch.lastFetch || now - lastFetch.lastFetch > 3600000) {
    let response = await fetch(API_URL);
    let data = await response.json();
    await chrome.storage.local.set({ trendingTopics: data, lastFetch: now });
  }
}

chrome.runtime.onStartup.addListener(fetchTrendingTopics);
chrome.runtime.onInstalled.addListener(fetchTrendingTopics);