chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "process_tweet") {
        // Perform fetch from the background service worker
        // This bypasses CORS if host_permissions are set correctly in manifest
        fetch("http://127.0.0.1:5000/api/process_tweet", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request.data)
        })
            .then(response => response.json())
            .then(data => {
                sendResponse(data);
            })
            .catch(error => {
                console.error("Background fetch error:", error);
                sendResponse({ status: "error", message: error.toString() });
            });

        return true; // Will respond asynchronously
    }
});
