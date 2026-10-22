"""MCP sunucusu: tools.TOOLS içindeki araçları olduğu gibi yayınlayan ince adaptör.

Çalıştırma (stdio):   python -m powerlab.mcp_server
Claude Desktop yapılandırması için README'ye bak. Hesap mantığı burada YOKTUR.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from . import tools


def build_server() -> MCPServer:
    server = MCPServer(
        name="powerlab",
        instructions=(
            "İstatistiksel güç analizi (tek yönlü ANOVA). Sayıları yalnızca araçlar üretir; "
            "kendi başına N veya güç hesaplama."
        ),
    )

    # Her araç aynı kayıttan gelir; fonksiyon gövdesi yalnızca tools.call'a iletir.
    @server.tool(name="anova_oneway_a_priori", description=tools.TOOLS["anova_oneway_a_priori"]["description"])
    def anova_oneway_a_priori(f: float, alpha: float, power: float, groups: int) -> dict:
        return tools.call("anova_oneway_a_priori", {"f": f, "alpha": alpha, "power": power, "groups": groups})

    @server.tool(name="anova_oneway_post_hoc", description=tools.TOOLS["anova_oneway_post_hoc"]["description"])
    def anova_oneway_post_hoc(f: float, alpha: float, groups: int, n_total: int) -> dict:
        return tools.call("anova_oneway_post_hoc", {"f": f, "alpha": alpha, "groups": groups, "n_total": n_total})

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
