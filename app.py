from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# temporary storage (simulates database)
comments = []

# POST endpoint to create comment
@app.route('/api/comments', methods=['POST'])
def create_comment():
    data = request.json

    comment = {
        "comment": data["comment"],
        "user_id": data["user_id"],
        "book_id": data["book_id"],
        "timestamp": datetime.now().isoformat()
    }

    comments.append(comment)

    return jsonify({"message": "Comment created successfully"}), 201


# GET endpoint to view comments
@app.route('/api/comments', methods=['GET'])
def get_comments():
    return jsonify(comments)


if __name__ == '__main__':
    app.run(port=5000)
