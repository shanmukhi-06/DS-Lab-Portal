import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import database

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ds_lab_portal_secret_2026')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB limit for video & images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("VERCEL"):
    UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
VIDEO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'svg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}

try:
    os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)
except Exception:
    pass


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file_storage, target_dir, allowed_extensions):
    """Save an uploaded file safely with a unique prefix and return relative URL."""
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Supported extensions: {', '.join(allowed_extensions)}")
    
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'bin'
    unique_filename = f"{uuid.uuid4().hex[:10]}_{original_name}"
    file_path = os.path.join(target_dir, unique_filename)
    file_storage.save(file_path)
    
    subfolder = 'images' if target_dir == IMAGE_UPLOAD_FOLDER else 'videos'
    return f"/static/uploads/{subfolder}/{unique_filename}"


# Initialize database schema and seeds
database.init_db()


# ----------------- ROUTES -----------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/static/docs/<path:filename>')
def serve_docs(filename):
    docs_dir = os.path.join(BASE_DIR, 'static', 'docs')
    response = send_from_directory(docs_dir, filename)
    response.headers['Content-Disposition'] = 'inline'
    if filename.lower().endswith('.pdf'):
        response.headers['Content-Type'] = 'application/pdf'
    return response


# Overview statistics
@app.route('/api/counts', methods=['GET'])
def get_counts_api():
    try:
        counts = database.get_counts()
        return jsonify({"success": True, "data": counts})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 1. Student Profile API
@app.route('/api/student', methods=['GET'])
def get_student_api():
    student = database.get_student()
    if not student:
        return jsonify({"success": False, "message": "Student profile not found"}), 404
    return jsonify({"success": True, "data": student})


