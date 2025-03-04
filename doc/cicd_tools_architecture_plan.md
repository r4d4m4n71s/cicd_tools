# CICD Tools Project - Detailed Architecture Plan

## 1. Project Overview

The cicd_tools project will be a flexible framework for development tasks including project creation, testing, building, and deployment. It will feature:

- Dynamic menus that adapt based on project type
- Template-based project creation and updates using Copier
- Support for multiple project types with different capabilities
- Integration with GitHub workflows for CI/CD
- Comprehensive environment management

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
│       ├── env_manager.py       # Adapted from existing env_manager
│       └── config_manager.py    # Project configuration
├── project_templates/           # Copier templates
│   ├── simple_project/
│   ├── development_project/
│   └── github_project/
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
        +__init__(project_path)
        +get_env_manager()
        +get_menus()*
        +get_env_config() 
        +configure_environment(env_type, env_name)
    }
    
    class SimpleProject {
        +install()
        +test() 
        +get_menus()
    }
    
    class DevelopmentProject {
        +install()
        +test()
        +prehook(action)
        +release(type)
        +deploy(target)
        +get_menus()
    }
    
    class GitHubProject {
        +install()
        +test()
        +prehook(action)
        +clone_repo(url)
        +get_menus()
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
        +add_action(action)
        +display()
    }
    
    class MenuAction {
        +name: str
        +description: str
        +callback: function
        +execute(*args, **kwargs)
    }
    
    class CreateMenu {
        +show_menu()
        -create_project()
        -update_project()
    }
    
    class AppMenu {
        +show_menu(project_dir)
        -detect_project_type(project_dir)
        -manage_environment()
        -check_environment_config()
    }
    
    class EnvironmentManager {
        +current_env: Environment
        +create_environment(name)
        +delete_environment()
        +recreate_environment()
        +get_environment_info()
    }
    
    Menu "1" *-- "many" MenuAction : contains
    CreateMenu --> Menu : uses
    AppMenu --> Menu : uses
    AppMenu --> EnvironmentManager : uses
```

The menu system dynamically adapts based on project type, presenting appropriate options to the user. The Command pattern is used for menu actions, improving maintainability and extensibility.

### 3.3 Template Management

```mermaid
classDiagram
    class TemplateManager {
        +templates_dir: Path
        +list_templates()
        +create_project(template_name, destination, **variables)
        +update_project(template_name, project_dir, **variables)
    }
    
    class TemplateUtils {
        +process_template_variables(template_name, variables)
        +detect_template_type(project_dir)
    }
    
    TemplateManager --> TemplateUtils : uses
```

Template management integrates with Copier to handle project creation and updates. Templates will be stored in a dedicated directory structure with proper separation of concerns.

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
    
    class EnvManager {
        +env: Environment
        +create()
        +remove()
        +activate()
        +deactivate()
        +run(*cmd_args)
        +install_pkg(package)
    }
    
    BaseProject --> EnvManager : uses
    EnvManager --> Environment : contains
```

We'll adapt the existing `env_manager` module to provide environment management capabilities, focusing on the elements needed for cicd_tools without unnecessary complexity.

## 4. Key Workflows

### 4.1 Project Creation

```mermaid
sequenceDiagram
    actor User
    User->>CLI: cicd_tools create
    CLI->>CreateMenu: show_menu()
    CreateMenu->>User: Display template options
    User->>CreateMenu: Select template
    CreateMenu->>User: Project configuration questionary
    User->>CreateMenu: Provide configuration
    CreateMenu->>TemplateManager: create_project(template, config)
    TemplateManager->>Copier: Apply template
    TemplateManager->>User: Project created successfully
```

### 4.2 Environment Configuration Check

