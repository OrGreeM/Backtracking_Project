import asyncio
import streamlit as st

st.set_page_config(page_title="Backtracking Visualizer", layout="wide")

# Sidebar navigation
st.sidebar.title("Algorithms")
pages = {
    "Maze Solver": "visualizers.maze_vis",
    "Sudoku Solver": "visualizers.sudoku_vis",
    "Graph Coloring": "visualizers.graph_vis",
    "Benchmark Comparisons": "visualizers.benchmark_vis",
}

selection = st.sidebar.radio("Select an application", list(pages.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("### Coming Soon")
st.sidebar.markdown("- Crossword Puzzle")
st.sidebar.markdown("- N-Queens")

# Dynamically import and run the selected page
import importlib

if selection == "Maze Solver":
    import visualizers.maze_vis as page
    asyncio.run(page.app())
elif selection == "Sudoku Solver":
    import visualizers.sudoku_vis as page
    asyncio.run(page.app())
elif selection == "Graph Coloring":
    import visualizers.graph_vis as page
    asyncio.run(page.app())
elif selection == "Benchmark Comparisons":
    import visualizers.benchmark_vis as page
    asyncio.run(page.app())
