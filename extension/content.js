// Basic Twitter scraper logic triggered by popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scrape") {
        processVisibleTweets();
        sendResponse({ status: "started" });
    }
});

async function processVisibleTweets() {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    console.log(`Found ${articles.length} visible tweets.`);

    for (const article of articles) {
        try {
            const tweetData = extractTweetData(article);
            if (tweetData) {
                // Send to local Python server
                await sendToServer(tweetData);
            }
        } catch (e) {
            console.error("Error processing tweet:", e);
        }
    }
    alert("Sync completed for visible tweets!");
}

function extractTweetData(article) {
    try {
        // 1. Get Text
        const textElement = article.querySelector('div[data-testid="tweetText"]');
        const text = textElement ? textElement.innerText : "";

        // 2. Get URL (Timestamp link usually links to the status)
        const timeElement = article.querySelector('time');
        const linkElement = timeElement ? timeElement.closest('a') : null;
        const url = linkElement ? linkElement.href : null;

        // 3. Get Images (img src in media div)
        const images = [];
        const photoElements = article.querySelectorAll('div[data-testid="tweetPhoto"] img');
        photoElements.forEach(img => {
            if (img.src) images.push(img.src);
        });

        if (!text && !url) return null;

        return { text, url, images };
    } catch (e) {
        console.error("Extraction error:", e);
        return null;
    }
}

async function sendToServer(data) {
    try {
        // Send message to background script to handle the fetch (bypasses CORS)
        const response = await chrome.runtime.sendMessage({
            action: "process_tweet",
            data: data
        });
        console.log("Server response:", response);
    } catch (e) {
        console.error("Failed to send to server:", e);
    }
}
