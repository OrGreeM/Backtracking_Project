import streamlit as st
import time
from Maze.generator import MazeGenerator
from Maze.solvers import MazeSolver, SmartMazeSolver
from Maze.models import Point



async def app():
    st.title("Maze")

    col1, col2 = st.columns([1, 2])

    with col1:
        width = st.slider("Width", 11, 51, 21, step=2)
        height = st.slider("Height", 11, 51, 21, step=2)
        algorithm = st.selectbox("Algorithm", ["DFS (Basic)", "Smart (Heuristic)"])
        speed = st.slider("Animation Speed (ms)", 1, 100, 20)

        import copy
        if st.button("Generate New Maze"):
            generator = MazeGenerator(height, width)
            st.session_state.original_maze = generator.generate()
            st.session_state.maze = copy.deepcopy(st.session_state.original_maze)
            st.session_state.running_maze = False

        if st.button("Solve Maze", type="primary"):
            if "original_maze" in st.session_state:
                st.session_state.maze = copy.deepcopy(st.session_state.original_maze)
            st.session_state.running_maze = True

    with col2:
        if "original_maze" not in st.session_state:
            generator = MazeGenerator(21, 21)
            st.session_state.original_maze = generator.generate()
            import copy
            st.session_state.maze = copy.deepcopy(st.session_state.original_maze)
        board_container = st.empty()
        info_container = st.empty()

        def render_maze(maze, current=None, visited=None, path=None):
            import numpy as np
            visited = visited or set()
            path = path or []
            path_set = set(path)

            img = np.zeros((maze.height, maze.width, 3), dtype=np.uint8)

            for r in range(maze.height):
                for c in range(maze.width):
                    if maze.grid[r][c] == 1:
                        img[r, c] = [34, 34, 34]
                    else:
                        img[r, c] = [221, 221, 221]

            for p in visited:
                img[p.x, p.y] = [179, 229, 252]

            for p in path_set:
                img[p.x, p.y] = [33, 150, 243]

            if current:
                img[current.x, current.y] = [255, 235, 59]

            img[maze.start_point.x, maze.start_point.y] = [76, 175, 80]
            img[maze.end_point.x, maze.end_point.y] = [244, 67, 54]

            # Scale image up without blurring
            scale = 12
            img = np.repeat(np.repeat(img, scale, axis=0), scale, axis=1)

            board_container.image(img, output_format="PNG", use_column_width=False)

        render_maze(st.session_state.maze)

        if st.session_state.get("running_maze", False):
            st.session_state.running_maze = False

            if algorithm == "DFS (Basic)":
                solver = MazeSolver(st.session_state.maze)
            else:
                solver = SmartMazeSolver(st.session_state.maze)

            gen = solver.solve_generator()
            steps = 0
            for step in gen:
                if step is True or step is False:
                    break
                steps += 1
                if steps % 2 == 0:
                    render_maze(st.session_state.maze, step["current"], step["visited"], step["path"])
                    info_container.info(f"Explored cells: {len(step['visited'])}")
                    import asyncio
                    await asyncio.sleep(speed / 1000.0)

            render_maze(st.session_state.maze, None, solver.visited, solver.path)
            info_container.success(f"Finished! Explored cells: {len(solver.visited)} | Path length: {len(solver.path)}")
