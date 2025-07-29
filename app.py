import os
import uuid
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'html', 'htm'}
USERS_FILE = 'users.json'

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {"users": []}

def save_users(users_data):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def get_user_by_username(username):
    """Get user data by username"""
    users_data = load_users()
    for user in users_data["users"]:
        if user["username"] == username:
            return user
    return None

def get_file_owner(filename):
    """Get the owner of a specific file"""
    users_data = load_users()
    for user in users_data["users"]:
        for file_info in user["files"]:
            if file_info["stored_name"] == filename:
                return user["username"]
    return None

def user_owns_file(username, filename):
    """Check if a user owns a specific file"""
    return get_file_owner(filename) == username

# Make get_user_by_username available in templates
app.jinja_env.globals.update(get_user_by_username=get_user_by_username)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'username' not in session:
        return redirect(url_for('login'))
        
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Only HTML files are allowed (.html, .htm)')
            return redirect(url_for('index'))
        
        # Generate unique filename to avoid conflicts
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{original_filename}"
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Update user's file list
        users_data = load_users()
        for user in users_data["users"]:
            if user["username"] == session["username"]:
                user["files"].append({
                    "original_name": original_filename,
                    "stored_name": filename
                })
                break
        save_users(users_data)
        
        # Generate access URL
        access_url = url_for('serve_file', filename=filename, _external=True)
        
        return render_template('success.html', 
                             filename=original_filename, 
                             access_url=access_url)
    
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        flash('An error occurred during upload. Please try again.')
        return redirect(url_for('index'))

@app.route('/view/<filename>')
def serve_file(filename):
    """Serve uploaded HTML files - publicly accessible"""
    try:
        # First check if the file physically exists
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return render_template('error.html', 
                                error_message="File not found"), 404
        
        # Verify the file exists in our system by checking if any user has uploaded it
        users_data = load_users()
        file_exists = False
        file_owner = None
        
        for user in users_data["users"]:
            if any(f['stored_name'] == filename for f in user['files']):
                file_exists = True
                file_owner = user['username']
                break
        
        if not file_exists:
            return render_template('error.html', 
                                error_message="File not found or has been removed."), 404
        
        # Add security headers to prevent modification
        response = send_from_directory(UPLOAD_FOLDER, filename)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-File-Owner'] = file_owner  # Custom header to identify owner
        
        return response
    except FileNotFoundError:
        return render_template('error.html', 
                             error_message="File not found"), 404
    except Exception as e:
        app.logger.error(f"Serve file error: {str(e)}")
        return render_template('error.html', 
                             error_message="An error occurred while loading the file"), 500

@app.route('/create', methods=['GET'])
def create_page():
    """Page creation interface"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('create.html')

@app.route('/save-generated', methods=['POST'])
def save_generated():
    """Save generated HTML file"""
    if 'username' not in session:
        return redirect(url_for('login'))
        
    try:
        html_content = request.form.get('html_content')
        filename = request.form.get('filename', '').strip()
        
        if not html_content:
            flash('No HTML content provided')
            return redirect(url_for('create_page'))
            
        if not filename:
            filename = 'generated.html'
        elif not filename.endswith('.html'):
            filename += '.html'
            
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        stored_filename = f"{unique_id}_{secure_filename(filename)}"
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, stored_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Update user's file list
        users_data = load_users()
        for user in users_data["users"]:
            if user["username"] == session["username"]:
                user["files"].append({
                    "original_name": filename,
                    "stored_name": stored_filename
                })
                break
        save_users(users_data)
        
        # Generate access URL
        access_url = url_for('serve_file', filename=stored_filename, _external=True)
        return jsonify({
            'success': True, 
            'url': access_url,
            'message': 'File saved successfully!'
        })
        
    except Exception as e:
        app.logger.error(f"Save generated file error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while saving the file'
        })

@app.route('/delete-file', methods=['POST'])
def delete_file():
    """Delete a user's file"""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    try:
        stored_name = request.form.get('filename')
        if not stored_name:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400
            
        # Check if the file belongs to the current user
        users_data = load_users()
        user_found = False
        file_found = False
        
        for user in users_data["users"]:
            if user["username"] == session["username"]:
                user_found = True
                # Find and remove the file entry
                user["files"] = [f for f in user["files"] if f["stored_name"] != stored_name]
                file_found = True
                break
                
        if not user_found:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        if not file_found:
            return jsonify({'success': False, 'error': 'File not found'}), 404
            
        # Delete the actual file
        filepath = os.path.join(UPLOAD_FOLDER, stored_name)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        # Save updated user data
        save_users(users_data)
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
        
    except Exception as e:
        app.logger.error(f"Delete file error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while deleting the file'
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File is too large. Maximum size is 16MB.')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', 
                         error_message="Internal server error"), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('signup'))
        
        users_data = load_users()
        
        # Check if username already exists
        if get_user_by_username(username):
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = {
            "username": username,
            "password": generate_password_hash(password),
            "files": []
        }
        
        users_data["users"].append(new_user)
        save_users(users_data)
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/files')
def list_files():
    """List all publicly available files - for debugging"""
    users_data = load_users()
    all_files = []
    
    for user in users_data["users"]:
        for file_info in user["files"]:
            all_files.append({
                'original_name': file_info['original_name'],
                'stored_name': file_info['stored_name'],
                'url': url_for('serve_file', filename=file_info['stored_name'], _external=True),
                'owner': user['username']
            })
    
    return jsonify(all_files)

