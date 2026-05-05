import streamlit as st
import time
import networkx as nx
import matplotlib.pyplot as plt
from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph_coloring import color_graph_visual

async def app():
    st.title("Graph Coloring Visualizer")

    col1, col2 = st.columns([1, 2])

    with col1:
        v_num = st.slider("Number of Vertices", 5, 30, 10)
        chance = st.slider("Chance of edge generation", 0.1, 1.0, 0.3)
        c_num = st.slider("Number of colors", 2, 10, 4)
        speed = st.slider("Animation Speed (ms)", 1, 500, 100)

        if st.button("Generate New Graph"):
            st.session_state.graph_obj = generate_graph(v_num, chance)
            # Store stable layout
            G = nx.Graph()
            for vk in st.session_state.graph_obj.get_vertices():
                G.add_node(vk)
            for vk in st.session_state.graph_obj.get_vertices():
                v = st.session_state.graph_obj.get_vertex(vk)
                for neighbor in v.get_neighbors():
                    G.add_edge(vk, neighbor)
            st.session_state.graph_pos = nx.spring_layout(G, seed=42)
            st.session_state.running_graph = False

        if st.button("Solve Graph", type="primary"):
            st.session_state.running_graph = True

    with col2:
        if "graph_obj" not in st.session_state:
            st.session_state.graph_obj = generate_graph(10, 0.3)
            G = nx.Graph()
            for vk in st.session_state.graph_obj.get_vertices():
                G.add_node(vk)
            for vk in st.session_state.graph_obj.get_vertices():
                v = st.session_state.graph_obj.get_vertex(vk)
                for n in v.get_neighbors():
                    G.add_edge(vk, n)
            st.session_state.graph_pos = nx.spring_layout(G, seed=42)

        plot_container = st.empty()
        info_container = st.empty()

        def render_graph(graph_obj, pos, colors_dict=None):
            colors_dict = colors_dict or {}
            G = nx.Graph()

            for vertex_key in graph_obj.get_vertices():
                G.add_node(vertex_key)

            for vertex_key in graph_obj.get_vertices():
                v = graph_obj.get_vertex(vertex_key)
                for neighbor in v.get_neighbors():
                    G.add_edge(vertex_key, neighbor)

            color_map = []
            palette = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4']

            for node in G.nodes():
                if node in colors_dict:
                    color_idx = colors_dict[node] % len(palette)
                    color_map.append(palette[color_idx])
                else:
                    color_map.append('#cccccc')

            fig, ax = plt.subplots(figsize=(6, 5))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#0e1117')
            nx.draw(G, pos, ax=ax, node_color=color_map, with_labels=True, node_size=600, font_color='white', font_weight='bold', edge_color='#666')

            plot_container.pyplot(fig)
            plt.close(fig)

        if st.session_state.get("running_graph", False):
            st.session_state.running_graph = False

            gen = color_graph_visual(c_num, st.session_state.graph_obj)

            steps = 0
            final_state = {}
            for colors_state in gen:
                steps += 1
                final_state = colors_state
                if steps % 1 == 0:
                    render_graph(st.session_state.graph_obj, st.session_state.graph_pos, colors_state)
                    info_container.info(f"Steps: {steps}")
                    import asyncio
                    await asyncio.sleep(speed / 1000.0)

            render_graph(st.session_state.graph_obj, st.session_state.graph_pos, final_state)
            if len(final_state) == len(list(st.session_state.graph_obj.get_vertices())):
                info_container.success(f"Graph colored successfully in {steps} steps using {c_num} colors max!")
            else:
                info_container.error(f"Failed to color graph with {c_num} colors.")
        else:
            render_graph(st.session_state.graph_obj, st.session_state.graph_pos)
