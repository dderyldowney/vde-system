"""
Unit tests for docker_helpers.py

These tests use mocks to simulate Docker command outputs without requiring actual Docker.
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json

# Import the helpers we're testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'features' / 'steps'))

from docker_helpers import (
    verify_container_running,
    verify_container_state,
    get_container_port,
    verify_container_network,
    wait_for_container_healthy,
    DockerVerificationError
)


class TestVerifyContainerRunning(unittest.TestCase):
    """Tests for verify_container_running function."""
    
    @patch('docker_helpers.subprocess.run')
    def test_container_running_success(self, mock_run):
        """Test successful verification of running container."""
        mock_output = json.dumps({
            'ID': 'abc123',
            'Image': 'nginx:latest',
            'Status': 'Up 5 minutes',
            'Names': 'my-nginx'
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output + '\n',
            stderr='',
            returncode=0
        )
        
        result = verify_container_running('my-nginx')
        
        self.assertEqual(result['ID'], 'abc123')
        self.assertEqual(result['Image'], 'nginx:latest')
        self.assertEqual(result['Names'], 'my-nginx')
        mock_run.assert_called_once()
    
    @patch('docker_helpers.subprocess.run')
    def test_container_not_running(self, mock_run):
        """Test when container is not running (empty output)."""
        mock_run.return_value = MagicMock(
            stdout='',
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_running('nonexistent')
        
        self.assertIn('not running', str(ctx.exception))
    
    @patch('docker_helpers.subprocess.run')
    def test_docker_command_fails(self, mock_run):
        """Test when docker ps command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'docker ps', stderr='Docker daemon not running'
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_running('my-container')
        
        self.assertIn('failed', str(ctx.exception))
    
    @patch('docker_helpers.subprocess.run')
    def test_timeout(self, mock_run):
        """Test when docker ps command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired('docker ps', 10)
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_running('my-container')
        
        self.assertIn('timed out', str(ctx.exception))


class TestVerifyContainerState(unittest.TestCase):
    """Tests for verify_container_state function."""
    
    @patch('docker_helpers.subprocess.run')
    def test_state_matches(self, mock_run):
        """Test when container state matches expected."""
        mock_output = json.dumps({
            'Status': 'running',
            'Running': True,
            'Paused': False,
            'Restarting': False,
            'OOMKilled': False,
            'Dead': False,
            'Pid': 12345,
            'ExitCode': 0
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        result = verify_container_state('my-container', 'running')
        
        self.assertEqual(result['Status'], 'running')
        self.assertTrue(result['Running'])
    
    @patch('docker_helpers.subprocess.run')
    def test_state_mismatch(self, mock_run):
        """Test when container state doesn't match expected."""
        mock_output = json.dumps({
            'Status': 'exited',
            'Running': False,
            'ExitCode': 1
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_state('my-container', 'running')
        
        self.assertIn('exited', str(ctx.exception))
        self.assertIn('expected', str(ctx.exception))
    
    @patch('docker_helpers.subprocess.run')
    def test_case_insensitive_match(self, mock_run):
        """Test that state comparison is case-insensitive."""
        mock_output = json.dumps({'Status': 'Running'})
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        # Should not raise - case insensitive
        result = verify_container_state('my-container', 'RUNNING')
        self.assertEqual(result['Status'], 'Running')


class TestGetContainerPort(unittest.TestCase):
    """Tests for get_container_port function."""
    
    @patch('docker_helpers.subprocess.run')
    def test_ipv4_port_mapping(self, mock_run):
        """Test extracting port from IPv4 mapping."""
        mock_run.return_value = MagicMock(
            stdout='0.0.0.0:8080\n',
            stderr='',
            returncode=0
        )
        
        port = get_container_port('my-container', 80)
        
        self.assertEqual(port, 8080)
    
    @patch('docker_helpers.subprocess.run')
    def test_ipv6_port_mapping(self, mock_run):
        """Test extracting port from IPv6 mapping."""
        mock_run.return_value = MagicMock(
            stdout='[::]:9000\n',
            stderr='',
            returncode=0
        )
        
        port = get_container_port('my-container', 80)
        
        self.assertEqual(port, 9000)
    
    @patch('docker_helpers.subprocess.run')
    def test_no_port_mapping(self, mock_run):
        """Test when no port mapping exists."""
        mock_run.return_value = MagicMock(
            stdout='',
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            get_container_port('my-container', 80)
        
        self.assertIn('No port mapping', str(ctx.exception))
    
    @patch('docker_helpers.subprocess.run')
    def test_invalid_port_format(self, mock_run):
        """Test when port output has invalid format."""
        mock_run.return_value = MagicMock(
            stdout='invalid-format\n',
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            get_container_port('my-container', 80)
        
        self.assertIn('Invalid port format', str(ctx.exception))


class TestVerifyContainerNetwork(unittest.TestCase):
    """Tests for verify_container_network function."""
    
    @patch('docker_helpers.subprocess.run')
    def test_container_on_network(self, mock_run):
        """Test when container is on the specified network."""
        mock_output = json.dumps({
            'bridge': {
                'IPAddress': '172.17.0.2',
                'Gateway': '172.17.0.1',
                'NetworkID': 'abc123'
            },
            'my-network': {
                'IPAddress': '172.18.0.2',
                'Gateway': '172.18.0.1',
                'NetworkID': 'def456'
            }
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        result = verify_container_network('my-container', 'my-network')
        
        self.assertEqual(result['IPAddress'], '172.18.0.2')
        self.assertEqual(result['NetworkID'], 'def456')
    
    @patch('docker_helpers.subprocess.run')
    def test_container_not_on_network(self, mock_run):
        """Test when container is not on the specified network."""
        mock_output = json.dumps({
            'bridge': {
                'IPAddress': '172.17.0.2'
            }
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_network('my-container', 'my-network')
        
        self.assertIn('not attached', str(ctx.exception))
        self.assertIn('bridge', str(ctx.exception))  # Shows available networks
    
    @patch('docker_helpers.subprocess.run')
    def test_no_networks(self, mock_run):
        """Test when container has no networks."""
        mock_output = json.dumps({})
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            verify_container_network('my-container', 'my-network')
        
        self.assertIn('none', str(ctx.exception))


class TestWaitForContainerHealthy(unittest.TestCase):
    """Tests for wait_for_container_healthy function."""
    
    @patch('docker_helpers.subprocess.run')
    @patch('docker_helpers.time.sleep')
    def test_immediately_healthy(self, mock_sleep, mock_run):
        """Test when container is immediately healthy."""
        mock_output = json.dumps({
            'Status': 'healthy',
            'FailingStreak': 0,
            'Log': []
        })
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr='',
            returncode=0
        )
        
        result = wait_for_container_healthy('my-container', timeout=10)
        
        self.assertEqual(result['Status'], 'healthy')
        mock_sleep.assert_not_called()  # No waiting needed
    
    @patch('docker_helpers.subprocess.run')
    @patch('docker_helpers.time.sleep')
    @patch('docker_helpers.time.time')
    def test_becomes_healthy_after_wait(self, mock_time, mock_sleep, mock_run):
        """Test when container becomes healthy after polling."""
        # Simulate time progression
        mock_time.side_effect = [0, 1, 2, 3]  # start, check1, check2, check3
        
        # First two checks: starting, then healthy
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps({'Status': 'starting'}), returncode=0),
            MagicMock(stdout=json.dumps({'Status': 'healthy'}), returncode=0)
        ]
        
        result = wait_for_container_healthy('my-container', timeout=30)
        
        self.assertEqual(result['Status'], 'healthy')
        self.assertEqual(mock_sleep.call_count, 1)  # Slept once between checks
    
    @patch('docker_helpers.subprocess.run')
    @patch('docker_helpers.time.sleep')
    @patch('docker_helpers.time.time')
    def test_timeout_waiting_for_healthy(self, mock_time, mock_sleep, mock_run):
        """Test timeout when container never becomes healthy."""
        # Simulate time progression past timeout
        # Need enough values for: start_time, while condition checks, and final elapsed calculation
        mock_time.side_effect = [0, 10, 20, 31, 31]  # Exceeds 30s timeout, extra for elapsed
        
        mock_run.return_value = MagicMock(
            stdout=json.dumps({'Status': 'starting'}),
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            wait_for_container_healthy('my-container', timeout=30)
        
        self.assertIn('did not become healthy', str(ctx.exception))
        self.assertIn('starting', str(ctx.exception))  # Shows last status
    
    @patch('docker_helpers.subprocess.run')
    def test_no_healthcheck_defined(self, mock_run):
        """Test when container has no healthcheck."""
        mock_run.return_value = MagicMock(
            stdout='<no value>',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            wait_for_container_healthy('my-container')
        
        self.assertIn('does not have a healthcheck', str(ctx.exception))
    
    @patch('docker_helpers.subprocess.run')
    def test_null_healthcheck(self, mock_run):
        """Test when healthcheck returns null."""
        mock_run.return_value = MagicMock(
            stdout='null',
            returncode=0
        )
        
        with self.assertRaises(DockerVerificationError) as ctx:
            wait_for_container_healthy('my-container')
        
        self.assertIn('does not have a healthcheck', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
