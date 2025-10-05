import os
import json
import time
import uuid
from urllib.parse import quote_plus

from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

load_dotenv()

# File-based storage for call results - no in-memory data
CALL_RESULTS_DIR = "call_results"

# Ensure results directory exists
os.makedirs(CALL_RESULTS_DIR, exist_ok=True)

# Initialize Twilio client and constants
client = Client(os.getenv("account_sid"), os.getenv("auth_token"))
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
BASE_URL = os.getenv("BASE_URL", "https://217fc92e7298.ngrok-free.app")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def save_call_result(request_id: str, digit: str):
    """Save call result to disk"""
    result_file = os.path.join(CALL_RESULTS_DIR, f"{request_id}.json")
    data = {
        "request_id": request_id,
        "digit": digit,
        "timestamp": time.time(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(result_file, 'w') as f:
        json.dump(data, f)


def get_call_result(request_id: str) -> str:
    """Get call result from disk"""
    result_file = os.path.join(CALL_RESULTS_DIR, f"{request_id}.json")
    if os.path.exists(result_file):
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
            return data.get("digit", "")
        except Exception as e:
            return ""
    return ""


def cleanup_call_result(request_id: str):
    """Remove call result file from disk"""
    result_file = os.path.join(CALL_RESULTS_DIR, f"{request_id}.json")
    if os.path.exists(result_file):
        try:
            os.remove(result_file)
        except Exception as e:
            pass


@app.route("/my-api/agent", methods=["GET"])
def run_workflow():
    """Run the approval workflow via HTTP endpoint"""
    import main

    result = main.approval_workflow.run()

    return jsonify({
        "ok": True,
        "result": result.content
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint for frontend - runs the approval workflow based on user message"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Run the workflow
        import main
        result = main.approval_workflow.run()
        
        response_data = {
            "response": result.content,
            "ok": True
        }
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_msg = f"Workflow failed: {str(e)}"
        return jsonify({
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "ok": False
        }), 500


@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve audio files to Twilio"""
    try:
        audio_dir = os.path.join(os.path.dirname(__file__), "audio_generations")
        file_path = os.path.join(audio_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype="audio/mpeg")
        else:
            return "Audio file not found", 404
            
    except Exception as e:
        return "Error serving audio file", 500


@app.route("/voice", methods=["POST", "GET"])
def voice():
    """Initial call endpoint - plays message and gathers DTMF input"""
    try:
        message = request.args.get("msg", "Please enter a key.")
        request_id = request.args.get("request_id", "")

        vr = VoiceResponse()
        g = Gather(
            input="dtmf",
            num_digits=1,
            timeout=45,
            action=f"{BASE_URL}/gather?request_id={quote_plus(request_id)}",
            method="POST"
        )

        # Play audio file or speak text
        if message.endswith('.mp3') and os.path.exists(message):
            filename = os.path.basename(message)
            audio_url = f"{BASE_URL}/audio/{filename}"
            g.play(audio_url)
        else:
            g.say(message)

        vr.append(g)
        vr.say("No input received. Goodbye.")
        vr.hangup()
        
        return Response(str(vr), mimetype="text/xml")
        
    except Exception as e:
        # Return a simple fallback TwiML response
        vr = VoiceResponse()
        vr.say("Sorry, there was an error processing your call. Please try again later.")
        vr.hangup()
        return Response(str(vr), mimetype="text/xml")


@app.route("/elevenlabs-webhook", methods=["POST"])
def elevenlabs_webhook():
    """Handle ElevenLabs webhook notifications"""
    try:
        data = request.get_json()
        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": "webhook processing failed"}), 500


@app.route("/gather", methods=["POST"])
def gather():
    """Handle DTMF input from Twilio"""
    try:
        digits = request.form.get("Digits")
        request_id = request.args.get("request_id", "")
        
        if request_id:
            save_call_result(request_id, digits or "")
        
        vr = VoiceResponse()
        if digits:
            vr.say(f"Thanks. You pressed {digits}.")
        else:
            vr.say("No input detected.")
        
        vr.hangup()
        
        return Response(str(vr), mimetype="text/xml")
        
    except Exception as e:
        # Return a simple fallback TwiML response
        vr = VoiceResponse()
        vr.say("Sorry, there was an error processing your input.")
        vr.hangup()
        return Response(str(vr), mimetype="text/xml")


def call_and_collect(to_number: str, message: str, timeout_sec: int = 45) -> str:
    """
    Make a Twilio call, play message, and collect 1 DTMF keypress.
    Uses disk-based polling to avoid Flask restart issues.
    
    Args:
        to_number: Phone number to call (E.164 format)
        message: Text to speak or path to MP3 file
        timeout_sec: Seconds to wait for input
        
    Returns:
        Pressed digit (str) or "timeout"/"error" on failure
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Initiate Twilio call
        call_url = f"{BASE_URL}/voice?msg={quote_plus(message)}&request_id={request_id}"
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_FROM,
            url=call_url
        )
        
        # Poll disk for result every second until timeout
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            digit = get_call_result(request_id)
            
            if digit:
                cleanup_call_result(request_id)
                return digit
            
            time.sleep(1)  # Poll every second
        
        # Final check after timeout
        digit = get_call_result(request_id)
        if digit:
            cleanup_call_result(request_id)
            return digit
        
        # No result found
        cleanup_call_result(request_id)
        return "timeout"
            
    except Exception as e:
        cleanup_call_result(request_id)
        return f"error: {str(e)}"


def run_server():
    """Start Flask server"""
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "3000"))
    app.run(host=host, port=port, debug=True, threaded=True, use_reloader=False)


if __name__ == "__main__":
    run_server()
