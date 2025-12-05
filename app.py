from flask import Flask, render_template, send_file, request, abort
import os
import zipfile
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# Configuration via environment variables
ROOT_PATH = os.getenv('ROOT_PATH', '/data')
FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))

def get_file_info(path):
    """Returns file/folder information"""
    stats = os.stat(path)
    return {
        'name': os.path.basename(path),
        'size': stats.st_size,
        'modified': datetime.fromtimestamp(stats.st_mtime),
        'is_dir': os.path.isdir(path)
    }

def format_size(size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def get_directory_listing(path):
    """List directory contents"""
    items = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                info = get_file_info(item_path)
                items.append(info)
            except (OSError, PermissionError):
                continue
    except (OSError, PermissionError):
        return []

    # Sort: folders first, then files by name
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return items

def is_safe_path(path):
    """Security check: prevent access outside ROOT_PATH"""
    return os.path.abspath(path).startswith(os.path.abspath(ROOT_PATH))

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    """Main page with navigation"""
    current_path = os.path.join(ROOT_PATH, subpath)

    if not is_safe_path(current_path):
        abort(403)

    if not os.path.exists(current_path):
        abort(404)

    # If it's a file, download it directly
    if os.path.isfile(current_path):
        return send_file(current_path, as_attachment=True)

    items = get_directory_listing(current_path)

    # Build breadcrumb navigation
    breadcrumb = []
    if subpath:
        parts = subpath.split('/')
        for i, part in enumerate(parts):
            breadcrumb.append({
                'name': part,
                'path': '/'.join(parts[:i+1])
            })

    return render_template('index.html',
                         items=items,
                         current_path=subpath,
                         breadcrumb=breadcrumb,
                         format_size=format_size)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    """Download single file"""
    full_path = os.path.join(ROOT_PATH, filepath)

    if not is_safe_path(full_path):
        abort(403)

    if not os.path.exists(full_path):
        abort(404)

    if os.path.isfile(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        abort(400)

@app.route('/download-multiple', methods=['POST'])
def download_multiple():
    """Download multiple files/folders as ZIP"""
    files = request.form.getlist('files[]')
    current_path = request.form.get('current_path', '')

    if not files:
        abort(400)

    # Create ZIP in memory
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            full_path = os.path.join(ROOT_PATH, current_path, file)

            if not is_safe_path(full_path):
                continue

            if not os.path.exists(full_path):
                continue

            if os.path.isfile(full_path):
                zf.write(full_path, file)
            elif os.path.isdir(full_path):
                # Add all files from folder
                for root, dirs, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.join(file, os.path.relpath(file_path, full_path))
                        try:
                            zf.write(file_path, arcname)
                        except (OSError, PermissionError):
                            continue

    memory_file.seek(0)

    zip_name = 'files.zip'
    if len(files) == 1:
        zip_name = f'{files[0]}.zip'

    return send_file(memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=zip_name)

@app.route('/download-all/<path:subpath>')
@app.route('/download-all')
def download_all(subpath=''):
    """Download entire folder as ZIP"""
    current_path = os.path.join(ROOT_PATH, subpath)

    if not is_safe_path(current_path):
        abort(403)

    if not os.path.exists(current_path) or not os.path.isdir(current_path):
        abort(404)

    # Create ZIP in memory
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(current_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, current_path)
                try:
                    zf.write(file_path, arcname)
                except (OSError, PermissionError):
                    continue

    memory_file.seek(0)

    folder_name = os.path.basename(current_path) if subpath else 'root'
    zip_name = f'{folder_name}.zip'

    return send_file(memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=zip_name)

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', 
                         error_code=403,
                         error_message='Access Forbidden'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html',
                         error_code=404,
                         error_message='File or Directory Not Found'), 404

if __name__ == '__main__':
    print(f"🗂️  Desk Swap v1.0 starting...")
    print(f"📂 Root path: {ROOT_PATH}")
    print(f"🌐 Server: http://0.0.0.0:{FLASK_PORT}")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
