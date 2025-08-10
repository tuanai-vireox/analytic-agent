"""
Tests for analysis API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_analysis(client: TestClient, sample_analysis_request):
    """Test creating a new analysis task."""
    response = client.post("/api/v1/analysis/", json=sample_analysis_request)
    
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] in ["pending", "processing", "completed", "failed"]
    assert "message" in data


def test_get_analysis_task(client: TestClient, sample_analysis_request):
    """Test getting an analysis task."""
    # First create a task
    create_response = client.post("/api/v1/analysis/", json=sample_analysis_request)
    task_id = create_response.json()["task_id"]
    
    # Then get the task
    response = client.get(f"/api/v1/analysis/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["query"] == sample_analysis_request["query"]


def test_get_nonexistent_analysis_task(client: TestClient):
    """Test getting a non-existent analysis task."""
    response = client.get("/api/v1/analysis/nonexistent-task-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_analysis_status(client: TestClient, sample_analysis_request):
    """Test getting analysis task status."""
    # First create a task
    create_response = client.post("/api/v1/analysis/", json=sample_analysis_request)
    task_id = create_response.json()["task_id"]
    
    # Then get the status
    response = client.get(f"/api/v1/analysis/{task_id}/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert "status" in data
    assert "created_at" in data


def test_list_analysis_tasks(client: TestClient, sample_analysis_request):
    """Test listing analysis tasks."""
    # Create a task first
    client.post("/api/v1/analysis/", json=sample_analysis_request)
    
    # Then list all tasks
    response = client.get("/api/v1/analysis/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_cancel_analysis_task(client: TestClient, sample_analysis_request):
    """Test canceling an analysis task."""
    # First create a task
    create_response = client.post("/api/v1/analysis/", json=sample_analysis_request)
    task_id = create_response.json()["task_id"]
    
    # Then cancel the task
    response = client.delete(f"/api/v1/analysis/{task_id}")
    
    assert response.status_code == 204


def test_invalid_analysis_request(client: TestClient):
    """Test creating an analysis with invalid data."""
    invalid_request = {
        "query": "",  # Empty query
        "analysis_type": "invalid_type"  # Invalid analysis type
    }
    
    response = client.post("/api/v1/analysis/", json=invalid_request)
    
    assert response.status_code == 422  # Validation error 