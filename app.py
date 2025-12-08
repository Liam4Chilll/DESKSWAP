from flask import Flask, render_template, send_file, request, abort, jsonify
import os
import zipfile
from io import BytesIO
from datetime import datetime
import mimetypes
from werkzeug.utils import secure_filename
import psutil

app = Flask(__name__)

ROOT_PATH = '/home/user'

def get_file_info(path):
    """Retourne les informations d'un fichier/dossier"""
    stats = os.stat(path)
    return {
        'name': os.path.basename(path),
        'size': stats.st_size,
        'modified': datetime.fromtimestamp(stats.st_mtime),
        'is_dir': os.path.isdir(path)
    }

def format_size(size):
    """Formate la taille en bytes vers un format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def get_directory_listing(path, show_hidden=False):
    """Liste le contenu d'un dossier"""
    items = []
    try:
        for item in os.listdir(path):
            # Filtrer les fichiers cachés si show_hidden est False
            if not show_hidden and item.startswith('.'):
                continue

            item_path = os.path.join(path, item)
            try:
                info = get_file_info(item_path)
                items.append(info)
            except (OSError, PermissionError):
                continue
    except (OSError, PermissionError):
        return []

    # Trier : dossiers d'abord, puis fichiers par nom
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return items

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    """Page principale avec navigation"""
    current_path = os.path.join(ROOT_PATH, subpath)

    # Vérification de sécurité : empêcher l'accès en dehors de ROOT_PATH
    if not os.path.abspath(current_path).startswith(os.path.abspath(ROOT_PATH)):
        abort(403)

    if not os.path.exists(current_path):
        abort(404)

    # Si c'est un fichier, le télécharger directement
    if os.path.isfile(current_path):
        return send_file(current_path, as_attachment=True)

    # Récupérer le paramètre show_hidden depuis la query string
    show_hidden = request.args.get('show_hidden', 'false').lower() == 'true'
    items = get_directory_listing(current_path, show_hidden=show_hidden)

    # Construire le breadcrumb
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
    """Télécharge un fichier unique"""
    full_path = os.path.join(ROOT_PATH, filepath)

    # Vérification de sécurité
    if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_PATH)):
        abort(403)

    if not os.path.exists(full_path):
        abort(404)

    if os.path.isfile(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        abort(400)

@app.route('/download-multiple', methods=['POST'])
def download_multiple():
    """Télécharge plusieurs fichiers/dossiers en ZIP"""
    files = request.form.getlist('files[]')
    current_path = request.form.get('current_path', '')

    if not files:
        abort(400)

    # Créer un ZIP en mémoire
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            full_path = os.path.join(ROOT_PATH, current_path, file)

            # Vérification de sécurité
            if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_PATH)):
                continue

            if not os.path.exists(full_path):
                continue

            if os.path.isfile(full_path):
                zf.write(full_path, file)
            elif os.path.isdir(full_path):
                # Ajouter tous les fichiers du dossier
                for root, dirs, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.join(file, os.path.relpath(file_path, full_path))
                        zf.write(file_path, arcname)

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
    """Télécharge tout le contenu d'un dossier en ZIP"""
    current_path = os.path.join(ROOT_PATH, subpath)

    # Vérification de sécurité
    if not os.path.abspath(current_path).startswith(os.path.abspath(ROOT_PATH)):
        abort(403)

    if not os.path.exists(current_path) or not os.path.isdir(current_path):
        abort(404)

    # Créer un ZIP en mémoire
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

@app.route('/upload', methods=['POST'])
def upload_files():
    """Upload des fichiers dans le dossier courant"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    files = request.files.getlist('files[]')
    current_path = request.form.get('current_path', '')
    upload_path = os.path.join(ROOT_PATH, current_path)

    # Vérification de sécurité
    if not os.path.abspath(upload_path).startswith(os.path.abspath(ROOT_PATH)):
        return jsonify({'error': 'Accès refusé'}), 403

    if not os.path.exists(upload_path) or not os.path.isdir(upload_path):
        return jsonify({'error': 'Dossier de destination invalide'}), 400

    uploaded_files = []
    errors = []

    for file in files:
        if file.filename == '':
            continue

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_path, filename)

            # Créer les sous-dossiers si nécessaire (pour l'upload de dossiers)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            file.save(file_path)
            uploaded_files.append(filename)
        except Exception as e:
            errors.append(f'{file.filename}: {str(e)}')

    result = {
        'uploaded': uploaded_files,
        'count': len(uploaded_files)
    }

    if errors:
        result['errors'] = errors

    return jsonify(result)

@app.route('/search')
def search_files():
    """Recherche de fichiers par nom"""
    query = request.args.get('q', '').lower().strip()
    current_path = request.args.get('path', '')
    show_hidden = request.args.get('show_hidden', 'false').lower() == 'true'

    if not query:
        return jsonify({'results': []})

    search_path = os.path.join(ROOT_PATH, current_path)

    # Vérification de sécurité
    if not os.path.abspath(search_path).startswith(os.path.abspath(ROOT_PATH)):
        abort(403)

    if not os.path.exists(search_path):
        return jsonify({'results': []})

    results = []

    # Recherche récursive
    try:
        for root, dirs, files in os.walk(search_path):
            # Filtrer les répertoires cachés si nécessaire
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]

            # Rechercher dans les noms de dossiers
            for dirname in dirs:
                if query in dirname.lower():
                    rel_path = os.path.relpath(os.path.join(root, dirname), ROOT_PATH)
                    results.append({
                        'name': dirname,
                        'path': rel_path,
                        'is_dir': True
                    })

            # Rechercher dans les noms de fichiers
            for filename in files:
                if query in filename.lower():
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, ROOT_PATH)
                    try:
                        stats = os.stat(full_path)
                        results.append({
                            'name': filename,
                            'path': rel_path,
                            'is_dir': False,
                            'size': stats.st_size,
                            'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                        })
                    except (OSError, PermissionError):
                        continue

            # Limiter à 100 résultats
            if len(results) >= 100:
                break
    except (OSError, PermissionError):
        pass

    return jsonify({'results': results[:100]})

@app.route('/metrics')
def system_metrics():
    """Retourne les métriques système (CPU, RAM, Disque)"""
    try:
        # Métriques disque pour ROOT_PATH
        disk = psutil.disk_usage(ROOT_PATH)
        disk_used = disk.used / (1024**3)  # GB
        disk_total = disk.total / (1024**3)  # GB
        disk_percent = disk.percent

        # Métriques RAM
        memory = psutil.virtual_memory()
        ram_used = memory.used / (1024**3)  # GB
        ram_total = memory.total / (1024**3)  # GB
        ram_percent = memory.percent

        # Métriques CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        return jsonify({
            'disk': {
                'used': disk_used,
                'total': disk_total,
                'percent': disk_percent,
                'free': disk.free / (1024**3)
            },
            'ram': {
                'used': ram_used,
                'total': ram_total,
                'percent': ram_percent
            },
            'cpu': {
                'percent': cpu_percent
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
