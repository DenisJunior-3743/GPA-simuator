from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from app import vault_manager
from app.gpa_calculator import compute_gpa
from app.simulator import generate_grade_combinations
from app.constants import GRADE_POINTS

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-me'

@app.route('/')
def index():
    user = None
    if session.get('user_id'):
        user = {'id': session.get('user_id'), 'username': session.get('username')}
    return render_template('dashboard.html', user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        # Very small stub: look up user by username in vault db
        conn = vault_manager.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, full_name FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()
        if row:
            session['user_id'] = row['id']
            session['username'] = row['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='User not found')
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name') or None
        email = request.form.get('email') or None
        program = request.form.get('program') or None
        user = vault_manager.register_user(username, password, full_name, email, program)
        if user:
            # auto-login after register
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/option3/summary')
def option3_summary():
    if not session.get('user_id'):
        return render_template('option3_summary.html', saved=None)
    user_id = session.get('user_id')
    semesters = vault_manager.get_semesters_for_user(user_id)
    summary = vault_manager.get_semesters_summary(user_id)
    total_cu = vault_manager.get_total_cu_completed(user_id)
    last_sem = vault_manager.get_last_complete_semester_data(user_id)
    return render_template('option3_summary.html', saved=semesters, summary=summary, total_cu=total_cu, last_sem=last_sem)


@app.route('/option3')
def option3():
    """Manual CGPA calculation page (all semesters)"""
    user = None
    if session.get('user_id'):
        user = {'id': session.get('user_id'), 'username': session.get('username')}
    return render_template('option3.html', user=user)


@app.route('/option3/load', methods=['GET'])
def option3_load():
    """API endpoint: calculate CGPA from saved semesters for the logged-in user."""
    if not session.get('user_id'):
        return jsonify({'error': 'guest', 'message': 'Please log in to load saved semesters.'}), 401
    user_id = session.get('user_id')
    semesters = vault_manager.get_semesters_for_user(user_id)
    if not semesters:
        return jsonify({'error': 'no_data', 'message': 'No saved semesters found.'}), 404
    wt = 0.0
    cu = 0
    for s in semesters:
        # rows may be sqlite3.Row or dict
        g = s['gpa'] if isinstance(s, dict) or 'gpa' in s else s['gpa']
        c = s['total_cu'] if isinstance(s, dict) or 'total_cu' in s else s['total_cu']
        try:
            wt += float(g) * int(c)
            cu += int(c)
        except Exception:
            continue
    cgpa = round(wt / cu, 2) if cu > 0 else 0.0
    # Normalize semesters into plain dicts for JSON
    sem_list = []
    for s in semesters:
        try:
            sem_list.append({
                'academic_year': s.get('academic_year') if hasattr(s, 'get') else s['academic_year'],
                'semester_num': s.get('semester_num') if hasattr(s, 'get') else s['semester_num'],
                'gpa': float(s.get('gpa')) if hasattr(s, 'get') else float(s['gpa']),
                'total_cu': int(s.get('total_cu')) if hasattr(s, 'get') else int(s['total_cu'])
            })
        except Exception:
            continue
    return jsonify({'cgpa': cgpa, 'total_cu': cu, 'count': len(semesters), 'semesters': sem_list})


@app.route('/onboarding', methods=['GET','POST'])
def onboarding():
    if request.method == 'POST':
        # For now, just acknowledge and redirect to dashboard
        return redirect(url_for('index'))
    return render_template('onboarding.html')

# Option 6-10, save-semester, init-vault routes
@app.route('/option6')
def option6():
    return render_template('option6.html')

@app.route('/option7')
def option7():
    return render_template('option7.html')

@app.route('/option8')
def option8():
    return render_template('option8.html')

@app.route('/option9')
def option9():
    return render_template('option9.html')

@app.route('/option10')
def option10():
    return render_template('option10.html')

@app.route('/save-semester')
def save_semester():
    """Save semester - requires login"""
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('save-semester.html')

@app.route('/history')
def history():
    """View academic history - requires login"""
    if not session.get('user_id'):
        return redirect('/login')
    user_id = session.get('user_id')
    semesters = vault_manager.get_semesters_for_user(user_id)
    summary = vault_manager.get_semesters_summary(user_id)
    total_cu = vault_manager.get_total_cu_completed(user_id)
    user = {'id': user_id, 'username': session.get('username')}
    return render_template('history.html', semesters=semesters, summary=summary, total_cu=total_cu, user=user)

@app.route('/init-vault')
def init_vault():
    return render_template('init-vault.html')


@app.route('/exit')
def exit_app():
    """Exit route: clear session and present a goodbye page."""
    session.clear()
    return render_template('exit.html')

@app.route('/option2')
def option2():
    # Update CGPA page (placeholder)
    return render_template('option2.html')


@app.route('/option1', methods=['GET'])
def option1():
    """Quick GPA page (GET). POSTs should use `/api/option1` for AJAX."""
    return render_template('option1.html')


@app.route('/option5')
def option5():
    """Simulate grade combinations page."""
    return render_template('option5.html')


@app.route('/api/option1', methods=['POST'])
def api_option1():
    """AJAX API: compute GPA and return JSON. Same validation as `/option1` route."""
    try:
        num = int(request.form.get('num_courses', 0))
    except Exception:
        return jsonify({'error': 'Invalid number of courses'}), 400
    courses = []
    for i in range(1, num + 1):
        grade = request.form.get(f'grade_{i}')
        cu = request.form.get(f'cu_{i}')
        if not grade or not cu:
            continue
        try:
            cu_i = int(cu)
        except Exception:
            return jsonify({'error': f'Invalid credit units for course {i}'}), 400
        if cu_i < 1 or cu_i > 5:
            return jsonify({'error': f'Credit units for course {i} must be between 1 and 5'}), 400
        grade_norm = grade.strip().upper()
        if grade_norm not in GRADE_POINTS:
            return jsonify({'error': f'Unknown grade for course {i}: {grade}'}), 400
        courses.append((cu_i, grade_norm))
    try:
        result = compute_gpa(courses)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'result': result, 'courses': len(courses)})


