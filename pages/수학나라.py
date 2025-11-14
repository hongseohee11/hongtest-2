import streamlit as st
import streamlit.components.v1 as components
import random
import json

# Sudoku 생성 & 검증 함수들
def is_valid(board, row, col, num):
    """Check if num is valid at board[row][col]"""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[i][col] for i in range(9)]:
        return False
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    return True

def solve_sudoku(board):
    """Solve sudoku using backtracking"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_solution():
    """Generate a complete valid sudoku solution"""
    board = [[0]*9 for _ in range(9)]
    # Fill diagonal 3x3 boxes (these don't conflict)
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[box*3 + i][box*3 + j] = nums[i*3 + j]
    # Solve the rest
    solve_sudoku(board)
    return board

def generate_puzzle(solution, blanks):
    """Remove 'blanks' cells from solution to create puzzle"""
    puzzle = [row[:] for row in solution]
    removed = 0
    attempts = 0
    max_attempts = 1000
    
    while removed < blanks and attempts < max_attempts:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            removed += 1
        attempts += 1
    
    return puzzle

def generate_sudoku(blanks_count):
    """Generate sudoku with specified number of blanks"""
    solution = generate_solution()
    puzzle = generate_puzzle(solution, blanks_count)
    return {"puzzle": puzzle, "solution": solution}

st.set_page_config(page_title="수학나라 - 스도쿠", layout="centered")
st.title("🧩 수학나라: 9x9 스도쿠 풀이")
st.write("빈칸 번호에 해당하는 입력란에 숫자를 넣으면 그 칸이 초록(정답)/빨강(오답)으로 표시됩니다. 모두 맞추면 폭죽(콘페티)이 터집니다!")

# Sidebar: difficulty & regenerate
with st.sidebar:
    st.header("⚙️ 설정")
    difficulty = st.selectbox("난이도 선택", ["쉬움 (30개)", "보통 (40개)", "어려움 (50개)"], 
                              index=1,
                              key="difficulty_select")
    if st.button("🔄 새 문제 생성"):
        st.session_state.regenerate = True

# Map difficulty to blank count
difficulty_map = {
    "쉬움 (30개)": 30,
    "보통 (40개)": 40,
    "어려움 (50개)": 50,
}
blanks_count = difficulty_map[difficulty]

# Generate or retrieve from session
if "current_puzzle" not in st.session_state or st.session_state.get("regenerate"):
    st.session_state.regenerate = False
    st.session_state.current_puzzle = generate_sudoku(blanks_count)
    st.rerun()

puzzle_data = st.session_state.current_puzzle

# HTML/JS component: Sudoku grid + inputs + validation + confetti
html = r'''
<style>
  .sudoku-board { display: grid; grid-template-columns: repeat(9, 44px); gap: 0; }
  .cell {
    width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;
    font-size: 18px; position: relative; border: 1px solid #999; box-sizing: border-box;
    background: #fff; transition: background 0.15s ease;
  }
  .cell.given { background: #f4f4f4; font-weight: 700; }
  .cell.correct { background: #c8f7c5; }
  .cell.wrong { background: #f7c5c5; }
  .cell .badge { position: absolute; top: 2px; right: 3px; font-size: 9px; color: #666; }

  /* Thicker borders for 3x3 boxes */
  .cell:nth-child(3n) { border-right: 2px solid #333; }
  .row-break { grid-column: 1 / -1; height: 0; }
  .sudoku-board .cell { border-bottom: 1px solid #999; }

  .inputs { margin-top: 18px; display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
  .input-item { display:flex; gap:8px; align-items:center; }
  .input-item input { width: 48px; padding:6px; font-size:16px; text-align:center; }

  .center { max-width:720px; margin: 8px auto; }
  .difficulty-info { font-size: 14px; color: #666; margin-top: 8px; }
</style>

<div class="center">
  <div id="board" class="sudoku-board"></div>
  <div class="difficulty-info" id="info"></div>

  <h4>빈칸 입력 (번호에 맞게 숫자 입력)</h4>
  <div id="inputs" class="inputs"></div>
</div>

<!-- confetti 라이브러리 -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>

<script>
// Data passed from Streamlit
const puzzleData = PUZZLE_DATA_PLACEHOLDER;
const solution = puzzleData.solution;
const puzzle = puzzleData.puzzle;

// collect blanks with numbering
let blanks = [];
for (let r=0, idx=1; r<9; r++){
  for (let c=0; c<9; c++){
    if (puzzle[r][c] === 0) {
      blanks.push({r, c, idx: idx, answer: solution[r][c]});
      idx++;
    }
  }
}

const boardEl = document.getElementById('board');
const infoEl = document.getElementById('info');
infoEl.textContent = `총 ${blanks.length}개 빈칸`;

// render 9x9 cells
for (let r=0; r<9; r++){
  for (let c=0; c<9; c++){
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.dataset.r = r; cell.dataset.c = c;
    // add thicker borders for 3x3 boxes
    if (c % 3 === 0) cell.style.borderLeft = '2px solid #333';
    if (r % 3 === 0) cell.style.borderTop = '2px solid #333';
    if (c === 8) cell.style.borderRight = '2px solid #333';
    if (r === 8) cell.style.borderBottom = '2px solid #333';

    if (puzzle[r][c] !== 0){
      cell.classList.add('given');
      cell.textContent = puzzle[r][c];
    } else {
      // find its blank number
      const b = blanks.find(x => x.r===r && x.c===c);
      cell.innerHTML = '<span class="badge">' + b.idx + '</span>';
      cell.dataset.blank = b.idx;
      cell.dataset.answer = b.answer;
    }
    boardEl.appendChild(cell);
  }
}

// render inputs for blanks
const inputsEl = document.getElementById('inputs');
blanks.forEach(b => {
  const item = document.createElement('div');
  item.className = 'input-item';
  item.innerHTML = `<label>#${b.idx}</label><input id="inp-${b.idx}" maxlength="1" pattern="[1-9]" data-idx="${b.idx}" inputmode="numeric" />`;
  inputsEl.appendChild(item);
});

// helper: update cell style for a blank
function setCellState(idx, state, value){
  const cell = document.querySelector('.cell[data-blank="'+idx+'"]');
  if (!cell) return;
  cell.classList.remove('correct','wrong');
  if (state === 'correct') {
    cell.classList.add('correct');
    cell.textContent = value;
    cell.innerHTML = value + '<span class="badge">' + idx + '</span>';
  } else if (state === 'wrong') {
    cell.classList.add('wrong');
    cell.textContent = value;
    cell.innerHTML = value + '<span class="badge">' + idx + '</span>';
  } else {
    cell.textContent = '';
    cell.innerHTML = '<span class="badge">' + idx + '</span>';
  }
}

// attach events
let correctCount = 0;
const total = blanks.length;
const answers = {};
blanks.forEach(b => answers[b.idx] = b.answer);

function checkAllDone(){
  if (correctCount === total){
    // confetti burst
    confetti({ particleCount: 200, spread: 70, origin: { y: 0.4 } });
    setTimeout(()=>{
      confetti({ particleCount: 150, spread: 100, origin: { y: 0.6 } });
    }, 500);
  }
}

blanks.forEach(b => {
  const input = document.getElementById('inp-' + b.idx);
  input.addEventListener('input', (e) => {
    const v = e.target.value.replace(/[^1-9]/g, '').slice(0,1);
    e.target.value = v;
    const idx = Number(e.target.dataset.idx);
    if (v === ''){
      // clear
      const prev = e.target.dataset.state;
      if (prev === 'correct') { correctCount--; }
      e.target.dataset.state = '';
      setCellState(idx, null, '');
      return;
    }
    const num = Number(v);
    if (num === answers[idx]){
      // mark correct
      if (e.target.dataset.state !== 'correct'){
        correctCount++;
      }
      e.target.dataset.state = 'correct';
      setCellState(idx, 'correct', num);
    } else {
      // wrong
      if (e.target.dataset.state === 'correct'){
        correctCount -= 1;
      }
      e.target.dataset.state = 'wrong';
      setCellState(idx, 'wrong', num);
    }
    checkAllDone();
  });
});

</script>
'''

# Replace placeholder with actual JSON data
html = html.replace('PUZZLE_DATA_PLACEHOLDER', json.dumps(puzzle_data))

components.html(html, height=920)
