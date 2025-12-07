document.getElementById("syncBtn").addEventListener("click", () => {
    const statusDiv = document.getElementById("status");
    statusDiv.textContent = "Syncing...";
    statusDiv.className = "";

    // Query the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];

        // Check if it's Twitter
        if (!activeTab.url.includes("twitter.com") && !activeTab.url.includes("x.com")) {
            statusDiv.textContent = "Please open Twitter/X first.";
            statusDiv.className = "error";
            return;
        }

        // Inject content script
        chrome.scripting.executeScript({
            target: { tabId: activeTab.id },
            files: ["content.js"]
        }, () => {
            // Send message to content script to start
            chrome.tabs.sendMessage(activeTab.id, { action: "scrape" }, (response) => {
                if (chrome.runtime.lastError) {
                    statusDiv.textContent = "Error: " + chrome.runtime.lastError.message;
                    statusDiv.className = "error";
                } else if (response && response.status === "started") {
                    statusDiv.textContent = "Processing... Check Python console.";
                    statusDiv.className = "success";
                } else {
                    statusDiv.textContent = "Failed to start.";
                    statusDiv.className = "error";
                }
            });
        });
    });
});
