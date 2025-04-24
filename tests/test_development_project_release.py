"""Tests for the release method of the DevelopmentProject class."""

import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from cicd_tools.project_types.development_project import DevelopmentProject


class TestDevelopmentProjectRelease:
    """Test class for the release method of the DevelopmentProject class."""

    @pytest.fixture
    def mock_env_manager(self) -> Generator[MagicMock, None, None]:
        """Mock the environment manager."""
        with patch.object(DevelopmentProject, 'get_env_manager') as mock:
            # Configure the mock to return a mock instance
            mock_instance = MagicMock()
            mock_runner = MagicMock()
            mock_instance.get_runner.return_value = mock_runner
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def mock_package_manager(self, mock_env_manager) -> Generator[MagicMock, None, None]:
        """Mock the PackageManager class."""
        with patch('cicd_tools.project_types.development_project.PackageManager') as mock:
            # Configure the mock to return a mock instance
            mock_instance = MagicMock()
            mock_instance.is_installed.return_value = True  # Assume packages are installed
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def mock_configure_git(self) -> Generator[MagicMock, None, None]:
        """Mock the _configure_git_for_release method."""
        with patch.object(DevelopmentProject, '_configure_git_for_release') as mock:
            yield mock

    @pytest.fixture
    def mock_prepare_release_dir(self) -> Generator[MagicMock, None, None]:
        """Mock the _prepare_release_directory method."""
        with patch.object(DevelopmentProject, '_prepare_release_directory') as mock:
            yield mock

    @pytest.fixture
    def mock_run(self) -> Generator[MagicMock, None, None]:
        """Mock the run method."""
        with patch.object(DevelopmentProject, 'run') as mock:
            yield mock
            
    @pytest.fixture
    def mock_bump_version(self) -> Generator[MagicMock, None, None]:
        """Mock the bump_version_for_release method."""
        with patch.object(DevelopmentProject, 'bump_version_for_release') as mock:
            yield mock
            
    @pytest.fixture
    def mock_clean_dist(self) -> Generator[MagicMock, None, None]:
        """Mock the _clean_dist_root method."""
        with patch.object(DevelopmentProject, '_clean_dist_root') as mock:
            yield mock

    def test_release_prod(self, mock_package_manager, mock_configure_git, 
                         mock_prepare_release_dir, mock_run,
                         mock_bump_version, mock_clean_dist) -> None:
        """Test production release process with specified bump type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock direct calls instead of using fixtures
            mock_bump_version.reset_mock()
            
            # Call the release method with named parameters to avoid any confusion
            result = project.release(release_type='prod', bump_type='minor')
            
            # Verify the result and method calls
            assert result is True
            mock_configure_git.assert_called_once()
            mock_bump_version.assert_called_once_with('prod', 'minor')
            assert mock_clean_dist.call_count == 2
            mock_run.assert_any_call('python', '-m', 'build')
            mock_prepare_release_dir.assert_called_once_with('prod')

    def test_release_beta(self, mock_package_manager, mock_configure_git, 
                         mock_prepare_release_dir, mock_run,
                         mock_bump_version, mock_clean_dist) -> None:
        """Test beta release process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Call the release method with beta release type
            result = project.release('beta')
            
            # Verify the result
            assert result is True
            
            # Verify the correct methods were called
            mock_configure_git.assert_called_once()
            mock_bump_version.assert_called_once_with('beta', 'patch')  # Default bump type for beta is patch
            assert mock_clean_dist.call_count == 2  # Called before build and after prepare_release_directory
            mock_run.assert_called_with('python', '-m', 'build')
            mock_prepare_release_dir.assert_called_once_with('beta')

    def test_release_with_exception(self, mock_package_manager, mock_configure_git) -> None:
        """Test release method when an exception occurs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock the questionary.select to avoid interactive prompts during tests
            with patch('cicd_tools.project_types.development_project.questionary.select') as mock_select:
                mock_select.return_value.ask.return_value = 'patch'  # Mock response for bump type selection
                
                # Mock run to raise an exception
                with patch.object(project, 'run', side_effect=Exception('Test exception')):
                    # Call the release method with explicit release_type to avoid first questionary prompt
                    result = project.release('prod')
                    
                    # Verify the result
                    assert result is False

    def test_release_with_user_selection_beta(self, mock_package_manager, mock_configure_git, 
                                           mock_prepare_release_dir, mock_run,
                                           mock_bump_version, mock_clean_dist) -> None:
        """Test release method with user selection of beta release type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock questionary.select to return 'beta'
            with patch('cicd_tools.project_types.development_project.questionary.select') as mock_select:
                mock_select.return_value.ask.return_value = 'beta'
                
                # Call the release method without specifying release type
                result = project.release()
                
                # Verify the result
                assert result is True
                
                # Verify questionary.select was called
                mock_select.assert_called_once()
                
                # Verify the correct methods were called
                mock_bump_version.assert_called_once_with('beta', 'patch')
                assert mock_clean_dist.call_count == 2  # Called before build and after prepare_release_directory
                mock_run.assert_called_with('python', '-m', 'build')
                mock_prepare_release_dir.assert_called_once_with('beta')

    def test_release_with_user_selection_prod(self, mock_package_manager, mock_configure_git, 
                                           mock_prepare_release_dir, mock_run,
                                           mock_bump_version, mock_clean_dist) -> None:
        """Test release method with user selection of production release type and bump type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock questionary.select to return first 'prod', then 'minor' for bump type
            select_return_values = ['prod', 'minor']
            
            def select_side_effect(*args:Any, **kwargs:Any) -> MagicMock:
                mock_result = MagicMock()
                mock_result.ask.return_value = select_return_values.pop(0)
                return mock_result
                
            with patch('cicd_tools.project_types.development_project.questionary.select', side_effect=select_side_effect):
                # Call the release method without specifying release type or bump type
                result = project.release()
                
                # Verify the result
                assert result is True
                
                # Verify the correct methods were called
                mock_bump_version.assert_called_once_with('prod', 'minor')
                assert mock_clean_dist.call_count == 2
                mock_run.assert_called_with('python', '-m', 'build')
                mock_prepare_release_dir.assert_called_once_with('prod')

    def test_clean_dist_root(self) -> None:
        """Test the _clean_dist_root method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            dist_dir = Path(temp_dir) / "dist"
            dist_dir.mkdir(exist_ok=True)
            
            # Create some files in the dist directory
            test_file = dist_dir / "test.txt"
            test_file.touch()
            
            # Create a subdirectory with a file
            beta_dir = dist_dir / "beta"
            beta_dir.mkdir(exist_ok=True)
            beta_file = beta_dir / "beta.txt"
            beta_file.touch()
            
            # Call the method
            project._clean_dist_root()
            
            # Verify that the file in the root is gone but the subdirectory and its file remain
            assert not test_file.exists()
            assert beta_dir.exists()
            assert beta_file.exists()


