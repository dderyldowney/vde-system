"""
Unit tests for test_utilities.py
"""

import json
import os
import subprocess
import tempfile
import time
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'features', 'steps'))

from test_utilities import (
    cleanup_test_containers,
    cleanup_test_vms,
    cleanup_port_registry,
    cleanup_docker_networks,
    cleanup_docker_volumes,
    register_cleanup_handler,
    create_test_vm_config,
    wait_for_condition,
    before_scenario,
    after_scenario,
    after_feature,
    before_all,
    after_all
)


class TestCleanupTestContainers(unittest.TestCase):
    """Tests for cleanup_test_containers function"""
    
    @patch('subprocess.run')
    def test_cleanup_with_containers(self, mock_run):
        """Test cleanup when containers exist"""
        # Mock docker ps output
        ps_result = Mock()
        ps_result.stdout = "vde-test-python\nvde-test-js\n"
        ps_result.returncode = 0
        
        # Mock docker rm output
        rm_result = Mock()
        rm_result.returncode = 0
        
        mock_run.side_effect = [ps_result, rm_result, rm_result]
        
        cleanup_test_containers(prefix="vde-test-")
        
        # Verify docker ps was called
        assert mock_run.call_args_list[0] == call(
            ["docker", "ps", "-a", "--filter", "name=vde-test-", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verify docker rm was called for each container
        assert mock_run.call_args_list[1] == call(
            ["docker", "rm", "-f", "vde-test-python"],
            capture_output=True,
            text=True,
            check=True
        )
        assert mock_run.call_args_list[2] == call(
            ["docker", "rm", "-f", "vde-test-js"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_cleanup_with_no_containers(self, mock_run):
        """Test cleanup when no containers exist"""
        # Mock docker ps with empty output
        ps_result = Mock()
        ps_result.stdout = ""
        ps_result.returncode = 0
        
        mock_run.return_value = ps_result
        
        cleanup_test_containers(prefix="vde-test-")
        
        # Verify only docker ps was called
        assert mock_run.call_count == 1
        assert mock_run.call_args_list[0] == call(
            ["docker", "ps", "-a", "--filter", "name=vde-test-", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_cleanup_with_custom_prefix(self, mock_run):
        """Test cleanup with custom prefix"""
        ps_result = Mock()
        ps_result.stdout = "custom-test-container\n"
        ps_result.returncode = 0
        
        rm_result = Mock()
        rm_result.returncode = 0
        
        mock_run.side_effect = [ps_result, rm_result]
        
        cleanup_test_containers(prefix="custom-test-")
        
        # Verify custom prefix was used
        assert mock_run.call_args_list[0] == call(
            ["docker", "ps", "-a", "--filter", "name=custom-test-", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )


class TestCreateTestVmConfig(unittest.TestCase):
    """Tests for create_test_vm_config function"""
    
    def test_create_basic_config(self):
        """Test creating a basic VM config"""
        config_path = create_test_vm_config("python")
        
        try:
            # Verify file exists
            assert os.path.exists(config_path)
            
            # Verify file content
            with open(config_path, 'r') as f:
                content = f.read()
            
            assert "vm_type: python" in content
            assert "container_name: vde-test-python-" in content
        finally:
            # Cleanup
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_create_config_with_custom_settings(self):
        """Test creating a VM config with custom settings"""
        custom_settings = {
            "memory": "2g",
            "cpus": "2",
            "ports": "8080:8080"
        }
        
        config_path = create_test_vm_config("js", custom_settings)
        
        try:
            # Verify file exists
            assert os.path.exists(config_path)
            
            # Verify file content
            with open(config_path, 'r') as f:
                content = f.read()
            
            assert "vm_type: js" in content
            assert "memory: 2g" in content
            assert "cpus: 2" in content
            assert "ports: 8080:8080" in content
        finally:
            # Cleanup
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_config_file_naming(self):
        """Test that config file has correct naming pattern"""
        config_path = create_test_vm_config("ruby")
        
        try:
            # Verify filename pattern
            filename = os.path.basename(config_path)
            assert filename.startswith("vde-test-config-")
            assert filename.endswith("-ruby.yml")
        finally:
            # Cleanup
            if os.path.exists(config_path):
                os.unlink(config_path)


class TestWaitForCondition(unittest.TestCase):
    """Tests for wait_for_condition function"""
    
    def test_condition_met_immediately(self):
        """Test when condition is met immediately"""
        condition = Mock(return_value=True)
        
        result = wait_for_condition(condition, timeout=5, interval=0.1)
        
        assert result is True
        assert condition.call_count == 1
    
    def test_condition_met_after_delay(self):
        """Test when condition is met after some attempts"""
        condition = Mock(side_effect=[False, False, True])
        
        result = wait_for_condition(condition, timeout=5, interval=0.1)
        
        assert result is True
        assert condition.call_count == 3
    
    def test_condition_timeout(self):
        """Test when condition times out"""
        condition = Mock(return_value=False)
        
        start_time = time.time()
        result = wait_for_condition(condition, timeout=1, interval=0.1)
        elapsed = time.time() - start_time
        
        assert result is False
        assert elapsed >= 1.0
        assert elapsed < 1.5  # Allow some margin
    
    def test_condition_with_custom_interval(self):
        """Test with custom polling interval"""
        call_times = []
        
        def condition():
            call_times.append(time.time())
            return len(call_times) >= 3
        
        result = wait_for_condition(condition, timeout=5, interval=0.2)
        
        assert result is True
        # Verify intervals are approximately correct
        if len(call_times) >= 2:
            interval1 = call_times[1] - call_times[0]
            assert 0.15 < interval1 < 0.3


class TestBeforeScenarioHook(unittest.TestCase):
    """Tests for before_scenario hook"""
    
    @patch('subprocess.run')
    def test_requires_docker_tag_with_docker_available(self, mock_run):
        """Test @requires_docker tag when Docker is available"""
        mock_run.return_value = Mock(returncode=0)
        
        context = Mock()
        scenario = Mock()
        scenario.effective_tags = ["requires_docker"]
        
        before_scenario(context, scenario)
        
        # Verify docker info was called
        mock_run.assert_called_once_with(
            ["docker", "info"],
            capture_output=True,
            check=True,
            timeout=5
        )
        
        # Verify context was initialized
        assert hasattr(context, 'temp_files')
        assert hasattr(context, 'test_containers')
        assert context.cleanup_containers is False
    
    @patch('subprocess.run')
    def test_requires_docker_tag_without_docker(self, mock_run):
        """Test @requires_docker tag when Docker is not available"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'docker')
        
        context = Mock()
        scenario = Mock()
        scenario.effective_tags = ["requires_docker"]
        
        before_scenario(context, scenario)
        
        # Verify scenario was skipped
        scenario.skip.assert_called_once_with("Docker is not available")
    
    def test_cleanup_containers_tag(self):
        """Test @cleanup_containers tag"""
        context = Mock()
        scenario = Mock()
        scenario.effective_tags = ["cleanup_containers"]
        
        before_scenario(context, scenario)
        
        assert context.cleanup_containers is True
    
    def test_no_special_tags(self):
        """Test scenario with no special tags"""
        context = Mock()
        scenario = Mock()
        scenario.effective_tags = []
        
        before_scenario(context, scenario)
        
        assert hasattr(context, 'temp_files')
        assert hasattr(context, 'test_containers')
        assert context.cleanup_containers is False


class TestAfterScenarioHook(unittest.TestCase):
    """Tests for after_scenario hook"""
    
    @patch('subprocess.run')
    @patch('test_utilities.cleanup_test_containers')
    def test_cleanup_containers_when_marked(self, mock_cleanup, mock_run):
        """Test container cleanup when cleanup_containers is True"""
        context = Mock()
        context.cleanup_containers = True
        context.test_containers = []
        context.temp_files = []
        
        scenario = Mock()
        
        after_scenario(context, scenario)
        
        # Verify cleanup was called
        mock_cleanup.assert_called_once_with(prefix="vde-test-")
    
    @patch('test_utilities.cleanup_port_registry')
    @patch('test_utilities.cleanup_docker_volumes')
    @patch('test_utilities.cleanup_docker_networks')
    @patch('test_utilities.cleanup_test_vms')
    @patch('subprocess.run')
    def test_cleanup_specific_containers(self, mock_run, mock_vms, mock_networks, mock_volumes, mock_port):
        """Test cleanup of specific containers tracked in context"""
        mock_run.return_value = Mock(returncode=0)
        
        context = Mock()
        context.cleanup_containers = False
        context.test_containers = ["vde-test-python", "vde-test-js"]
        context.temp_files = []
        
        scenario = Mock()
        
        after_scenario(context, scenario)
        
        # Verify docker rm was called for each container
        assert mock_run.call_count == 2
        assert call(
            ["docker", "rm", "-f", "vde-test-python"],
            capture_output=True,
            check=False
        ) in mock_run.call_args_list
        assert call(
            ["docker", "rm", "-f", "vde-test-js"],
            capture_output=True,
            check=False
        ) in mock_run.call_args_list
    
    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files"""
        # Create actual temp files
        fd1, temp_file1 = tempfile.mkstemp()
        os.close(fd1)
        fd2, temp_file2 = tempfile.mkstemp()
        os.close(fd2)
        
        context = Mock()
        context.cleanup_containers = False
        context.test_containers = []
        context.temp_files = [temp_file1, temp_file2]
        
        scenario = Mock()
        
        after_scenario(context, scenario)
        
        # Verify files were deleted
        assert not os.path.exists(temp_file1)
        assert not os.path.exists(temp_file2)
    
    @patch('subprocess.run')
    def test_cleanup_handles_errors_gracefully(self, mock_run):
        """Test that cleanup errors don't raise exceptions"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'docker')
        
        context = Mock()
        context.cleanup_containers = False
        context.test_containers = ["nonexistent-container"]
        context.temp_files = ["/nonexistent/file.txt"]
        
        scenario = Mock()
        
        # Should not raise exception
        after_scenario(context, scenario)


class TestCleanupTestVms(unittest.TestCase):
    """Tests for cleanup_test_vms function"""
    
    @patch('subprocess.run')
    def test_cleanup_vms_with_vde_command(self, mock_run):
        """Test VM cleanup using VDE remove command"""
        # Mock docker ps output
        ps_result = Mock()
        ps_result.stdout = "vde-test-python\nvde-test-js\n"
        ps_result.returncode = 0
        
        # Mock VDE remove success
        vde_result = Mock()
        vde_result.returncode = 0
        
        # Mock verification (container removed)
        verify_result = Mock()
        verify_result.stdout = ""
        verify_result.returncode = 0
        
        mock_run.side_effect = [ps_result, vde_result, verify_result, vde_result, verify_result]
        
        cleanup_test_vms(prefix="vde-test-")
        
        # Verify docker ps was called
        assert mock_run.call_args_list[0][0][0] == ["docker", "ps", "-a", "--filter", "name=vde-test-", "--format", "{{.Names}}"]
    
    @patch('subprocess.run')
    def test_cleanup_vms_fallback_to_docker(self, mock_run):
        """Test VM cleanup falls back to docker rm when VDE fails"""
        # Mock docker ps output
        ps_result = Mock()
        ps_result.stdout = "vde-test-python\n"
        ps_result.returncode = 0
        
        # Mock VDE remove failure
        vde_result = Mock()
        vde_result.returncode = 1
        
        # Mock docker rm success
        rm_result = Mock()
        rm_result.returncode = 0
        
        # Mock verification
        verify_result = Mock()
        verify_result.stdout = ""
        verify_result.returncode = 0
        
        mock_run.side_effect = [ps_result, vde_result, rm_result, verify_result]
        
        cleanup_test_vms(prefix="vde-test-")
        
        # Verify docker rm was called as fallback
        assert any("docker" in str(call) and "rm" in str(call) for call in mock_run.call_args_list)


class TestCleanupPortRegistry(unittest.TestCase):
    """Tests for cleanup_port_registry function"""
    
    @patch('test_utilities.logger')
    @patch('test_utilities.Path')
    def test_cleanup_port_registry_with_test_entries(self, mock_path, mock_logger):
        """Test cleaning up test entries from port registry"""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            vde_dir = Path(tmpdir) / ".vde"
            vde_dir.mkdir()
            registry_file = vde_dir / "port-registry.json"
            
            # Write test data
            registry_data = {
                "vde-test-python": {"8000": "8000"},
                "vde-test-js": {"3000": "3000"},
                "vde-production-app": {"9000": "9000"}
            }
            with open(registry_file, 'w') as f:
                json.dump(registry_data, f)
            
            # Mock Path to return our temp directory
            mock_path.return_value.parent.parent.parent.parent = Path(tmpdir)
            
            cleanup_port_registry()
            
            # Verify the file was cleaned
            with open(registry_file, 'r') as f:
                cleaned_data = json.load(f)
            
            assert "vde-test-python" not in cleaned_data
            assert "vde-test-js" not in cleaned_data
            assert "vde-production-app" in cleaned_data
    
    @patch('test_utilities.Path')
    def test_cleanup_port_registry_no_file(self, mock_path):
        """Test cleanup when registry file doesn't exist"""
        mock_registry_path = Mock()
        mock_registry_path.exists.return_value = False
        mock_path.return_value.parent.parent.parent.parent.__truediv__.return_value = mock_registry_path
        
        # Should not raise exception
        cleanup_port_registry()


class TestCleanupDockerNetworks(unittest.TestCase):
    """Tests for cleanup_docker_networks function"""
    
    @patch('subprocess.run')
    def test_cleanup_networks(self, mock_run):
        """Test cleaning up Docker networks"""
        # Mock network ls output
        ls_result = Mock()
        ls_result.stdout = "vde-test-network1\nvde-test-network2\n"
        ls_result.returncode = 0
        
        # Mock network rm success
        rm_result = Mock()
        rm_result.returncode = 0
        
        # Mock verification
        verify_result = Mock()
        verify_result.stdout = ""
        verify_result.returncode = 0
        
        mock_run.side_effect = [ls_result, rm_result, verify_result, rm_result, verify_result]
        
        cleanup_docker_networks(prefix="vde-test-")
        
        # Verify network ls was called
        assert mock_run.call_args_list[0][0][0] == ["docker", "network", "ls", "--filter", "name=vde-test-", "--format", "{{.Name}}"]
        
        # Verify at least 2 network rm calls were made (one for each network)
        assert mock_run.call_count >= 3  # ls + 2 rm calls (verification calls may vary)


class TestCleanupDockerVolumes(unittest.TestCase):
    """Tests for cleanup_docker_volumes function"""
    
    @patch('subprocess.run')
    def test_cleanup_volumes(self, mock_run):
        """Test cleaning up Docker volumes"""
        # Mock volume ls output
        ls_result = Mock()
        ls_result.stdout = "vde-test-volume1\nvde-test-volume2\n"
        ls_result.returncode = 0
        
        # Mock volume rm success
        rm_result = Mock()
        rm_result.returncode = 0
        
        # Mock verification
        verify_result = Mock()
        verify_result.stdout = ""
        verify_result.returncode = 0
        
        mock_run.side_effect = [ls_result, rm_result, verify_result, rm_result, verify_result]
        
        cleanup_docker_volumes(prefix="vde-test-")
        
        # Verify volume ls was called
        assert mock_run.call_args_list[0][0][0] == ["docker", "volume", "ls", "--filter", "name=vde-test-", "--format", "{{.Name}}"]
        
        # Verify at least 2 volume rm calls were made (one for each volume)
        assert mock_run.call_count >= 3  # ls + 2 rm calls (verification calls may vary)


class TestRegisterCleanupHandler(unittest.TestCase):
    """Tests for register_cleanup_handler function"""
    
    def test_register_cleanup_handler(self):
        """Test registering a cleanup handler"""
        # Import the module-level list
        import test_utilities
        
        # Clear any existing handlers
        test_utilities._cleanup_handlers.clear()
        
        def my_cleanup():
            pass
        
        register_cleanup_handler(my_cleanup)
        
        assert my_cleanup in test_utilities._cleanup_handlers
    
    def test_register_same_handler_twice(self):
        """Test that registering the same handler twice doesn't duplicate it"""
        import test_utilities
        
        test_utilities._cleanup_handlers.clear()
        
        def my_cleanup():
            pass
        
        register_cleanup_handler(my_cleanup)
        register_cleanup_handler(my_cleanup)
        
        # Should only be registered once
        assert test_utilities._cleanup_handlers.count(my_cleanup) == 1


class TestAfterFeatureHook(unittest.TestCase):
    """Tests for after_feature hook"""
    
    @patch('test_utilities.cleanup_test_vms')
    @patch('test_utilities.cleanup_docker_networks')
    @patch('test_utilities.cleanup_docker_volumes')
    @patch('test_utilities.cleanup_port_registry')
    def test_after_feature_cleanup(self, mock_port, mock_volumes, mock_networks, mock_vms):
        """Test after_feature performs comprehensive cleanup"""
        context = Mock()
        feature = Mock()
        feature.name = "Test Feature"
        
        after_feature(context, feature)
        
        # Verify all cleanup functions were called
        mock_vms.assert_called_once_with(prefix="vde-test-")
        mock_networks.assert_called_once_with(prefix="vde-test-")
        mock_volumes.assert_called_once_with(prefix="vde-test-")
        mock_port.assert_called_once()


class TestBeforeAllHook(unittest.TestCase):
    """Tests for before_all hook"""
    
    @patch('subprocess.run')
    @patch('test_utilities.cleanup_test_vms')
    @patch('test_utilities.cleanup_docker_networks')
    @patch('test_utilities.cleanup_docker_volumes')
    @patch('test_utilities.cleanup_port_registry')
    def test_before_all_setup(self, mock_port, mock_volumes, mock_networks, mock_vms, mock_run):
        """Test before_all performs initial setup and cleanup"""
        mock_run.return_value = Mock(returncode=0)
        
        context = Mock()
        
        before_all(context)
        
        # Verify Docker check was performed
        mock_run.assert_called_once()
        
        # Verify initial cleanup was performed
        mock_vms.assert_called_once_with(prefix="vde-test-")
        mock_networks.assert_called_once_with(prefix="vde-test-")
        mock_volumes.assert_called_once_with(prefix="vde-test-")
        mock_port.assert_called_once()


class TestAfterAllHook(unittest.TestCase):
    """Tests for after_all hook"""
    
    @patch('test_utilities.cleanup_test_vms')
    @patch('test_utilities.cleanup_docker_networks')
    @patch('test_utilities.cleanup_docker_volumes')
    @patch('test_utilities.cleanup_port_registry')
    def test_after_all_cleanup(self, mock_port, mock_volumes, mock_networks, mock_vms):
        """Test after_all performs final cleanup"""
        import test_utilities
        
        # Add some handlers to clear
        test_utilities._cleanup_handlers.append(lambda: None)
        
        context = Mock()
        
        after_all(context)
        
        # Verify all cleanup functions were called
        mock_vms.assert_called_once_with(prefix="vde-test-")
        mock_networks.assert_called_once_with(prefix="vde-test-")
        mock_volumes.assert_called_once_with(prefix="vde-test-")
        mock_port.assert_called_once()
        
        # Verify handlers were cleared
        assert len(test_utilities._cleanup_handlers) == 0


if __name__ == '__main__':
    unittest.main()