@app.route('/api/option2', methods=['POST'])
def api_option2():
    """Preview CGPA after adding a new semester for logged-in users.

    Expects form fields: `new_gpa` (float) and `new_cu` (int).
    """
    # Accept two flows:
    # 1) logged-in + use_vault=true -> infer old CGPA and old CU from vault
    # 2) guest or manual -> caller provides old_cgpa and old_cu explicitly (or per-semester list summed client-side)
    try:
        new_gpa = float(request.form.get('new_gpa', 0))
        new_cu = int(request.form.get('new_cu', 0))
    except Exception:
        return jsonify({'error': 'Invalid new_gpa or new_cu'}), 400
    if new_cu < 1 or new_cu > 200:
        return jsonify({'error': 'new_cu must be positive and reasonable'}), 400

    user_id = session.get('user_id') if session.get('user_id') else None

    # Determine old_cgpa and old_cu
    use_vault = request.form.get('use_vault', '').lower() in ('1', 'true', 'yes', 'on')
    old_cgpa = None
    old_cu = None
    if use_vault and user_id:
        try:
            defaults = vault_manager.get_last_complete_semester_data(user_id)
            if defaults:
                old_cgpa = defaults.get('cgpa') or defaults.get('gpa')
                old_cu = vault_manager.get_total_cu_completed(user_id)
            else:
                # no saved data
                return jsonify({'error': 'No saved semesters found in vault to use as defaults.'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        # Expect explicit old_cgpa and old_cu from form (guest/manual flow)
        try:
            old_cgpa = float(request.form.get('old_cgpa', None))
            old_cu = int(request.form.get('old_cu', None))
        except Exception:
            return jsonify({'error': 'Provide old_cgpa and old_cu for guest/manual mode'}), 400

    # Validate inputs
    from app.cgpa_calculator import update_cgpa
    from app.constants import DECIMAL_PLACES
    if old_cgpa is None or old_cu is None:
        return jsonify({'error': 'Old CGPA and CU could not be determined'}), 400
    if old_cgpa < 0 or old_cgpa > 5.0:
        return jsonify({'error': 'old_cgpa out of range 0.0 - 5.0'}), 400
    if old_cu < 0:
        return jsonify({'error': 'old_cu must be non-negative'}), 400

    try:
        new_cgpa = update_cgpa(old_cgpa, old_cu, new_gpa, new_cu)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'new_cgpa': new_cgpa, 'old_cgpa': old_cgpa, 'old_cu': old_cu, 'new_gpa': new_gpa, 'new_cu': new_cu})


