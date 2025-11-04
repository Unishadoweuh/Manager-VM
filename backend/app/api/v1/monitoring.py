from fastapi import APIRouter


router = APIRouter(prefix="/monitoring")


@router.get("/nodes")
async def get_nodes_status():
    """Get status of all Proxmox nodes"""
    # TODO: Implement Proxmox node monitoring
    return {"nodes": []}


@router.get("/node/{node_id}/metrics")
async def get_node_metrics(node_id: int):
    """Get metrics for a specific node"""
    # TODO: Implement node metrics retrieval
    return {"metrics": {}}
