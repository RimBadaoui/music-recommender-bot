import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from llmproxy import LLMProxy

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

proxy = LLMProxy()
SESSION_ID = "my-app-session"

# Upload all .txt files from the data folder once on startup
data_dir = "data"

for filename in os.listdir(data_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(data_dir, filename)
        result = proxy.upload_file(
            file_path=file_path,
            session_id=SESSION_ID,
            mime_type="text/plain",
            description=filename,
            strategy="smart",
        )
        print(f"Uploaded {filename}: {result}")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    response = proxy.generate(
        model="4o-mini",
        system="You are a friendly assistant that suggests songs to users based on their mood. The query you will recieve describes the user's mood. Based on that, search the RAG context and suggest 2 or 3 songs that best match their mood. Explain briefly why you chose those songs. However, if the user displays signs of depression or suicidal thoughts, direct them to contact a medical professional immediately and do not provide song recommendations. However, if the user is simply sad, and it's nothing serious, you can recommend some sad songs.",
        query=user_query,
        session_id=SESSION_ID,
        rag_usage=True,
        rag_threshold=0.8,
        rag_k=5,
    )

    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
