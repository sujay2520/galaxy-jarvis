from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from galaxy.core.permissions import permission_engine, Permission
from galaxy.security.approval import approval_system, RiskTier

class BaseTool(ABC):
    name: str = ""
    description: str = ""
    risk_level: RiskTier = RiskTier.LOW
    required_permission: Optional[Permission] = None

    async def execute(self, agent_id: str, **kwargs) -> Any:
        # Check permissions
        scope = self.get_scope(**kwargs)
        if self.required_permission:
            if not permission_engine.check(agent_id, self.required_permission, scope):
                return {"error": f"Permission denied: {self.required_permission} for {scope}"}
        
        # Check approval
        approved = await approval_system.request_approval(
            agent_id, 
            self.name, 
            kwargs, 
            self.risk_level
        )
        if not approved:
            return {"error": f"Action denied by approval system: {self.name}"}
            
        try:
            return await self._execute(agent_id, **kwargs)
        except Exception as e:
            return {"error": str(e)}

    @abstractmethod
    def get_scope(self, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    async def _execute(self, agent_id: str, **kwargs) -> Any:
        pass