class TestVersionManagerMixin:
    """Test class for the VersionManagerMixin methods."""
    
    @pytest.fixture
    def mock_run(self) -> Generator[MagicMock, None, None]:
        """Mock the run method."""
        with patch.object(DevelopmentProject, 'run') as mock:
            yield mock
            
    def test_is_beta_version(self) -> None:
        """Test the _is_beta_version method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Test with beta versions
            assert project._is_beta_version('0.1.0b0') is True
            assert project._is_beta_version('0.1.0.beta') is True
            
            # Test with production versions
            assert project._is_beta_version('0.1.0') is False
            assert project._is_beta_version('1.2.3') is False
    
    def test_bump_version_for_release_prod_from_beta(self, mock_run) -> None:
        """Test bump_version_for_release when transitioning from beta to prod."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a beta version
            with patch.object(project, '_get_current_version', return_value='0.1.0.beta'):
                # Mock _transition_beta_to_prod to verify it's called
                with patch.object(project, '_transition_beta_to_prod') as mock_transition:
                    # Call the method
                    project.bump_version_for_release('prod')
                    
                    # Verify _transition_beta_to_prod was called with the correct version
                    # It now gets the default bump_type parameter
                    mock_transition.assert_called_once_with('0.1.0.beta', 'patch')
    
    def test_bump_version_for_release_prod_from_prod(self, mock_run) -> None:
        """Test bump_version_for_release when already on a production version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a production version
            with patch.object(project, '_get_current_version', return_value='0.1.0'):
                # Mock _bump_production_version to verify it's called
                with patch.object(project, '_bump_production_version') as mock_bump:
                    # Call the method
                    project.bump_version_for_release('prod')
                    
                    # Verify _bump_production_version was called
                    mock_bump.assert_called_once()
    
    def test_bump_version_for_release_beta_from_prod(self, mock_run) -> None:
        """Test bump_version_for_release when transitioning from prod to beta."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a production version
            with patch.object(project, '_get_current_version', return_value='0.1.0'):
                # Mock _transition_prod_to_beta to verify it's called
                with patch.object(project, '_transition_prod_to_beta') as mock_transition:
                    # Call the method
                    project.bump_version_for_release('beta')
                    
                    # Verify _transition_prod_to_beta was called with the correct version
                    mock_transition.assert_called_once_with('0.1.0')
    
    def test_bump_version_for_release_beta_from_beta(self, mock_run) -> None:
        """Test bump_version_for_release when already on a beta version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a beta version
            with patch.object(project, '_get_current_version', return_value='0.1.0b0'):
                # Mock _bump_beta_version to verify it's called
                with patch.object(project, '_bump_beta_version') as mock_bump:
                    # Call the method
                    project.bump_version_for_release('beta')
                    
                    # Verify _bump_beta_version was called
                    mock_bump.assert_called_once()
    
    def test_transition_beta_to_prod(self, mock_run) -> None:
        """Test the _transition_beta_to_prod method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Test with .beta suffix
            project._transition_beta_to_prod('0.1.0.beta')
            mock_run.assert_called_with('bump2version', '--allow-dirty', '--new-version', '0.1.1', 'patch', capture_output=False)
            
            mock_run.reset_mock()
            
            # Test with b suffix
            project._transition_beta_to_prod('0.1.0b0')
            mock_run.assert_called_with('bump2version', '--allow-dirty', '--new-version', '0.1.1', 'patch', capture_output=False)
    
    def test_transition_prod_to_beta(self, mock_run) -> None:
        """Test the _transition_prod_to_beta method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            project._transition_prod_to_beta('0.1.0')
            mock_run.assert_called_with('bump2version', 'patch', '--allow-dirty', '--new-version', '0.1.0b0', capture_output=False)  # noqa: E501

    def test_bump_beta_version(self, mock_run) -> None:
        """Test the _bump_beta_version method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            project._bump_beta_version()
            mock_run.assert_called_with('bump2version', 'beta', capture_output=False)
    
    def test_bump_production_version(self, mock_run) -> None:
        """Test the _bump_production_version method for a production version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a production version
            with patch.object(project, '_get_current_version', return_value='0.1.8'):
                # Mock _is_beta_version to return False (not a beta version)
                with patch.object(project, '_is_beta_version', return_value=False):
                    # Call the method
                    project._bump_production_version()
                    
                    # Verify that bump2version is called with the right parameters
                    mock_run.assert_called_once_with(
                        'bump2version', '--allow-dirty', '--new-version', '0.1.9', 'patch',
                        capture_output=False
                    )


    def test_bump_production_version_from_beta(self, mock_run) -> None:
        """Test the _bump_production_version method when starting from a beta version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal project with the mixin
            project = DevelopmentProject(Path(temp_dir))
            
            # Mock _get_current_version to return a beta version
            with patch.object(project, '_get_current_version', return_value='0.1.8b0'):
                # Mock _is_beta_version to return True (beta version)
                with patch.object(project, '_is_beta_version', return_value=True):
                    # Mock _transition_beta_to_prod to verify it's called
                    with patch.object(project, '_transition_beta_to_prod') as mock_transition:
                        # Call the method
                        project._bump_production_version()
                        
                        # Verify that _transition_beta_to_prod was called with the beta version
                        # It now includes the default bump_type parameter
                        mock_transition.assert_called_once_with('0.1.8b0', 'patch')
                        
    def test_calculate_next_version(self) -> None:
        """Test the _calculate_next_version method for different scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DevelopmentProject(Path(temp_dir))
            
            # Production version predictions
            # Patch version increment
            assert project._calculate_next_version('0.1.9', 'patch', 'prod') == '0.1.10'
            # Minor version increment
            assert project._calculate_next_version('0.1.9', 'minor', 'prod') == '0.2.0'
            # Major version increment
            assert project._calculate_next_version('0.9.9', 'major', 'prod') == '1.0.0'
            
            # Beta version predictions
            # New beta from production
            assert project._calculate_next_version('1.0.0', 'patch', 'beta') == '1.0.0b0'
            # Next beta version
            assert project._calculate_next_version('1.0.0b0', 'patch', 'beta') == '1.0.0b1'
            
            # Beta to production transitions with different bump types
            assert project._calculate_next_version('0.1.9b2', 'patch', 'prod') == '0.1.10'
            assert project._calculate_next_version('0.1.9b2', 'minor', 'prod') == '0.2.0'
            assert project._calculate_next_version('0.9.9b2', 'major', 'prod') == '1.0.0'


if __name__ == "__main__":
    # Run the tests directly
    pytest.main(["-v", __file__])
