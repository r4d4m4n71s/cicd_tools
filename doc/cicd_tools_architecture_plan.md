# CICD Tools Project - Updated Architecture Document

## 1. Project Overview

The cicd_tools project is a flexible framework for development tasks including project creation, testing, building, and deployment. It features:

- Dynamic menus that adapt based on project type with enhanced look and feel
- Template-based project creation and updates using Copier
- Support for multiple project types with different capabilities
- Comprehensive environment management
- Project-specific configuration management
- Example modules with built-in logging capabilities
- Configurable logging via centralized configuration in .app_cache

## 2. Project Structure

```
cicd_tools/
├── pyproject.toml
├── README.md
├── cicd_tools/
│   ├── __init__.py
│   ├── cli.py                   # Main entry point
│   ├── menus/                   # Menu system components
│   │   ├── __init__.py
│   │   ├── create_menu.py       # Project creation/update menu
│   │   ├── app_menu.py          # Project-specific operations menu
│   │   └── menu_utils.py        # Common menu utilities
│   ├── project_types/           # Project type implementations
│   │   ├── __init__.py
│   │   ├── base_project.py      # Abstract base class
│   │   ├── simple_project.py
│   │   ├── development_project.py
│   │   └── github_project.py
│   ├── templates/               # Template management
│   │   ├── __init__.py
│   │   ├── template_manager.py  # Copier integration
│   │   └── template_utils.py    # Template helpers
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── env_manager.py       # Environment management adapter
│       └── config_manager.py    # Project configuration
├── project_templates/           # Copier templates
│   ├── simple_project/
│   │   ├── sample_module/       # Example module template
│   │   │   ├── __init__.py.jinja
│   │   │   └── main.py.jinja
│   │   ├── .app_cache/          # Configuration directory
│   │   │   └── config.yaml.jinja
│   ├── development_project/
│   │   ├── sample_module/       # Example module template
│   │   │   ├── __init__.py.jinja
│   │   │   └── main.py.jinja
│   │   ├── .app_cache/          # Configuration directory
│   │   │   └── config.yaml.jinja
│   └── github_project/
│       ├── sample_module/       # Example module template
│       │   ├── __init__.py.jinja
│       │   └── main.py.jinja
│       ├── .app_cache/          # Configuration directory
│       │   └── config.yaml.jinja
└── tests/                       # Test suite
    ├── __init__.py
    ├── conftest.py
    └── ...
```

## 3. Core Components

### 3.1 Project Types

```mermaid
classDiagram
    class BaseProject {
        <<abstract>>
        +project_path: Path
        +_env_manager: EnvManager
        +__init__(project_path)
        +get_env_manager()
        +get_menus()*
        +get_env_config() 
        +configure_environment(env_type, env_name)
    }
    
    class SimpleProject {
        +__init__(project_path)
        +get_menus()
        +install()
        +test() 
        +build()
        +clean()
    }
    
    class DevelopmentProject {
        +__init__(project_path)
        +get_menus()
        +install()
        +test()
        +prehook(action)
        +release(type)
        +deploy(target)
        +clean()
        -_install_if_needed(package)
        -_configure_git_for_release()
        -_get_current_version()
        -_prepare_release_directory(release_type)
    }
    
    class GitHubProject {
        +__init__(project_path)
        +get_menus()
        +install()
        +test()
        +prehook(action)
        +clone_repo(url)
        +pull_changes()
        +push_changes()
        +clean()
        -_install_if_needed(package)
    }
    
    BaseProject <|-- SimpleProject
    BaseProject <|-- DevelopmentProject
    BaseProject <|-- GitHubProject
```

The project type system follows the Strategy pattern, enabling dynamic behavior based on project type. Each project type implements specific operations and provides appropriate menus.

### 3.2 Menu System

