import httpx
from typing import Dict, Optional, Any
from app.core.logging import logger
from app.core.encryption import encryption


class ProxmoxService:
    """Service for interacting with Proxmox VE API"""
    
    def __init__(self, api_url: str, api_token_encrypted: str, verify_ssl: bool = True):
        self.api_url = api_url.rstrip('/')
        self.api_token = encryption.decrypt(api_token_encrypted)
        self.verify_ssl = verify_ssl
        self.headers = {
            "Authorization": f"PVEAPIToken={self.api_token}"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Proxmox server"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/api2/json/version",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Proxmox connection test failed: {e}")
            raise
    
    async def get_nodes(self) -> list:
        """Get list of Proxmox nodes"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/api2/json/nodes",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Proxmox nodes: {e}")
            return []
    
    async def create_vm(
        self,
        node: str,
        vmid: int,
        name: str,
        cores: int,
        memory: int,
        disk_size: int,
        template_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new VM"""
        try:
            vm_config = {
                "vmid": vmid,
                "name": name,
                "cores": cores,
                "memory": memory,
                "scsihw": "virtio-scsi-pci",
                "boot": "order=scsi0",
                "scsi0": f"local-lvm:{disk_size}",
            }
            
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                if template_id:
                    # Clone from template
                    response = await client.post(
                        f"{self.api_url}/api2/json/nodes/{node}/qemu/{template_id}/clone",
                        headers=self.headers,
                        data={"newid": vmid, "name": name},
                        timeout=30.0
                    )
                else:
                    # Create new VM
                    response = await client.post(
                        f"{self.api_url}/api2/json/nodes/{node}/qemu",
                        headers=self.headers,
                        data=vm_config,
                        timeout=30.0
                    )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to create VM: {e}")
            raise
    
    async def start_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Start a VM"""
        return await self._vm_action(node, vmid, "start")
    
    async def stop_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Stop a VM"""
        return await self._vm_action(node, vmid, "stop")
    
    async def reboot_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Reboot a VM"""
        return await self._vm_action(node, vmid, "reboot")
    
    async def suspend_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Suspend a VM"""
        return await self._vm_action(node, vmid, "suspend")
    
    async def resume_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Resume a VM"""
        return await self._vm_action(node, vmid, "resume")
    
    async def delete_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Delete a VM"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.delete(
                    f"{self.api_url}/api2/json/nodes/{node}/qemu/{vmid}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to delete VM {vmid}: {e}")
            raise
    
    async def get_vm_status(self, node: str, vmid: int) -> Dict[str, Any]:
        """Get VM status"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/api2/json/nodes/{node}/qemu/{vmid}/status/current",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to get VM status: {e}")
            return {}
    
    async def _vm_action(self, node: str, vmid: int, action: str) -> Dict[str, Any]:
        """Perform action on VM"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.post(
                    f"{self.api_url}/api2/json/nodes/{node}/qemu/{vmid}/status/{action}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to {action} VM {vmid}: {e}")
            raise
    
    async def get_next_vmid(self) -> int:
        """Get next available VMID"""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/api2/json/cluster/nextid",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return int(data.get("data", 100))
        except Exception as e:
            logger.error(f"Failed to get next VMID: {e}")
            return 100
    
    async def resize_vm(
        self,
        node: str,
        vmid: int,
        cores: Optional[int] = None,
        memory: Optional[int] = None,
        disk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Resize VM resources"""
        try:
            config = {}
            if cores is not None:
                config["cores"] = cores
            if memory is not None:
                config["memory"] = memory
            if disk_size is not None:
                config["scsi0"] = f"local-lvm:{disk_size}"
            
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.put(
                    f"{self.api_url}/api2/json/nodes/{node}/qemu/{vmid}/config",
                    headers=self.headers,
                    data=config,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to resize VM {vmid}: {e}")
            raise