@app.route('/api/student', methods=['POST', 'PUT'])
def update_student_api():
    try:
        name = request.form.get('name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        section = request.form.get('section', '').strip()
        branch = request.form.get('branch', '').strip()
        subject = request.form.get('subject', 'Data Science').strip()
        faculty = request.form.get('faculty', 'Faculty In-Charge').strip()
        github_url = request.form.get('github_url', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        website_url = request.form.get('website_url', '').strip()
        assistant_professor = request.form.get('assistant_professor', '').strip()

        if not name or not roll_no:
            return jsonify({"success": False, "message": "Name and Roll Number are required."}), 400

        photo_url = None
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo_url = save_uploaded_file(request.files['photo'], IMAGE_UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS)

        updated_student = database.update_student(
            name=name,
            roll_no=roll_no,
            section=section,
            branch=branch,
            assistant_professor=assistant_professor,
            github_url=github_url,
            photo_url=photo_url,
            subject=subject,
            faculty=faculty,
            linkedin_url=linkedin_url,
            website_url=website_url
        )
        return jsonify({"success": True, "message": "ID card updated successfully", "data": updated_student})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


# 2. Experiments API
@app.route('/api/experiments', methods=['GET'])
def get_experiments_api():
    search_query = request.args.get('q', '').strip()
    experiments = database.get_experiments(search=search_query if search_query else None)
    return jsonify({"success": True, "count": len(experiments), "data": experiments})


@app.route('/api/experiments/<int:exp_id>', methods=['GET'])
def get_single_experiment_api(exp_id):
    experiment = database.get_experiment(exp_id)
    if not experiment:
        return jsonify({"success": False, "message": "Experiment not found"}), 404
    return jsonify({"success": True, "data": experiment})


@app.route('/api/experiments', methods=['POST'])
def add_experiment_api():
    try:
        experiment_no = request.form.get('experiment_no', '').strip()
        title = request.form.get('title', '').strip()
        short_description = request.form.get('short_description', '').strip()
        d2_heading = request.form.get('d2_heading', 'Long Description').strip()
        long_content = request.form.get('long_content', '').strip()
        github_url = request.form.get('github_url', '').strip()

        if not experiment_no:
            return jsonify({"success": False, "message": "Experiment number is required."}), 400
        if not title:
            return jsonify({"success": False, "message": "Experiment title is required."}), 400
        if not short_description:
            return jsonify({"success": False, "message": "Short description is required."}), 400
        if not long_content:
            return jsonify({"success": False, "message": "Experiment full content is required."}), 400

        cover_url = None
        if 'cover_image' in request.files and request.files['cover_image'].filename != '':
            cover_url = save_uploaded_file(request.files['cover_image'], IMAGE_UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS)
        else:
            cover_url = '/static/images/default-cover.svg'

        video_url = None
        if 'video' in request.files and request.files['video'].filename != '':
            video_url = save_uploaded_file(request.files['video'], VIDEO_UPLOAD_FOLDER, ALLOWED_VIDEO_EXTENSIONS)

        new_exp = database.add_experiment(
            experiment_no=experiment_no,
            title=title,
            short_description=short_description,
            d2_heading=d2_heading or 'Long Description',
            long_content=long_content,
            github_url=github_url,
            cover_url=cover_url,
            video_url=video_url
        )

        return jsonify({"success": True, "message": "Experiment added successfully", "data": new_exp}), 201

    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/experiments/<int:exp_id>', methods=['DELETE'])
def delete_experiment_api(exp_id):
    try:
        exp = database.get_experiment(exp_id)
        if not exp:
            return jsonify({"success": False, "message": "Experiment not found"}), 404

        media_urls = database.delete_experiment(exp_id)

        for url in media_urls:
            if url and url.startswith('/static/uploads/'):
                rel_path = url.replace('/static/', '')
                file_path = os.path.join(BASE_DIR, 'static', rel_path.replace('/', os.sep))
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as err:
                        app.logger.warning(f"Could not remove file {file_path}: {err}")

        return jsonify({"success": True, "message": f"Experiment {exp.get('experiment_no', exp_id)} deleted successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


# 3. Modules API
@app.route('/api/modules', methods=['GET'])
def get_modules_api():
    try:
        mods = database.get_modules()
        return jsonify({"success": True, "count": len(mods), "data": mods})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/modules', methods=['POST'])
def add_module_api():
    try:
        module_no = request.form.get('module_no', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        topics = request.form.get('topics', '').strip()

        if not module_no or not title:
            return jsonify({"success": False, "message": "Module Number and Title are required."}), 400

        mod = database.add_module(module_no, title, description, topics)
        return jsonify({"success": True, "message": "Module added successfully", "data": mod}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/modules/<int:mod_id>', methods=['DELETE'])
def delete_module_api(mod_id):
    try:
        database.delete_module(mod_id)
        return jsonify({"success": True, "message": "Module deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 4. Tools API
@app.route('/api/tools', methods=['GET'])
def get_tools_api():
    try:
        tools = database.get_tools()
        return jsonify({"success": True, "count": len(tools), "data": tools})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/tools', methods=['POST'])
def add_tool_api():
    try:
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        tool_url = request.form.get('tool_url', '').strip()

        if not name:
            return jsonify({"success": False, "message": "Tool name is required."}), 400

        tool = database.add_tool(name, category, description, tool_url)
        return jsonify({"success": True, "message": "Tool added successfully", "data": tool}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/tools/<int:tool_id>', methods=['DELETE'])
def delete_tool_api(tool_id):
    try:
        database.delete_tool(tool_id)
        return jsonify({"success": True, "message": "Tool deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 5. Resources API
@app.route('/api/resources', methods=['GET'])
def get_resources_api():
    try:
        res = database.get_resources()
        return jsonify({"success": True, "count": len(res), "data": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/resources', methods=['POST'])
def add_resource_api():
    try:
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        link_url = request.form.get('link_url', '').strip()

        if not title:
            return jsonify({"success": False, "message": "Resource title is required."}), 400

        item = database.add_resource(title, category, description, link_url)
        return jsonify({"success": True, "message": "Resource added successfully", "data": item}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/resources/<int:res_id>', methods=['DELETE'])
def delete_resource_api(res_id):
    try:
        database.delete_resource(res_id)
        return jsonify({"success": True, "message": "Resource deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[DS LAB] Server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
