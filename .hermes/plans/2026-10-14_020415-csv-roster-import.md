# CSV Roster Import Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a feature to the admin dashboard allowing the user to upload a CSV file to populate the `roster` table in the database.

**Architecture:** 
- A new admin route `/admin/import-roster` will handle both the GET (upload form) and POST (processing the file) requests.
- The server will parse the uploaded CSV file using the `csv` module and insert valid rows into the `roster` table via `database.add_roster_entry`.
- The process will include basic validation (checking for the correct number of columns) and return a summary of imported vs skipped rows.

**Tech Stack:** Flask, SQLite (via `database.py`), Python `csv` module.

---

## Tasks

### Task 1: Create the Import Roster HTML Template

**Objective:** Create a simple upload form for the admin to select a CSV file.

**Files:**
- Create: `/opt/data/Bowling_Poker/templates/import_roster.html`

**Step 1: Create the HTML file**
```html
{% extends "admin.html" %}
{% block content %}
<h2>Import Weekly Roster</h2>
<form method="POST" enctype="multipart/form-data">
    <div class="form-group">
        <label for="csv_file">Select CSV File:</label>
        <input type="file" name="csv_file" id="csv_file" accept=".csv" required>
    </div>
    <button type="submit" class="btn btn-primary">Upload and Import</button>
</form>
{% endblock %}
```

**Step 2: Commit**
```bash
git add templates/import_roster.html
git commit -m "feat: add import roster upload template"
```

### Task 2: Implement the `/admin/import-roster` Route

**Objective:** Create the backend logic to handle CSV upload and database insertion.

**Files:**
- Modify: `/opt/data/Bowling_Poker/app.py`

**Step 1: Add the route implementation**
Add the following route to `app.py`:

```python
import csv
from io import TextIOWrapper

@app.route("/admin/import-roster", methods=["GET", "POST"])
@login_required
def import_roster():
    if request.method == "POST":
        if 'csv_file' not in request.files:
            flash("No file part", "error")
            return redirect(url_for("import_roster"))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(url_for("import_roster"))

        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV from stream
                stream = TextIOWrapper(file.stream, encoding='utf-8')
                reader = csv.reader(stream)
                header = next(reader, None) # Skip header
                
                imported_count = 0
                skipped_count = 0
                
                for row in reader:
                    if len(row) >= 6:
                        # Expected: date, p1, p2, p3, p4, off
                        database.add_roster_entry(row[0], row[1], row[2], row[3], row[4], row[5])
                        imported_count += 1
                    else:
                        skipped_count += 1
                
                flash(f"Import complete: {imported_count} rows imported, {skipped_count} skipped.", "success")
            except Exception as e:
                flash(f"Error processing CSV: {str(e)}", "error")
            
            return redirect(url_for("admin_dashboard"))
        
        flash("Invalid file type. Please upload a .csv file.", "error")
        return redirect(url_for("import_roster"))

    return render_template("import_roster.html")
```

**Step 2: Commit**
```bash
git add app.py
git commit -m "feat: implement CSV import logic"
```

### Task 3: Update Admin Dashboard Navigation

**Objective:** Add a link to the import tool on the admin home page.

**Files:**
- Modify: `/opt/data/Bowling_Poker/templates/admin.html`

**Step 1: Add the link to the navigation or main menu**
Add a link to `/admin/import-roster` (e.g., in the button group or list of admin actions).

**Step 2: Commit**
```bash
git add templates/admin.html
git commit -m "feat: add import roster link to admin dashboard"
```

### Task 4: Verification and Testing

**Objective:** Ensure the import works as expected.

**Step 1: Create a test CSV file**
Create `test_import.csv` with a header and 2-3 rows of data.

**Step 2: Perform the upload**
1. Navigate to `/admin/import-roster`.
2. Upload `test_import.csv`.
3. Verify the flash message shows the correct count.

**Step 3: Verify database records**
Check the `/admin/edit-roster` page or run a query to ensure the new rows exist in the `roster` table.

**Step 4: Test error handling**
1. Upload a non-CSV file.
2. Upload a CSV with missing columns (should be skipped).
3. Verify error flash messages appear.

---

## Risks & Tradeoffs
- **Duplicate Data**: This implementation currently allows duplicate rows to be imported. If the user uploads the same file twice, the roster will have duplicates. 
  - *Future mitigation*: Check for existing date/player combinations before inserting.
- **Memory**: For extremely large files, reading line-by-line with `csv.reader` is efficient, but the `TextIOWrapper` is necessary to handle the binary stream from Flask.