```mermaid
classDiagram
    class Menu {
        +title: str
        +actions: List[MenuAction]
        +style_config: Dict
        +add_action(action)
        +display()
        +apply_style(element, style_type)
    }
    
    class MenuAction {
        +name: str
        +description: str
        +callback: function
        +icon: str
        +execute(*args, **kwargs)
    }
    
    class CreateMenu {
        +template_manager: TemplateManager
        +__init__()
        +show_menu(directory)
        -_create_project(directory)
        -_update_project(directory)
        -_list_templates()
    }
    
    class AppMenu {
        +__init__()
        +show_menu(project_dir)
        -_detect_project_type(project_dir)
        -_check_environment_config(project)
        -_manage_environment(project)
        -_recreate_environment(project, config_manager)
        -_delete_environment(project, config_manager)
        -_create_environment(project, config_manager)
        -_show_help(project)
    }
    
    class MenuUtils {
        +confirm_action(message)
        +ask_for_input(message, default)
        +ask_for_selection(message, choices)
        +show_progress_bar(message, total)
        +update_progress(progress_bar, value, status)
        +style_text(text, style)
    }
    
    Menu "1" *-- "many" MenuAction : contains
    CreateMenu --> Menu : uses
    AppMenu --> Menu : uses
    CreateMenu --> MenuUtils : uses
    AppMenu --> MenuUtils : uses
```

The menu system dynamically adapts based on project type, presenting appropriate options to the user. The Command pattern is used for menu actions, improving maintainability and extensibility. Additional utility functions help with user interactions.

The enhanced menu system now includes:
- Improved styling with configurable colors and formatting
- Icons for menu actions to improve visual recognition
- Progress bar display for long-running operations
- Styled text output for better readability and user experience

### 3.3 Template Management

```mermaid
classDiagram
    class TemplateManager {
        +templates_dir: Path
        +__init__(templates_dir)
        +list_templates()
        +create_project(template_name, destination, **variables)
        +update_project(project_dir, **variables)
        -_process_template_variables(template_name, variables)
        -_get_template_defaults(template_path)
        -_get_template_version(template_path)
        -_run_copier(command, source_or_destination, destination, processed_vars)
        -_setup_example_module(destination, template_name)
    }
    
    class TemplateUtils {
        +get_template_info(template_name)
        +detect_template_type(project_dir)
        +process_template_variables(template_name, variables)
        +setup_logger_config(project_dir)
    }
    
    TemplateManager --> TemplateUtils : uses
```

Template management integrates with Copier to handle project creation and updates. Templates are stored in a dedicated directory structure with proper separation of concerns. Each template now includes a sample_module with a logger implementation. The `_setup_example_module` method ensures the proper configuration of the example module and its logging capabilities.

### 3.4 Environment Management

```mermaid
classDiagram
    class Environment {
        +root: Path
        +bin: Path
        +lib: Path
        +python: Path
        +is_virtual: bool
        +name: str
    }
    
    class BaseEnvManager {
        <<external>>
        +env: Environment
        +create()
        +remove()
        +activate()
        +deactivate()
        +run(*cmd_args)
        +install_pkg(package)
    }
    
    class EnvManager {
        +__init__(path, clear, logger)
        +run(*cmd_args, capture_output)
        -_check_capture_config()
        -_run_with_progress(cmd_args)
    }
    
    class ProgressHandler {
        +__init__(message)
        +start()
        +update(progress, status)
        +finish(success)
    }
    
    BaseProject --> EnvManager : uses
    EnvManager --|> BaseEnvManager : extends
    BaseEnvManager --> Environment : contains
    EnvManager --> ProgressHandler : uses
```

The environment management system extends an external `env_manager` library to provide environment management capabilities. It handles environment creation, activation, and running commands in the appropriate context.

The enhanced EnvManager now includes:
- Support for configurable command output capture with progress bars (enabled by default)
- Smart detection of long-running commands
- Visual progress feedback for operations like installation or testing
- Integration with the progress_runner using inline_output parameter

### 3.5 Configuration Management

```mermaid
classDiagram
    class ConfigManager {
        +config_path: Path
        +config: Dict
        +__init__(config_path)
        -_load_config()
        +save_config()
        +get(key, default)
        +set(key, value)
        +delete(key)
        +get_all()
        +clear()
        +get_config(project_path)$
        +get_logger_config(name)
        +setup_default_config()
    }
    
    class Logger {
        +__init__(name, config)
        +debug(message)
        +info(message)
        +warning(message)
        +error(message)
        +critical(message)
    }
    
    BaseProject --> ConfigManager : uses
    TemplateManager --> ConfigManager : uses
    ConfigManager --> Logger : configures
```

