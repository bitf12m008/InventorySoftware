# Project Setup & Usage

## 1. Running the Project

1. Open a terminal and navigate to the project folder.
2. Activate the virtual environment:

```bash
source venv/bin/activate   # Linux/macOS
# OR
venv\Scripts\activate      # Windows
```

3. Run the main application:

```bash
python -m app.main
```

---

## 2. Building a Windows Installer (GUI, One-Click)

This app stores its database, backups, and receipts in `%LOCALAPPDATA%\\KFCInventoryApp`, so it can be installed under Program Files without write-permission errors. The installer still defaults to `%LOCALAPPDATA%\\KFCInventoryApp` to avoid requiring admin privileges. The installer now creates a fresh, empty database on first run.

### Prerequisites (Windows)

1. Activate your venv and install PyInstaller:

```bash
pip install pyinstaller
```

2. Install Inno Setup and ensure `ISCC.exe` is in your `PATH`.

### Build

```powershell
.\scripts\build_installer.ps1
```

Outputs:
1. PyInstaller build folder: `dist\KFCInventoryApp`
2. Installer EXE: `output\KFCInventoryAppSetup.exe`

### App Icon (Optional)

Put a Windows `.ico` file at `app\assets\app.ico`. The build script and installer will use it automatically.

---

## 3. `requirements.txt`

The `requirements.txt` file lists all external Python packages your project depends on, along with optional version specifications. It ensures consistency across environments and simplifies setup.

### **Key Purposes**

1. **Dependency Management**
   Specifies which packages need to be installed, so your project runs consistently for all users.

2. **Reproducibility**
   By specifying exact versions (e.g., `requests==2.31.0`), it ensures everyone uses the same packages, reducing bugs caused by version differences.

3. **Easy Installation**
   Install all dependencies in one command:

```bash
pip install -r requirements.txt
```

4. **Deployment**
   Useful for deploying the project to servers or cloud platforms, automatically installing all required packages.

### **Tip**

Keep `requirements.txt` updated whenever you add new packages to your project to avoid missing dependencies.

---

## 4. Generating `requirements.txt` Automatically

If you add new packages or want to capture all dependencies used in your project:

1. Make sure your virtual environment is activated.
2. Run the following command in the project root:

```bash
pip freeze > requirements.txt
```

* This command lists all installed packages in the environment and writes them to `requirements.txt`.
* For a cleaner file containing only packages your code actually imports, you can use [`pipreqs`](https://github.com/bndr/pipreqs):

```bash
pip install pipreqs
pipreqs /path/to/your/project --force
```

* `--force` overwrites any existing `requirements.txt`.

This ensures new developers or deployment environments can install exactly the packages your project needs.
