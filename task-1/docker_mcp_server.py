"""
docker_mcp_server.py

A Model Context Protocol (MCP) server that exposes Docker operations as
tools. Talks to the Docker daemon via the docker SDK (docker.from_env()),
same as the `docker` CLI does — no separate container required to run
this; it's a plain Python process that connects to your existing Docker
socket.

Run directly:
    python3 docker_mcp_server.py

Or point your agent's mcp_config.json at it:
    "docker": {
      "transport": "stdio",
      "command": "python3",
      "args": ["/absolute/path/to/docker_mcp_server.py"]
    }
"""
import docker
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("docker-mcp-server")
client = docker.from_env()


@mcp.tool()
def list_containers(all: bool = True) -> list[dict]:
    """List Docker containers.

    Args:
        all: if True, include stopped containers too. If False, only
             running ones.
    """
    containers = client.containers.list(all=all)
    return [
        {
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else c.image.short_id,
            "status": c.status,
            "ports": c.ports,
        }
        for c in containers
    ]


@mcp.tool()
def container_logs(name_or_id: str, tail: int = 100) -> str:
    """Get recent logs from a container.

    Args:
        name_or_id: container name or ID
        tail: number of most recent lines to return (default 100)
    """
    container = client.containers.get(name_or_id)
    logs = container.logs(tail=tail).decode("utf-8", errors="replace")
    return logs


@mcp.tool()
def start_container(name_or_id: str) -> str:
    """Start a stopped container."""
    container = client.containers.get(name_or_id)
    container.start()
    return f"Started {container.name} ({container.short_id})"


@mcp.tool()
def stop_container(name_or_id: str, timeout: int = 10) -> str:
    """Stop a running container.

    Args:
        name_or_id: container name or ID
        timeout: seconds to wait for graceful stop before killing it
    """
    container = client.containers.get(name_or_id)
    container.stop(timeout=timeout)
    return f"Stopped {container.name} ({container.short_id})"


@mcp.tool()
def restart_container(name_or_id: str, timeout: int = 10) -> str:
    """Restart a container."""
    container = client.containers.get(name_or_id)
    container.restart(timeout=timeout)
    return f"Restarted {container.name} ({container.short_id})"


@mcp.tool()
def remove_container(name_or_id: str, force: bool = False) -> str:
    """Remove a container.

    Args:
        name_or_id: container name or ID
        force: if True, remove even if it's currently running
    """
    container = client.containers.get(name_or_id)
    container.remove(force=force)
    return f"Removed {name_or_id}"


@mcp.tool()
def container_stats(name_or_id: str) -> dict:
    """Get a live resource-usage snapshot (CPU, memory, network) for a
    running container."""
    container = client.containers.get(name_or_id)
    stats = container.stats(stream=False)
    mem = stats.get("memory_stats", {})
    return {
        "name": container.name,
        "status": container.status,
        "memory_usage_bytes": mem.get("usage"),
        "memory_limit_bytes": mem.get("limit"),
        "pids": stats.get("pids_stats", {}).get("current"),
    }


@mcp.tool()
def list_images() -> list[dict]:
    """List Docker images available locally."""
    images = client.images.list()
    return [
        {"id": img.short_id, "tags": img.tags, "size_mb": round(img.attrs["Size"] / 1_000_000, 1)}
        for img in images
    ]


@mcp.tool()
def pull_image(repository: str, tag: str = "latest") -> str:
    """Pull an image from a registry (e.g. Docker Hub).

    Args:
        repository: image name, e.g. 'nginx' or 'myregistry.com/myimage'
        tag: image tag (default 'latest')
    """
    image = client.images.pull(repository, tag=tag)
    return f"Pulled {repository}:{tag} ({image.short_id})"


if __name__ == "__main__":
    mcp.run(transport="stdio")