Configuration management provides persistent storage for project settings, template information, and environment configuration. It uses YAML files to store configuration data in a `.app_cache` directory within each project.

The enhanced configuration system now includes:
- Centralized configuration in `.app_cache/config.yaml`
- Logger configuration with multiple output targets
- Environment command execution parameters with capture_output enabled by default
- Menu styling configuration

## 4. Key Workflows

### 4.1 Project Creation

```mermaid
sequenceDiagram
    actor User
    User->>CLI: cicd_tools create
    CLI->>CreateMenu: show_menu()
    CreateMenu->>User: Display template options
    User->>CreateMenu: Select template
    CreateMenu->>TemplateUtils: get_template_info(template)
    CreateMenu->>User: Project configuration questionary
    User->>CreateMenu: Provide configuration
    CreateMenu->>TemplateManager: create_project(template, config)
    TemplateManager->>ConfigManager: Save template info
    TemplateManager->>Copier: Apply template
    TemplateManager->>TemplateManager: _setup_example_module(destination, template)
    TemplateManager->>ConfigManager: setup_default_config()
    TemplateManager->>User: Project created successfully
```

### 4.2 Environment Configuration Check

```mermaid
sequenceDiagram
    actor User
    participant AppMenu
    participant ConfigManager
    participant MenuUtils
    participant EnvManager
    participant ProjectType
    
    User->>AppMenu: Select any operation
    AppMenu->>AppMenu: check_environment_config()
    AppMenu->>ConfigManager: get_config(path)
    ConfigManager->>AppMenu: Return config
    
    alt No environment configured
        AppMenu->>MenuUtils: ask_for_selection("Environment type")
        MenuUtils->>User: Show options (Current/New virtual env)
        User->>MenuUtils: Select option
        MenuUtils->>AppMenu: Return selection
        
        alt Selected "Current"
            AppMenu->>ProjectType: configure_environment("current")
            ProjectType->>EnvManager: Initialize with current environment
            AppMenu->>ConfigManager: Set environment config
        else Selected "New virtual environment"
            AppMenu->>MenuUtils: ask_for_input("Environment name")
            MenuUtils->>User: Prompt for name
            User->>MenuUtils: Provide environment name
            MenuUtils->>AppMenu: Return environment name
            AppMenu->>ProjectType: configure_environment("virtual", name)
            ProjectType->>EnvManager: Create virtual environment
            AppMenu->>ConfigManager: Set environment config
        end
        
        AppMenu->>ProjectType: install()
    end
    
    AppMenu->>ProjectType: Execute selected operation
    ProjectType->>User: Return operation result
```

### 4.3 Environment Management Menu

```mermaid
sequenceDiagram
    actor User
    participant AppMenu
    participant Menu
    participant ConfigManager
    participant MenuUtils
    participant EnvManager
    
    User->>AppMenu: Select "Manage Environment"
    AppMenu->>ConfigManager: get_config(path)
    ConfigManager->>AppMenu: Return config
    
    alt Has environment config
        AppMenu->>Menu: Create environment menu
        
        alt Virtual environment
            Menu->>Menu: Add recreate/delete actions
        end
        
        Menu->>Menu: Add create action
        Menu->>User: Display menu
        User->>Menu: Select option
        
        alt Selected "Recreate"
            Menu->>AppMenu: _recreate_environment()
            AppMenu->>MenuUtils: confirm_action()
            MenuUtils->>User: Ask for confirmation
            User->>MenuUtils: Confirm
            AppMenu->>EnvManager: remove()
            AppMenu->>ProjectType: configure_environment("virtual", name)
            AppMenu->>ProjectType: install()
        else Selected "Delete"
            Menu->>AppMenu: _delete_environment()
            AppMenu->>MenuUtils: confirm_action()
            MenuUtils->>User: Ask for confirmation
            User->>MenuUtils: Confirm
            AppMenu->>EnvManager: remove()
            AppMenu->>ConfigManager: delete("environment")
        else Selected "Create"
            Menu->>AppMenu: _create_environment()
            AppMenu->>MenuUtils: ask_for_input("Environment name")
            MenuUtils->>User: Prompt for name
            User->>MenuUtils: Provide environment name
            AppMenu->>ProjectType: configure_environment("virtual", name)
            AppMenu->>ConfigManager: set("environment", config)
            AppMenu->>ProjectType: install()
        end
        
        AppMenu->>User: Display operation result
    else No environment config
        AppMenu->>User: Display "No environment configured"
    end
```