@app.route('/edit/<filename>')
def edit_file(filename):
    """Edit HTML file - only accessible by file owner"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Check if user owns this file
    if not user_owns_file(session['username'], filename):
        return render_template('error.html', 
                             error_message="Access denied. You can only edit files you created."), 403
    
    # Check if file exists
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return render_template('error.html', 
                             error_message="File not found"), 404
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get original filename
        users_data = load_users()
        original_name = filename
        for user in users_data["users"]:
            if user["username"] == session["username"]:
                for file_info in user["files"]:
                    if file_info["stored_name"] == filename:
                        original_name = file_info["original_name"]
                        break
                break
        
        return render_template('edit.html', 
                             filename=filename,
                             original_name=original_name,
                             content=content)
    
    except Exception as e:
        app.logger.error(f"Edit file error: {str(e)}")
        return render_template('error.html', 
                             error_message="Error reading file"), 500

@app.route('/update-file', methods=['POST'])
def update_file():
    """Update HTML file content - only accessible by file owner"""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        filename = request.form.get('filename')
        new_content = request.form.get('content')
        
        if not filename or not new_content:
            return jsonify({'success': False, 'error': 'Missing filename or content'}), 400
        
        # Check if user owns this file
        if not user_owns_file(session['username'], filename):
            return jsonify({'success': False, 'error': 'Access denied. You can only edit files you created.'}), 403
        
        # Update file content
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Create backup before updating
        backup_path = filepath + '.backup'
        if os.path.exists(filepath):
            import shutil
            shutil.copy2(filepath, backup_path)
        
        # Write new content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Remove backup if write was successful
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        return jsonify({
            'success': True, 
            'message': 'File updated successfully!',
            'url': url_for('serve_file', filename=filename, _external=True)
        })
        
    except Exception as e:
        app.logger.error(f"Update file error: {str(e)}")
        # Restore from backup if it exists
        backup_path = os.path.join(UPLOAD_FOLDER, filename + '.backup')
        if os.path.exists(backup_path):
            import shutil
            shutil.move(backup_path, os.path.join(UPLOAD_FOLDER, filename))
        
        return jsonify({
            'success': False,
            'error': 'An error occurred while updating the file'
        }), 500

@app.route('/file-info/<filename>')
def file_info(filename):
    """Get file information including owner - for security checks"""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    owner = get_file_owner(filename)
    if not owner:
        return jsonify({'error': 'File not found'}), 404
    
    can_edit = user_owns_file(session['username'], filename)
    
    # Get file details
    users_data = load_users()
    original_name = filename
    for user in users_data["users"]:
        for file_info in user["files"]:
            if file_info["stored_name"] == filename:
                original_name = file_info["original_name"]
                break
    
    return jsonify({
        'filename': filename,
        'original_name': original_name,
        'owner': owner,
        'can_edit': can_edit,
        'current_user': session['username'],
        'view_url': url_for('serve_file', filename=filename, _external=True),
        'edit_url': url_for('edit_file', filename=filename, _external=True) if can_edit else None
    })





if __name__ == '__main__':
    app.run(debug=True)