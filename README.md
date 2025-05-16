<div align="center">

# 🚀 CICD Tools

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/Linting-Ruff-red?style=for-the-badge)](https://github.com/astral-sh/ruff)

**A flexible framework for development tasks including project creation, testing, building, and deployment.**

</div>

## 🚀 Quick Start

```bash
# Install the package
pip install cicd_tools

# Create a new project (using long option)
cicd_tools --create
# or with short option
cicd_tools -c

# Restore project configuration (using long option)
cicd_tools --restore
# or with short option
cicd_tools -r

# Display version information
cicd_tools -v
# or
cicd_tools --version

# Specify working directory (using long option)
cicd_tools --directory /path/to/project
# or with short option
cicd_tools -d /path/to/project

# Display help information
cicd_tools -h
# or 
cicd_tools --help
```

> **Note**: Without any arguments, the tool automatically detects if you're in a project directory and shows the appropriate menu.

### Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Detailed Usage Guide](#-detailed-usage-guide)
- [Project Types](#-project-types)
- [Template System](#-template-system)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

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

The `--create` option allows you to create new projects from templates.

```bash
cicd_tools --create
# or using the short form
cicd_tools -c
```

<details>
<summary><b>Step-by-Step Example</b></summary>

1. Run the create command:
   ```bash
   cicd_tools --create
   # or
   cicd_tools -c
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

When you run CICD Tools without any options in a project directory, it automatically detects the project type and shows the appropriate menu.

```bash
# Simply run without options in a project directory
cicd_tools
```

<details>
<summary><b>Step-by-Step Example</b></summary>

1. Navigate to your project directory:
   ```bash
   cd my-project
   ```

2. Simply run the tool with no options:
   ```bash
   cicd_tools
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

#### Restoring Configuration

The `--restore` option allows you to reset a project's configuration to defaults allowing to choose a new template:

```bash
cicd_tools --restore
# or using the short form
cicd_tools -r
```

This completely clears any existing configuration and applies fresh defaults, which is useful when:
- You want to start with a clean configuration
- Your configuration file has become corrupted
- You've made experimental changes and want to revert to defaults

<details>
<summary><b>Configuration Options</b></summary>

- **Environment Settings**
  ```yaml
  console:
    stack_trace: False  # Disable progress bars for cmd trace log (default: false)
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

### Template Description System

Templates now include rich descriptions to help users choose the appropriate template:

- Each template has a name and description displayed in selection menus
- Descriptions are defined in the `_description` field in each template's `copier.yaml` file
- When listing or selecting templates, you'll see both the name and description:
  ```
  ? Select a template: (Use arrow keys)
   > simple_project - Creates a project with basic file structure
     development_project - Project template with CI/CD workflows, testing, github enablement
  ```

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

## 🏗️ Architecture

The CICD Tools package follows a modular design pattern for extensibility and maintainability:

```mermaid
graph TD
    CLI[CLI Module] --> CreateMenu[Create Menu]
    CLI --> AppMenu[App Menu]
    CreateMenu --> TemplateManager[Template Manager]
    AppMenu --> ProjectDetector[Project Type Detector]
    ProjectDetector --> BaseProject[Base Project]
    ProjectDetector --> DevProject[Development Project]
    ProjectDetector --> SimpleProject[Simple Project]
    BaseProject --> ConfigManager[Config Manager]
    DevProject --> GitMixin[Git Mixin]
    DevProject --> VersionMixin[Version Manager Mixin]
    TemplateManager --> Templates[Project Templates]
```

### Key Components

- **CLI Module**: Entry point handling command-line arguments and routing to appropriate menus
- **Create Menu**: Handles the project creation workflow
- **App Menu**: Provides operations for existing projects
- **Template Manager**: Manages template rendering using Copier
- **Project Type Detector**: Identifies project type based on configuration and structure
- **Base Project & Mixins**: Provides functionality using a composable design pattern
- **Config Manager**: Centralized configuration handling

## ⚠️ Troubleshooting

Common issues and their solutions:

### Environment Detection Failures

**Problem**: Environment is not detected properly or virtual environment operations fail.

**Solutions**:
- Ensure Python (3.8+) is correctly installed and in your PATH
- Check for permissions to create directories in the project folder
- Try running with administrator/elevated privileges
- For virtual environment issues, ensure you have the venv module installed

### Template Rendering Problems

**Problem**: Project creation fails during template rendering.

**Solutions**:
- Verify you have the latest version of CICD Tools
- Check that all input values match the expected format
- For custom templates, validate your copier.yaml file syntax
- Try with a simpler template first to isolate the issue

### Pre-commit Hook Failures

**Problem**: Pre-commit hooks fail or don't run as expected.

**Solutions**:
- Run `cicd_tools app`, select Prehook → run to see specific failures
- Ensure you have the dev dependencies installed with `pip install -e ".[dev]"`
- Check that your files are properly formatted according to the hooks
- For custom hooks, verify your .pre-commit-config.yaml file

### Release and Deployment Issues

**Problem**: Release creation or deployment to PyPI fails.

**Solutions**:
- Ensure you have a properly configured .pypirc file
- Verify you have permissions to publish to the specified PyPI repository
- Check that your version is incremented and follows semantic versioning
- Validate package structure with `twine check dist/*` before deploying

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