```mermaid
sequenceDiagram
    actor User
    participant AppMenu
    participant Questionary
    participant EnvManager
    participant ProjectType
    
    User->>AppMenu: Select any operation
    AppMenu->>AppMenu: check_environment_config()
    
    alt No environment configured
        AppMenu->>Questionary: Ask for environment selection
        Questionary->>User: Show options (Current/New virtual env)
        User->>Questionary: Select option
        Questionary->>AppMenu: Return selection
        
        alt Selected "Current"
            AppMenu->>EnvManager: Create with current environment
        else Selected "New virtual environment"
            AppMenu->>Questionary: Ask for environment name
            Questionary->>User: Prompt for name
            User->>Questionary: Provide environment name
            Questionary->>AppMenu: Return environment name
            AppMenu->>EnvManager: Create new environment with name
            EnvManager->>EnvManager: Create virtual environment
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
    participant Questionary
    participant EnvironmentManager
    
    User->>AppMenu: Select "Manage Environment"
    AppMenu->>Questionary: Show environment options
    Questionary->>User: Display options (Recreate/Delete/Create)
    User->>Questionary: Select option
    Questionary->>AppMenu: Return selection
    
    alt Selected "Recreate"
        AppMenu->>EnvironmentManager: recreate_environment()
        EnvironmentManager->>EnvironmentManager: Delete virtual environment
        EnvironmentManager->>EnvironmentManager: Create new environment
        EnvironmentManager->>AppMenu: Return success
    else Selected "Delete"
        AppMenu->>EnvironmentManager: delete_environment()
        EnvironmentManager->>EnvironmentManager: Remove virtual environment
        EnvironmentManager->>AppMenu: Return success
    else Selected "Create"
        AppMenu->>Questionary: Ask for environment name
        Questionary->>User: Prompt for name
        User->>Questionary: Provide environment name
        Questionary->>AppMenu: Return environment name
        AppMenu->>EnvironmentManager: create_environment(name)
        EnvironmentManager->>EnvironmentManager: Create new environment
        EnvironmentManager->>AppMenu: Return success
    end
    
    AppMenu->>User: Display operation result
```

### 4.4 App Operations by Project Type

#### 4.4.1 Simple Project - Build Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Build option
    AppMenu->>SimpleProject: build()
    SimpleProject->>EnvManager: run("python", "setup.py", "build")
    EnvManager->>SimpleProject: Return result
    SimpleProject->>AppMenu: Return operation status
    AppMenu->>User: Display build results
```

#### 4.4.2 Development Project - Install Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Install option
    AppMenu->>DevelopmentProject: install()
    DevelopmentProject->>EnvManager: get_env_manager()
    DevelopmentProject->>EnvManager: run("python", "-m", "pip", "install", "-e", ".[dev]")
    EnvManager->>DevelopmentProject: Return result
    DevelopmentProject->>AppMenu: Return operation status
    AppMenu->>User: Display installation results
```

#### 4.4.3 Development Project - Test Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Test option
    AppMenu->>DevelopmentProject: test()
    DevelopmentProject->>Questionary: Display test options (All/Failed)
    Questionary->>User: Show test choices
    User->>Questionary: Select test option
    Questionary->>DevelopmentProject: Return selection
    DevelopmentProject->>EnvManager: run("pytest", selected_option, "--tb=short", "-v")
    EnvManager->>DevelopmentProject: Return test results
    DevelopmentProject->>AppMenu: Return operation status
    AppMenu->>User: Display test results
```

#### 4.4.4 Development/GitHub Project - Prehook Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Prehook option
    AppMenu->>User: Ask for action (enable/disable)
    User->>AppMenu: Provide action
    AppMenu->>ProjectType: hooks(action)
    alt action == "on"
        ProjectType->>EnvManager: run("pre-commit", "install")
    else action == "off"
        ProjectType->>EnvManager: run("pre-commit", "uninstall")
    end
    EnvManager->>ProjectType: Return result
    ProjectType->>AppMenu: Return operation status
    AppMenu->>User: Display hook configuration result
```

