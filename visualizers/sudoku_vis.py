import streamlit as st
import time
from sudoku.sudoku import parse_board, PureBacktracking, BacktrackingMRV, BacktrackingMRVFC, GreedySolver, board_copy, generate_puzzle

async def app():
    st.title("Sudoku Visualizer")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard", "expert"])
        algorithm = st.selectbox("Algorithm", ["Backtracking + MRV + FC", "Backtracking + MRV", "Pure Backtracking", "Greedy / DFS"])
        speed = st.slider("Animation Speed (ms)", 1, 500, 50)
        
        if st.button("Generate New Puzzle"):
            st.session_state.puzzle, _ = generate_puzzle(difficulty)
            st.session_state.running_sudoku = False
            
        if st.button("Solve Puzzle", type="primary"):
            st.session_state.running_sudoku = True
            
    with col2:
        if "puzzle" not in st.session_state:
            st.session_state.puzzle = parse_board('530070000600195000098000060800060003400803001700020006060000280000419005000080079')
            
        board_container = st.empty()
        info_container = st.empty()
        
        # Render function
        def render_board(board, active_cell=None):
            html = "<table style='border-collapse: collapse; margin: auto; font-size: 24px; font-family: monospace; border: 3px solid #ccc; background-color: #2e2e2e; color: white;'>"
            for r in range(9):
                html += "<tr>"
                for c in range(9):
                    val = board[r][c]
                    text = str(val) if val != 0 else "&nbsp;"
                    
                    bg_color = "transparent"
                    if active_cell == (r, c):
                        bg_color = "#4CAF50" if val != 0 else "#f44336"
                        
                    border_right = "3px solid #ccc" if c % 3 == 2 else "1px solid #666"
                    border_bottom = "3px solid #ccc" if r % 3 == 2 else "1px solid #666"
                    
                    html += f"<td style='width: 40px; height: 40px; text-align: center; border-right: {border_right}; border-bottom: {border_bottom}; background-color: {bg_color};'>{text}</td>"
                html += "</tr>"
            html += "</table>"
            board_container.markdown(html, unsafe_allow_html=True)

        board = board_copy(st.session_state.puzzle)
        render_board(board)
        
        if st.session_state.get("running_sudoku", False):
            st.session_state.running_sudoku = False
            
            alg_map = {
                "Pure Backtracking": PureBacktracking,
                "Backtracking + MRV": BacktrackingMRV,
                "Backtracking + MRV + FC": BacktrackingMRVFC,
                "Greedy / DFS": GreedySolver
            }
            solver = alg_map[algorithm]()
            
            gen = solver.solve_visual(board)
            for step in gen:
                if step is True or step is False:
                    break
                r, c, num = step
                render_board(board, active_cell=(r, c))
                info_container.info(f"Steps: {solver.steps} | Backtracks: {solver.backtracks}")
                import asyncio
                await asyncio.sleep(speed / 1000.0)
            
            render_board(board)
            info_container.success(f"Finished! Steps: {solver.steps} | Backtracks: {solver.backtracks}")
