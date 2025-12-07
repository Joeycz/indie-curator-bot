from flask import Flask, request, jsonify
from flask_cors import CORS
from curator import check_if_exists, analyze_content, save_to_notion
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow extension to access

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockItem:
    """Mock object to match feedparser entry structure expected by save_to_notion"""
    def __init__(self, title, link):
        self.title = title
        self.link = link

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/process_tweet', methods=['POST'])
def process_tweet():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload"}), 400

        title = data.get('text', '')[:100] + "..."
        full_text = data.get('text', '')
        link = data.get('url')
        images = data.get('images', [])
        
        if not link or not full_text:
            return jsonify({"status": "error", "message": "Missing link or text"}), 400

        logger.info(f"Processing: {title}")

        # 1. Deduplication
        if check_if_exists(link):
            logger.info(f"Skipping duplicate: {link}")
            return jsonify({"status": "skipped", "reason": "duplicate"})

        # 2. Analyze
        # Enhance summary with images for AI context
        summary = full_text
        if images:
            summary += f"\n\n[Images]: {', '.join(images)}"
        
        analysis = analyze_content(title, summary, link)
        
        if not analysis:
            return jsonify({"status": "error", "message": "Analysis failed"}), 500

        # Add Twitter tag specifically for this flow
        if 'tags' in analysis:
            analysis['tags'].append("Twitter")

        # 3. Save
        # We use a slightly lower threshold for user-liked content (assumed valuable)
        if analysis['score'] >= 6:
            item = MockItem(title=title, link=link)
            save_to_notion(item, analysis)
            return jsonify({"status": "saved", "score": analysis['score']})
        else:
            logger.info(f"Low score skipped: {analysis['score']}")
            return jsonify({"status": "skipped", "reason": "low_score", "score": analysis['score']})

    except Exception as e:
        logger.error(f"Server Error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    app.run(port=5000)
