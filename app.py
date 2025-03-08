from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def upload_page():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    chunk_number = int(request.form.get("chunkNumber", 0))
    total_chunks = int(request.form.get("totalChunks", 1))
    filename = request.form.get("filename")
    
    # Check if file already exists before starting upload
    final_path = os.path.join(UPLOAD_FOLDER, filename)
    if chunk_number == 0 and os.path.exists(final_path):
        return jsonify({
            "error": "File already exists",
            "message": f"A file named '{filename}' already exists"
        }), 409
    
    temp_path = os.path.join(UPLOAD_FOLDER, filename + ".part")
    
    with open(temp_path, "ab") as f:
        f.write(file.read())
    
    if chunk_number + 1 == total_chunks:
        os.rename(temp_path, final_path)
        return jsonify({
            "message": "Upload complete",
            "filename": filename
        }), 200
    
    return jsonify({"message": "Chunk received", "chunk": chunk_number}), 200

@app.route("/cancel-upload", methods=["POST"])
def cancel_upload():
    filename = request.form.get("filename")
    if not filename:
        return jsonify({"error": "Filename is required"}), 400
    
    # Remove only partial file if it exists
    temp_path = os.path.join(UPLOAD_FOLDER, filename + ".part")
    
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
            return jsonify({"message": "Upload cancelled and partial file cleared"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to clear partial file: {str(e)}"}), 500
    
    return jsonify({"message": "No partial file found to clear"}), 200

    
if __name__ == "__main__":
    app.run(debug=True)