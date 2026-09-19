from typing import Dict, Type, Any
from .agent import Agent
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant

class AgentRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.agent_types = {}
            cls._instance.active_agents = {}
        return cls._instance
        
    def register_type(self, role: str, agent_class: Type[Agent], default_permissions: PermissionSet):
        self.agent_types[role] = {
            "class": agent_class,
            "permissions": default_permissions
        }
        
    def spawn(self, role: str, name: str = None) -> Agent:
        if role not in self.agent_types:
            raise ValueError(f"Unknown agent role: {role}")
            
        config = self.agent_types[role]
        agent_class = config["class"]
        # Make a copy of permissions for the instance
        import copy
        permissions = copy.deepcopy(config["permissions"])
        
        agent = agent_class(role=role, permissions=permissions, name=name)
        self.active_agents[agent.id] = agent
        return agent
        
    def get_agent(self, agent_id: str) -> Agent:
        return self.active_agents.get(agent_id)
        
    def list_agents(self) -> Dict[str, Agent]:
        return self.active_agents

agent_registry = AgentRegistry()
