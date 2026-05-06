import asyncio

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph_coloring import color_graph as bt_color_graph
from graph_coloring.graph_coloring_baselines import dfs_color, greedy_color
from graph_coloring.graph_coloring_optimized import color_graph as mrv_fc_color_graph
from graph_coloring.visualize import COLOR_PALETTE, UNCOLORED, simple_bt_steps, to_networkx


async def app():
    st.title("Graph Coloring Visualizer")

    col1, col2 = st.columns([1, 2])

    with col1:
        algorithm = st.selectbox(
            "Algorithm",
            ["Simple Backtracking", "MRV + FC", "Greedy (Welsh-Powell)", "DFS"],
        )
        v_num = st.slider("Number of Vertices", 5, 30, 10)
        chance = st.slider("Chance of edge generation", 0.1, 1.0, 0.3)
        c_num = st.slider("Number of colors", 2, 10, 4)

        speed = 100
        if algorithm == "Simple Backtracking":
            speed = st.slider("Animation Speed (ms)", 1, 500, 100)
            st.caption("Step-by-step animation plays on Solve.")

        if st.button("Generate New Graph"):
            st.session_state.graph_obj = generate_graph(v_num, chance)
            nx_g = to_networkx(st.session_state.graph_obj)
            st.session_state.graph_pos = nx.spring_layout(nx_g, seed=42)
            st.session_state.running_graph = False
            st.session_state.last_coloring = None

        btn_label = (
            "Solve (Step-by-step)"
            if algorithm == "Simple Backtracking"
            else "Solve"
        )
        if st.button(btn_label, type="primary"):
            st.session_state.running_graph = True
            st.session_state.graph_algorithm = algorithm
            st.session_state.graph_c_num = c_num
            st.session_state.graph_speed = speed

    with col2:
        if "graph_obj" not in st.session_state:
            st.session_state.graph_obj = generate_graph(v_num, chance)
            nx_g = to_networkx(st.session_state.graph_obj)
            st.session_state.graph_pos = nx.spring_layout(nx_g, seed=42)
            st.session_state.last_coloring = None

        plot_placeholder = st.empty()
        info_placeholder = st.empty()

        def render_graph(graph_obj, pos, colors_dict=None, current_vertex=None):
            colors_dict = colors_dict or {}
            nx_g = to_networkx(graph_obj)

            node_colors, edge_colors, edge_widths = [], [], []
            for node in nx_g.nodes():
                c = colors_dict.get(node)
                node_colors.append(
                    COLOR_PALETTE[c % len(COLOR_PALETTE)] if c is not None else UNCOLORED
                )
                if node == current_vertex:
                    edge_colors.append("#ffffff")
                    edge_widths.append(3.5)
                else:
                    edge_colors.append("#555555")
                    edge_widths.append(1.0)

            fig, ax = plt.subplots(figsize=(6, 5))
            fig.patch.set_facecolor("#0e1117")
            ax.set_facecolor("#0e1117")
            ax.set_axis_off()

            nx.draw_networkx_edges(nx_g, pos, ax=ax, edge_color="#666666", width=1.5)
            nx.draw_networkx_nodes(
                nx_g, pos, ax=ax,
                node_color=node_colors, node_size=700,
                edgecolors=edge_colors, linewidths=edge_widths,
            )
            nx.draw_networkx_labels(
                nx_g, pos, ax=ax,
                font_size=10, font_color="white", font_weight="bold",
            )

            plot_placeholder.pyplot(fig)
            plt.close(fig)

        if st.session_state.get("running_graph", False):
            st.session_state.running_graph = False
            alg = st.session_state.get("graph_algorithm", "Simple Backtracking")
            k = st.session_state.get("graph_c_num", c_num)
            spd = st.session_state.get("graph_speed", 100)
            graph_obj = st.session_state.graph_obj
            pos = st.session_state.graph_pos
            n_vertices = len(list(graph_obj.get_vertices()))

            if alg == "Simple Backtracking":
                gen = simple_bt_steps(k, graph_obj)
                steps = 0
                final_colors = {}
                for current_key, colors_state in gen:
                    steps += 1
                    final_colors = colors_state
                    render_graph(graph_obj, pos, colors_state, current_key)
                    info_placeholder.info(f"Steps: {steps}")
                    await asyncio.sleep(spd / 1000.0)

                solved = len(final_colors) == n_vertices
                st.session_state.last_coloring = final_colors if solved else {}
                render_graph(graph_obj, pos, st.session_state.last_coloring)
                if solved:
                    used = len(set(final_colors.values()))
                    info_placeholder.success(
                        f"Colored in {steps} steps using {used} color(s)!"
                    )
                else:
                    info_placeholder.error(f"Cannot color this graph with {k} colors.")

            else:
                if alg == "MRV + FC":
                    result = mrv_fc_color_graph(k, graph_obj)
                elif alg == "Greedy (Welsh-Powell)":
                    result = greedy_color(k, graph_obj)
                else:
                    result = dfs_color(k, graph_obj)

                st.session_state.last_coloring = result or {}
                render_graph(graph_obj, pos, st.session_state.last_coloring)
                if result:
                    used = len(set(result.values()))
                    info_placeholder.success(
                        f"Colored successfully using {used} color(s)!"
                    )
                else:
                    info_placeholder.error(f"Cannot color this graph with {k} colors.")

        else:
            render_graph(
                st.session_state.graph_obj,
                st.session_state.graph_pos,
                st.session_state.get("last_coloring"),
            )