@app.route('/api/vault_defaults', methods=['GET'])
def api_vault_defaults():
    """Return smart defaults (old_cgpa, old_cu, last_semester) for logged-in user."""
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session.get('user_id')
    try:
        last = vault_manager.get_last_complete_semester_data(user_id)
        old_cgpa = None
        old_cu = None
        if last:
            old_cgpa = last.get('cgpa') or last.get('gpa')
            old_cu = vault_manager.get_total_cu_completed(user_id)
        return jsonify({'old_cgpa': old_cgpa, 'old_cu': old_cu, 'last_semester': last})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-semester', methods=['POST'])
def api_save_semester():
    """Save current semester to vault for logged-in users.

    Expects JSON: academic_year, semester_num, total_cu, gpa
    Returns: new_cgpa, semester_id
    """
    if not session.get('user_id'):
        return jsonify({'error': 'Please log in to save semesters.'}), 401
    
    user_id = session.get('user_id')
    
    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    
    try:
        academic_year = int(data.get('academic_year', 0))
        semester_num = int(data.get('semester_num', 0))
        total_cu = int(data.get('total_cu', 0))
        gpa = float(data.get('gpa', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input fields'}), 400
    
    # Validation
    if academic_year < 1 or academic_year > 5:
        return jsonify({'error': 'Academic year must be 1-5'}), 400
    if semester_num < 1 or semester_num > 2:
        return jsonify({'error': 'Semester must be 1 or 2'}), 400
    if total_cu < 1:
        return jsonify({'error': 'Total CU must be >= 1'}), 400
    if gpa < 0 or gpa > 5:
        return jsonify({'error': 'GPA must be 0-5'}), 400
    
    try:
        # Calculate new CGPA including this semester
        new_cgpa = vault_manager.calculate_current_cgpa_with_new_semester(user_id, gpa, total_cu)
        
        # Save semester with new CGPA
        sem_id = vault_manager.save_semester(user_id, academic_year, semester_num, total_cu, gpa, new_cgpa, courses=None)
        
        return jsonify({'success': True, 'semester_id': sem_id, 'new_cgpa': new_cgpa})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/option4')
def option4():
    # Required GPA page
    user = None
    if session.get('user_id'):
        user = {'id': session.get('user_id'), 'username': session.get('username')}
    return render_template('option4.html', user=user)

@app.route('/api/simulate-grades', methods=['POST'])
def simulate_grades():
    """Generate grade combinations for a target GPA."""
    try:
        data = request.get_json()
        num_courses = data.get('num_courses')
        cus = data.get('cus')
        target_gpa = data.get('target_gpa')
        
        # Validate inputs
        if not isinstance(num_courses, int) or num_courses < 1 or num_courses > 10:
            return jsonify({'error': 'num_courses must be between 1 and 10'}), 400
        
        if not isinstance(cus, list) or len(cus) != num_courses:
            return jsonify({'error': 'cus list must match num_courses'}), 400
        
        # Validate each CU
        for cu in cus:
            if not isinstance(cu, int) or cu < 1 or cu > 5:
                return jsonify({'error': 'Each CU must be between 1 and 5'}), 400
        
        if not isinstance(target_gpa, (int, float)) or target_gpa < 0 or target_gpa > 5:
            return jsonify({'error': 'target_gpa must be between 0 and 5'}), 400
        
        # Calculate achievable range
        min_gp = min(GRADE_POINTS.values())
        max_gp = max(GRADE_POINTS.values())
        total_cu = sum(cus)
        min_possible = sum(c * min_gp for c in cus) / total_cu
        max_possible = sum(c * max_gp for c in cus) / total_cu
        
        # Generate combinations
        results = generate_grade_combinations(num_courses, cus, target_gpa)
        
        return jsonify({
            'results': results,
            'min_possible': round(min_possible, 2),
            'max_possible': round(max_possible, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on localhost for offline usage
    app.run(host='127.0.0.1', port=5000, debug=True)
