import streamlit as st
import time
import pandas as pd
import copy
from sudoku.sudoku import generate_puzzle as sudoku_generate, board_copy as sudoku_board_copy
from sudoku.sudoku import PureBacktracking as SudokuDFS, BacktrackingMRV as SudokuMRV, BacktrackingMRVFC as SudokuFC, GreedySolver as SudokuGreedy
from Maze.generator import MazeGenerator
from Maze.solvers import MazeSolver, SmartMazeSolver
from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph_coloring import main as solve_graph

async def app():
    st.title("Algorithm Benchmarks")
    st.markdown("Run automated benchmarks across multiple instances to compare algorithm performance.")
    
    domain = st.selectbox("Select Domain to Benchmark", ["Sudoku", "Maze Solver", "Graph Coloring", "Crossword Puzzle"])
    
    if domain == "Crossword Puzzle":
        st.info("🚧 Coming Soon: The Crossword algorithm is not yet implemented in the core logic.")
        return
        
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        num_executions = st.number_input("Executions per Algorithm", 1, 500, 10)
        
        if domain == "Sudoku":
            difficulty = st.selectbox("Sudoku Difficulty", ["easy", "medium", "hard", "expert"])
        elif domain == "Maze Solver":
            m_width = st.slider("Maze Width", 11, 51, 21, step=2)
            m_height = st.slider("Maze Height", 11, 51, 21, step=2)
        elif domain == "Graph Coloring":
            v_num = st.slider("Number of Vertices", 5, 30, 10)
            chance = st.slider("Edge Chance", 0.1, 1.0, 0.3)
            c_num = st.slider("Colors", 2, 10, 4)
            
        if st.button("Run Benchmarks", type="primary"):
            st.session_state.running_bench = True
            
    with col2:
        if st.session_state.get("running_bench", False):
            st.session_state.running_bench = False
            progress_bar = st.progress(0)
            status = st.empty()
            
            results = []
            
            if domain == "Sudoku":
                algorithms = {
                    "Pure DFS": SudokuDFS,
                    "MRV": SudokuMRV,
                    "MRV + FC": SudokuFC,
                    "Greedy": SudokuGreedy
                }
                for i in range(int(num_executions)):
                    puzzle, _ = sudoku_generate(difficulty)
                    for name, AlgClass in algorithms.items():
                        board = sudoku_board_copy(puzzle)
                        alg = AlgClass()
                        t0 = time.perf_counter()
                        solved = alg.solve(board)
                        elapsed = (time.perf_counter() - t0) * 1000
                        results.append({
                            "Algorithm": name,
                            "Iteration": i,
                            "Time (ms)": elapsed,
                            "Steps": alg.steps,
                            "Backtracks": alg.backtracks,
                            "Solved": solved
                        })
                    progress = (i + 1) / int(num_executions)
                    progress_bar.progress(progress)
                    status.text(f"Running iteration {i+1}/{int(num_executions)}...")
                    import asyncio
                    await asyncio.sleep(0.01)
                    
            elif domain == "Maze Solver":
                algorithms = {
                    "DFS (Basic)": MazeSolver,
                    "Smart (Heuristic)": SmartMazeSolver
                }
                for i in range(int(num_executions)):
                    generator = MazeGenerator(m_height, m_width)
                    maze = generator.generate()
                    for name, AlgClass in algorithms.items():
                        test_maze = copy.deepcopy(maze)
                        alg = AlgClass(test_maze)
                        t0 = time.perf_counter()
                        path = alg.solve()
                        elapsed = (time.perf_counter() - t0) * 1000
                        results.append({
                            "Algorithm": name,
                            "Iteration": i,
                            "Time (ms)": elapsed,
                            "Explored Cells": len(alg.visited),
                            "Path Length": len(path) if path else 0
                        })
                    progress = (i + 1) / int(num_executions)
                    progress_bar.progress(progress)
                    status.text(f"Running iteration {i+1}/{int(num_executions)}...")
                    import asyncio
                    await asyncio.sleep(0.01)

            elif domain == "Graph Coloring":
                for i in range(int(num_executions)):
                    base_graph = generate_graph(v_num, chance)
                    
                    t0 = time.perf_counter()
                    _, colored = solve_graph(0, 0, c_num, graph=copy.deepcopy(base_graph))
                    elapsed = (time.perf_counter() - t0) * 1000
                    
                    results.append({
                        "Algorithm": "Backtracking",
                        "Iteration": i,
                        "Time (ms)": elapsed,
                        "Solved": bool(colored)
                    })
                    
                    progress = (i + 1) / int(num_executions)
                    progress_bar.progress(progress)
                    status.text(f"Running iteration {i+1}/{int(num_executions)}...")
                    import asyncio
                    await asyncio.sleep(0.01)
                    
            status.success("Benchmarking complete!")
            df = pd.DataFrame(results)
            
            st.subheader("Average Performance")
            if domain == "Sudoku":
                avg_df = df.groupby("Algorithm")[["Time (ms)", "Steps", "Backtracks"]].mean().reset_index()
                st.dataframe(avg_df)
                st.subheader("Steps Comparison")
                st.bar_chart(avg_df.set_index("Algorithm")["Steps"])
                st.subheader("Execution Time (ms) Comparison")
                st.bar_chart(avg_df.set_index("Algorithm")["Time (ms)"])
            elif domain == "Maze Solver":
                avg_df = df.groupby("Algorithm")[["Time (ms)", "Explored Cells", "Path Length"]].mean().reset_index()
                st.dataframe(avg_df)
                st.subheader("Explored Cells Comparison")
                st.bar_chart(avg_df.set_index("Algorithm")["Explored Cells"])
                st.subheader("Execution Time (ms) Comparison")
                st.bar_chart(avg_df.set_index("Algorithm")["Time (ms)"])
            elif domain == "Graph Coloring":
                avg_df = df.groupby("Algorithm")[["Time (ms)", "Solved"]].mean().reset_index()
                st.dataframe(avg_df)
                st.subheader("Execution Time (ms)")
                st.bar_chart(avg_df.set_index("Algorithm")["Time (ms)"])
