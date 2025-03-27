import sys
import threading
import logging
import requests
import webview
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from innertube import InnerTube

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # More permissive CORS

TARGET_SITE = "https://ytpro-cyan.vercel.app/play.html"

@app.route('/streams/<video_id>', methods=['GET'])
def get_video_info(video_id):
    try:
        logger.info(f"Fetching video info for video_id: {video_id}")

        yt = InnerTube("ANDROID")

        try:
            data = yt.player(video_id)
        except Exception as retrieval_error:
            logger.error(f"Error retrieving video data: {retrieval_error}")
            return jsonify({
                "error": f"Unable to retrieve video data: {str(retrieval_error)}",
                "status": "error"
            }), 400

        if not data or "videoDetails" not in data or "streamingData" not in data:
            logger.warning(f"No video details found for video_id: {video_id}")
            return jsonify({
                "error": "No video details found",
                "status": "error"
            }), 404

        video_details = data["videoDetails"]
        streaming_data = data["streamingData"]

        thumbnails = video_details.get("thumbnail", {}).get("thumbnails", [])
        thumbnail_url = thumbnails[-1].get("url", "") if thumbnails else ""

        audio_streams = [
            {
                "url": audio_fmt.get("url", ""),
                "format": "AUDIO",
                "quality": audio_fmt.get("audioQuality", "").replace("AUDIO_QUALITY_", "").capitalize(),
                "mimeType": audio_fmt.get("mimeType", ""),
                "codec": audio_fmt.get("mimeType", "").split(";")[0].split("/")[-1] if "mimeType" in audio_fmt else "",
                "bitrate": audio_fmt.get("bitrate", 0),
                "contentLength": int(audio_fmt.get("contentLength", 0))
            }
            for audio_fmt in streaming_data.get("adaptiveFormats", []) 
            if "audio" in audio_fmt.get("mimeType", "").lower() and audio_fmt.get("url")
        ]

        video_streams = [
            {
                "url": video_fmt.get("url", ""),
                "format": "VIDEO",
                "quality": video_fmt.get("qualityLabel", ""),
                "mimeType": video_fmt.get("mimeType", ""),
                "codec": video_fmt.get("mimeType", "").split(";")[0].split("/")[-1] if "mimeType" in video_fmt else "",
                "videoOnly": True,
                "bitrate": video_fmt.get("bitrate", 0),
                "width": video_fmt.get("width", 0),
                "height": video_fmt.get("height", 0),
                "contentLength": int(video_fmt.get("contentLength", 0))
            }
            for video_fmt in streaming_data.get("adaptiveFormats", []) 
            if "video" in video_fmt.get("mimeType", "").lower() 
            and "audio" not in video_fmt.get("mimeType", "").lower() 
            and video_fmt.get("url")
        ]

        response = {
            "title": video_details.get("title", ""),
            "description": video_details.get("shortDescription", ""),
            "thumbnailUrl": thumbnail_url,
            "audioStreams": audio_streams,
            "videoStreams": video_streams,
            "livestream": video_details.get("isLiveContent", False),
            "status": "success"
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Unexpected error in get_video_info: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Proxy route with error handling
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    try:
        url = f"{TARGET_SITE}/{path}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            **{key: value for (key, value) in request.headers if key not in ['Host', 'Cookie', 'Origin', 'Referer']}
        }
        cookies = request.cookies.to_dict() if request.cookies else {}

        response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=10)
        proxy_response = Response(
            response.content, 
            status=response.status_code, 
            content_type=response.headers.get('Content-Type', 'text/html')
        )
        return proxy_response
    
    except requests.RequestException as e:
        logger.error(f"Proxy request error: {e}")
        return jsonify({
            "error": f"Error fetching site: {e}",
            "status": "error"
        }), 500

# Error handler for 404 and 500 errors
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "error": "Page not found",
        "status": "error"
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

# Start Flask in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=30000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start PyWebView
    webview.create_window("Ytify", "http://localhost:30000")
    webview.start()