#### 4.4.5 Development Project - Release Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Release option
    AppMenu->>User: Ask for release type (beta/prod)
    User->>AppMenu: Provide release type
    AppMenu->>DevelopmentProject: release(type)
    DevelopmentProject->>DevelopmentProject: _install_if_needed("build")
    DevelopmentProject->>DevelopmentProject: _install_if_needed("bump2version")
    DevelopmentProject->>DevelopmentProject: _configure_git_for_release()
    alt type == "prod"
        DevelopmentProject->>EnvManager: run("bump2version", "patch")
    else type == "beta"
        DevelopmentProject->>DevelopmentProject: _get_current_version()
        DevelopmentProject->>EnvManager: run("bump2version", "patch", "--new-version", version+".beta")
    end
    DevelopmentProject->>EnvManager: run("python", "-m", "build")
    DevelopmentProject->>DevelopmentProject: _prepare_release_directory(type)
    DevelopmentProject->>DevelopmentProject: Move build artifacts to release directory
    DevelopmentProject->>AppMenu: Return operation status
    AppMenu->>User: Display release creation result
```

#### 4.4.6 Development Project - Deploy Operation

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Deploy option
    AppMenu->>User: Ask for deploy target (test/prod)
    User->>AppMenu: Provide deploy target
    AppMenu->>DevelopmentProject: deploy(target)
    DevelopmentProject->>DevelopmentProject: _install_if_needed("twine")
    alt target == "prod"
        DevelopmentProject->>DevelopmentProject: Check for production release
        DevelopmentProject->>EnvManager: run("twine", "upload", "dist/release/*")
    else target == "test"
        DevelopmentProject->>DevelopmentProject: Check for beta release
        DevelopmentProject->>EnvManager: run("twine", "upload", "--repository", "testpypi", "dist/beta/*")
    end
    DevelopmentProject->>AppMenu: Return operation status
    AppMenu->>User: Display deployment result
```

#### 4.4.7 GitHub Project - Clone Repository Operation

```mermaid
sequenceDiagram
    actor User
    User->>CreateMenu: Select GitHub project
    CreateMenu->>User: Ask for repository URL
    User->>CreateMenu: Provide repository URL
    CreateMenu->>GitHubProject: clone_repo(url)
    GitHubProject->>EnvManager: run("git", "clone", url, project_path)
    EnvManager->>GitHubProject: Return clone result
    GitHubProject->>TemplateManager: update_project(template, project_path)
    TemplateManager->>GitHubProject: Return template update result
    GitHubProject->>CreateMenu: Return operation status
    CreateMenu->>User: Display repository setup result
```

#### 4.4.8 Help Operation (Common to all project types)

```mermaid
sequenceDiagram
    actor User
    User->>AppMenu: Select Help option
    AppMenu->>AppMenu: _get_command_help(command)
    AppMenu->>AppMenu: Load documentation from markdown
    AppMenu->>User: Display help text
```

## 5. Implementation Approach

### 5.1 SOLID Principles Application

1. **Single Responsibility Principle**: Each class has a single responsibility
   - ProjectType classes handle project-specific logic
   - MenuSystem handles user interaction
   - TemplateManager handles template operations
   - EnvironmentManager handles environment tasks

2. **Open/Closed Principle**: Open for extension, closed for modification
   - New project types can be added without modifying existing code
   - Menu system can be extended with new actions
   - Environment management is extensible

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

### 5.2 GitHub Workflow Configurations

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

## 6. Development Steps

1. Set up project structure and dependencies
2. Implement core interfaces and base classes
3. Develop template management system
4. Implement project type classes
5. Create menu system with dynamic adaptation
6. Implement environment management
7. Develop project templates for each project type
8. Implement GitHub workflow configurations
9. Write comprehensive tests and documentation

## 7. Technical Considerations

### 7.1 Dependencies

- **Questionary**: For interactive command prompts
- **Copier**: For template-based project creation and updates
- **PyYAML**: For configuration handling
- **Click**: For CLI interface (optional, can use argparse)

### 7.2 Error Handling

- Comprehensive error handling with descriptive messages
- Graceful failure modes with recovery options
- Proper logging at appropriate levels

### 7.3 Testing Strategy

- Unit tests for individual components
- Integration tests for workflow verification
- Mocking for external dependencies

## 8. Future Extensibility

The architecture is designed for future expansion:
- Additional project types can be added by creating new classes
- New menu actions can be registered dynamically
- Template system supports custom template variables and functions
- Environment management system can be extended for additional configuration options