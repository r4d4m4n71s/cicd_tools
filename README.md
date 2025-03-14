<div align="center">

# 🚀 CICD Tools

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge)](https://github.com/psf/black)

**A flexible framework for development tasks including project creation, testing, building, and deployment.**

</div>

---

## ✨ Features

- 🔄 **Dynamic Menus** - Adapt based on project type with enhanced visual styling and icons
- 📋 **Template-based** - Project creation and updates using Copier
- 🧩 **Multiple Project Types** - Different capabilities for different needs
- 🔗 **GitHub Integration** - Workflows for CI/CD
- 🛠️ **Environment Management** - Comprehensive virtual environment handling
- 📊 **Progress Tracking** - Visual feedback for long-running operations (enabled by default)
- 📝 **Example Modules** - Ready-to-use sample modules with logging capabilities
- ⚙️ **Centralized Configuration** - Flexible configuration via .app_cache/config.yaml

---

## 📦 Installation

### Standard Installation

```bash
pip install cicd_tools
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cicd_tools.git
cd cicd_tools

# Install in development mode with development dependencies
pip install -e ".[dev]"
```

---

## 📚 Detailed Usage Guide

### 🆕 Creating a New Project

The `create` command allows you to create new projects from templates.

```bash
cicd_tools create
```

<details>
<summary><b>Step-by-Step Example</b></summary>

1. Run the create command:
   ```bash
   cicd_tools create
   ```

2. Select "Create Project" from the menu.

3. Choose a template type:
   ```
   ? Select a template: (Use arrow keys)
    > simple_project
      development_project
      github_project
   ```

4. Enter project details when prompted:
   ```
   ? Enter project name: my-project
   ? Short description of the project: A Python utility for awesome things
   ? Author name: Your Name
   ? Author email: your.email@example.com
   ? Python version: 3.8
   ? License: MIT
   ```

5. The project will be created with the selected template:
   ```
   Project created successfully at /path/to/my-project
   ```

6. The created project includes:
   - Basic project structure
   - Example module with logging capabilities
   - Configuration file in .app_cache/config.yaml
</details>

### 🔧 Working with an Existing Project

The `app` command allows you to work with existing projects.

```bash
cicd_tools app
```

<details>
<summary><b>Step-by-Step Example</b></summary>

1. Navigate to your project directory:
   ```bash
   cd my-project
   ```

2. Run the app command:
   ```bash
   cicd_tools app
   ```

3. The tool will detect your project type and display appropriate options with enhanced styling:
   ```
   App Menu - my-project
   
   ? Select an action: (Use arrow keys)
    > 🔧 Manage Environment - Manage the project environment
      📥 Install - Install the project
      🧪 Test - Run tests
      🏗️ Build - Build the project
      🧹 Clean - Clean build artifacts
      ℹ️ Help - Show help for project operations
      ↩️ Back/Exit
   ```

4. Select an action to perform.
</details>

### 🌐 Environment Management

CICD Tools provides comprehensive environment management capabilities.

<details>
<summary><b>Step-by-Step Example</b></summary>

1. From the app menu, select "Manage Environment":
   ```
   ? Select an action: 🔧 Manage Environment - Manage the project environment
   ```

2. Choose an environment management action:
   ```
   Environment Management
   
   ? Select an action: (Use arrow keys)
    > 🔄 Recreate Environment - Recreate the virtual environment
      🗑️ Delete Environment - Delete the virtual environment
      ➕ Create New Environment - Create a new virtual environment
      ↩️ Back/Exit
   ```

3. If creating a new environment, enter a name:
   ```
   ? Enter environment name: my-env
   ```

4. The environment will be created and the project will be installed with visual progress tracking:
   ```
   Creating environment... [========================================] 100%
   Installing dependencies... [====================================] 100%
   Environment created successfully
   ```
</details>

### ⚙️ Configuration System

CICD Tools uses a centralized configuration system located in `.app_cache/config.yaml`.

<details>
<summary><b>Configuration Options</b></summary>

- **Environment Settings**
  ```yaml
  environment:
    capture_output: true  # Enable progress bars for long-running operations (default: true)
  ```

- **Logging Configuration**
  ```yaml
  logging:
    default:
      level: INFO
      handlers:
        - type: console
          format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        - type: file
          filename: "app.log"
          format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
          max_bytes: 10485760  # 10MB
          backup_count: 3
  ```

- **Menu Styling**
  ```yaml
  styling:
    colors:
      primary: "#007BFF"
      secondary: "#6C757D"
      success: "#28A745"
      warning: "#FFC107"
      error: "#DC3545"
  ```

You can customize these settings to match your preferences and requirements.
</details>

### 📝 Example Module

Each project template includes a ready-to-use sample module with logging capabilities.

<details>
<summary><b>Using the Example Module</b></summary>

The example module is located in your project structure and includes:

- `__init__.py` - Module initialization with logger setup
- `main.py` - Example functionality with proper logging

Example usage:

```python
from my_project.sample_module import main

# Call a function from the example module
result = main.process_data([1, 2, 3])
print(result)
```

The example module automatically sets up logging based on your configuration in `.app_cache/config.yaml`.
</details>

---

## 📋 Project Types

### 🔹 Simple Project

Basic project with minimal functionality:

<details>
<summary><b>Available Operations</b></summary>

- **📥 Install**: Install the project
  ```bash
  # From the app menu, select "Install"
  # The project will be installed in the current environment
  ```

- **🧪 Test**: Run tests
  ```bash
  # From the app menu, select "Test"
  # Tests will be run using unittest discover
  ```

- **🏗️ Build**: Build the project
  ```bash
  # From the app menu, select "Build"
  # The project will be built using setup.py build
  ```

- **🧹 Clean**: Clean build artifacts
  ```bash
  # From the app menu, select "Clean"
  # Build artifacts will be removed
  ```
</details>

### 🔹 Development Project

Advanced project with development capabilities:

<details>
<summary><b>Available Operations</b></summary>

- **📥 Install**: Install the project with development dependencies
  ```bash
  # From the app menu, select "Install"
  # The project will be installed with development dependencies
  ```

- **🧪 Test**: Run tests with options
  ```bash
  # From the app menu, select "Test"
  # Choose a test option:
  # - All tests
  # - Failed tests only
  # - With coverage
  ```

- **🔄 Prehook**: Configure pre-commit hooks
  ```bash
  # From the app menu, select "Prehook"
  # Choose an action:
  # - on: Enable pre-commit hooks
  # - off: Disable pre-commit hooks
  ```

- **📦 Release**: Create a release
  ```bash
  # From the app menu, select "Release"
  # Choose a release type:
  # - beta: Create a beta release
  # - prod: Create a production release
  ```

- **🚀 Deploy**: Deploy the project
  ```bash
  # From the app menu, select "Deploy"
  # Choose a deployment target:
  # - test: Deploy to TestPyPI
  # - prod: Deploy to PyPI
  ```
</details>

### 🔹 GitHub Project

Project with GitHub integration:

<details>
<summary><b>Available Operations</b></summary>

- **📥 Clone Repository**: Clone a GitHub repository
  ```bash
  # From the app menu, select "Clone Repository"
  # Enter the repository URL
  # Choose a template to apply (optional)
  ```

- **⬇️ Pull Changes**: Pull changes from the remote repository
  ```bash
  # From the app menu, select "Pull Changes"
  # Changes will be pulled from the remote repository
  ```

- **⬆️ Push Changes**: Push changes to the remote repository
  ```bash
  # From the app menu, select "Push Changes"
  # Enter a commit message
  # Changes will be committed and pushed to the remote repository
  ```
</details>

---

## 📝 Template System

CICD Tools uses Copier for template-based project creation and updates.

### Available Templates

<details>
<summary><b>🔹 Simple Project</b></summary>

- **Features**: 
  - Basic project structure
  - setup.py
  - Tests
  - Sample module with logging
  - Configuration in .app_cache/config.yaml
- **Use case**: Simple utility libraries, scripts
</details>

<details>
<summary><b>🔹 Development Project</b></summary>

- **Features**: 
  - pyproject.toml
  - Pre-commit hooks
  - GitHub Actions workflows
  - Sample module with logging
  - Configuration in .app_cache/config.yaml
- **Use case**: Libraries with CI/CD requirements, packages for distribution
</details>

<details>
<summary><b>🔹 GitHub Project</b></summary>

- **Features**: 
  - GitHub-specific files (issue templates, PR templates)
  - GitHub Actions
  - Sample module with logging
  - Configuration in .app_cache/config.yaml
- **Use case**: Open source projects hosted on GitHub
</details>

### Creating Custom Templates

<details>
<summary><b>Step-by-Step Guide</b></summary>

1. Create a directory for your template in the `project_templates` directory.
2. Create a `copier.yaml` file with template configuration.
3. Add template files with `.jinja` extension for templating.
4. Include a sample module with logging capabilities.
5. Add a default configuration file template.

Example `copier.yaml`:
```yaml
# Custom Template Configuration
_version: "0.1.0"
_description: "My custom template"

# Project Information
project_name:
  type: str
  help: "Name of the project"
  default: "custom-project"
```
</details>

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <sub>Built with ❤️ by the CICD Tools Team</sub>
</div>