### 4.4 App Operations by Project Type

#### 4.4.1 Simple Project - Build Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Build option
    AppMenu->>SimpleProject: build()
    SimpleProject->>ConfigManager: Check capture_output flag
    alt capture_output enabled
        SimpleProject->>MenuUtils: show_progress_bar("Building project...")
        SimpleProject->>EnvManager: run("python", "setup.py", "build", capture_output=True)
        SimpleProject->>MenuUtils: update_progress()
    else capture_output disabled
        SimpleProject->>EnvManager: run("python", "setup.py", "build", capture_output=False)
    end
    SimpleProject->>AppMenu: Return operation status
    AppMenu->>User: Display build results
```

#### 4.4.2 Logger Configuration and Usage

```mermaid
sequenceDiagram
    participant Application
    participant ConfigManager
    participant Logger
    
    Application->>ConfigManager: get_logger_config("my_logger")
    ConfigManager->>ConfigManager: Read from .app_cache/config.yaml
    ConfigManager->>Application: Return logger configuration
    
    Application->>Logger: Create logger with config
    Application->>Logger: logger.info("Message")
    
    Logger->>Logger: Format message according to config
    
    alt Console output configured
        Logger->>Console: Write formatted message
    end
    
    alt File output configured
        Logger->>File: Write formatted message
    end
```

## 5. Implementation Approach

### 5.1 SOLID Principles Application

1. **Single Responsibility Principle**: Each class has a single responsibility
   - ProjectType classes handle project-specific logic
   - MenuSystem handles user interaction
   - TemplateManager handles template operations
   - ConfigManager handles configuration persistence
   - EnvironmentManager handles environment tasks
   - Logger handles logging functionality

2. **Open/Closed Principle**: Open for extension, closed for modification
   - New project types can be added without modifying existing code
   - Menu system can be extended with new actions
   - Environment management is extensible
   - Logging system supports multiple configurations without code changes

3. **Liskov Substitution Principle**: Subtypes are substitutable for base types
   - All ProjectType implementations can be used interchangeably
   - Base classes define clear contracts for subclasses

4. **Interface Segregation Principle**: Clients only depend on methods they use
   - Clear interfaces for each component
   - No forced dependencies on unused functionality
   - BaseProject only includes methods common to all project types

5. **Dependency Inversion Principle**: High-level modules depend on abstractions
   - Core components depend on interfaces, not concrete implementations
   - Dependency injection used where appropriate

### 5.2 GitHub Workflow Configurations (Planned)

The following GitHub workflow configurations are planned for future implementation:

#### 5.2.1 pytest.yml Workflow

The pytest workflow will run automated tests on push and pull requests:

- Uses matrix strategy for multiple Python versions
- Configures caching for faster execution
- Reports test results

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
        restore-keys: |
          ${{ runner.os }}-pip-
          
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
        
    - name: Run tests
      run: |
        pytest --cov=cicd_tools
```

#### 5.2.2 release.yml Workflow

The release workflow will handle version management and build operations:

- User-triggered workflow with version selection
- Automatic version bumping using bump2version
- Conditional logic for production vs. beta releases

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Release Type'
        required: true
        default: 'beta'
        type: choice
        options:
          - beta
          - prod

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build bump2version twine
        
    - name: Configure Git
      run: |
        git config --local user.email "actions@github.com"
        git config --local user.name "GitHub Actions"
        
    - name: Bump version (Production)
      if: ${{ github.event.inputs.release_type == 'prod' }}
      run: |
        bump2version patch
        
    - name: Bump version (Beta)
      if: ${{ github.event.inputs.release_type == 'beta' }}
      run: |
        current_version=$(grep -o 'current_version = "[^"]*' .bumpversion.cfg | cut -d'"' -f2)
        bump2version patch --new-version "${current_version}.beta"
        
    - name: Build package
      run: |
        python -m build
        
    - name: Create release directory
      run: |
        mkdir -p dist/${{ github.event.inputs.release_type }}
        cp dist/*.whl dist/${{ github.event.inputs.release_type }}/
        cp dist/*.tar.gz dist/${{ github.event.inputs.release_type }}/
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: release-${{ github.event.inputs.release_type }}
        path: dist/${{ github.event.inputs.release_type }}/*
```

#### 5.2.3 deploy.yml Workflow

The deploy workflow will handle deployment to PyPI:

- User-guided artifact selection
- Conditional deployment targets (test.pypi or main PyPI)
- Proper use of secrets

```yaml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      deploy_target:
        description: 'Deployment Target'
        required: true
        default: 'test'
        type: choice
        options:
          - test
          - prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install twine
        
    - name: Download beta artifacts
      if: ${{ github.event.inputs.deploy_target == 'test' }}
      uses: actions/download-artifact@v3
      with:
        name: release-beta
        path: dist/beta
        
    - name: Download production artifacts
      if: ${{ github.event.inputs.deploy_target == 'prod' }}
      uses: actions/download-artifact@v3
      with:
        name: release-prod
        path: dist/release
        
    - name: Deploy to TestPyPI
      if: ${{ github.event.inputs.deploy_target == 'test' }}
      env:
        TWINE_USERNAME: ${{ secrets.TEST_PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_PASSWORD }}
      run: |
        twine upload --repository testpypi dist/beta/*
        
    - name: Deploy to PyPI
      if: ${{ github.event.inputs.deploy_target == 'prod' }}
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        twine upload dist/release/*
```

## 6. Development Progress

1. ✅ Set up project structure and dependencies
2. ✅ Implement core interfaces and base classes
3. ✅ Develop template management system
4. ✅ Implement project type classes
5. ✅ Create menu system with dynamic adaptation
6. ✅ Implement environment management
7. ✅ Develop project templates for each project type
8. ⏳ Implement enhanced menu system with improved styling
9. ⏳ Replace {{ project_name.replace('-', '_') }} with sample_module
10. ⏳ Add example modules with logging to all templates
11. ⏳ Implement centralized configuration in .app_cache
12. ⏳ Configure capture_output flag (enabled by default)
13. ⏳ Develop progress bar display for captured output
14. ⏳ Implement GitHub workflow configurations
15. ⏳ Write comprehensive tests and documentation

## 7. Technical Considerations

### 7.1 Dependencies

- **Questionary**: For interactive command prompts
- **Copier**: For template-based project creation and updates
- **PyYAML**: For configuration handling
- **Click**: For CLI interface
- **Rich**: For enhanced terminal formatting and progress bars
- **Logging**: For flexible logging capabilities

### 7.2 Error Handling

- Comprehensive try/except blocks with descriptive messages
- Graceful failure modes with recovery options
- Proper logging at appropriate levels

### 7.3 Testing Strategy

- Unit tests for individual components
- Integration tests for workflow verification
- Mocking for external dependencies

### 7.4 Configuration Structure

The `.app_cache/config.yaml` will have the following structure:

```yaml
# Environment configuration
environment:
  capture_output: true  # Controls whether to capture command output and show progress bar (enabled by default)
  
# Logging configuration
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
        
  # Additional logger configurations
  development:
    level: DEBUG
    handlers:
      - type: console
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      - type: file
        filename: "dev.log"
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        max_bytes: 10485760
        backup_count: 5

# Menu styling configuration
styling:
  colors:
    primary: "#007BFF"
    secondary: "#6C757D"
    success: "#28A745"
    warning: "#FFC107"
    error: "#DC3545"
  formatting:
    title_style: "bold underline"
    menu_item_style: "italic"
```

## 8. Future Extensibility

The architecture is designed for future expansion:
- Additional project types can be added by creating new classes
- New menu actions can be registered dynamically
- Template system supports custom template variables and functions
- Environment management system can be extended for additional configuration options
- Configuration management provides a foundation for more complex project settings
- Logging system supports custom handlers and formatters
- Menu styling can be extended with additional themes