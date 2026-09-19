from typing import Optional, Any
from .base import BaseTool
from galaxy.core.permissions import Permission
from galaxy.security.approval import RiskTier

class BrowserNavigateTool(BaseTool):
    name = "browser_navigate"
    description = "Navigate browser to a URL"
    risk_level = RiskTier.MEDIUM
    required_permission = Permission.BROWSER_NAVIGATE
    
    def get_scope(self, url: str, **kwargs) -> Optional[str]:
        # simplified scope: domain extraction could be better
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
        
    async def _execute(self, agent_id: str, url: str, **kwargs) -> Any:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)
                content = await page.content()
                await browser.close()
                return {"content": content[:10000] + "..." if len(content) > 10000 else content} # Simple trunc for now
        except Exception as e:
            return {"error": str(e)}
