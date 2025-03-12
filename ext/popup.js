document.addEventListener("DOMContentLoaded", () => {
    const keywordList = document.getElementById("keyword-list");
    const refreshButton = document.getElementById("refresh");

    const keywords = localStorage.getItem('CiteThis Keywords')

    // Display keyword list
    keywordList.innerHTML = keywords.map(word => `<li>${word}</li>`).join("");

    // Refresh Twitter page when clicked
    refreshButton.addEventListener("click", () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0].url.includes("x.com")) {
                chrome.scripting.executeScript({
                    target: { tabId: tabs[0].id },
                    function: () => location.reload()
                });
            }
        });
    });
});
