"""
Duel Grid — Tic Tac Toe
Game logic written entirely in Python, executed in the browser by Brython.
Direct port of the original minimax evaluate()/findBestMove() logic.
"""
from browser import document, html, timer
import random

# ---------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------
board = [['_', '_', '_'] for _ in range(3)]
game_over = False
current_player = 'x'          # 'x' always moves first
mode = 'pve'                  # 'pve' = vs AI, 'pvp' = vs friend (pass and play)
difficulty = 'hard'
scores = {'x': 0, 'o': 0, 'draw': 0}

WIN_LINES = [
    [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)],
]

ROBOT_AVATAR = (
    '<svg viewBox="0 0 40 40"><rect x="10" y="9" width="20" height="16" rx="8" '
    'fill="#fff8ec" stroke="#161311" stroke-width="2"/><circle cx="16" cy="17" r="1.8" '
    'fill="#161311"/><circle cx="24" cy="17" r="1.8" fill="#161311"/>'
    '<path d="M15 21 L25 21" stroke="#161311" stroke-width="1.8" stroke-linecap="round"/>'
    '<path d="M14 9 L11 4 M26 9 L29 4" stroke="#161311" stroke-width="1.8" '
    'stroke-linecap="round"/></svg>'
)
HUMAN2_AVATAR = (
    '<svg viewBox="0 0 40 40"><circle cx="20" cy="17" r="10" fill="#fff8ec" '
    'stroke="#161311" stroke-width="2"/><circle cx="16.5" cy="16" r="1.6" fill="#161311"/>'
    '<circle cx="23.5" cy="16" r="1.6" fill="#161311"/>'
    '<path d="M16 21 Q20 19.5 24 21" stroke="#161311" stroke-width="1.8" fill="none" '
    'stroke-linecap="round"/><path d="M12 10 Q20 3 28 10" stroke="#161311" '
    'stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>'
)

# ---------------------------------------------------------------------
# CORE MINIMAX EVALUATION (unchanged logic, ported line-for-line)
# ---------------------------------------------------------------------
def evaluate(b):
    for row in range(3):
        if b[row][0] == b[row][1] == b[row][2]:
            if b[row][0] == 'x':
                return 10
            elif b[row][0] == 'o':
                return -10
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col]:
            if b[0][col] == 'x':
                return 10
            elif b[0][col] == 'o':
                return -10
    if b[0][0] == b[1][1] == b[2][2]:
        if b[0][0] == 'x':
            return 10
        elif b[0][0] == 'o':
            return -10
    if b[0][2] == b[1][1] == b[2][0]:
        if b[0][2] == 'x':
            return 10
        elif b[0][2] == 'o':
            return -10
    return 0


def is_moves_left(b):
    return any(cell == '_' for row in b for cell in row)


def minimax(b, depth, is_max, alpha, beta):
    score = evaluate(b)
    if score == 10:
        return score - depth
    if score == -10:
        return score + depth
    if not is_moves_left(b):
        return 0

    if is_max:
        best = float('-inf')
        for i in range(3):
            for j in range(3):
                if b[i][j] == '_':
                    b[i][j] = 'x'
                    best = max(best, minimax(b, depth + 1, False, alpha, beta))
                    b[i][j] = '_'
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        return best
        return best
    else:
        best = float('inf')
        for i in range(3):
            for j in range(3):
                if b[i][j] == '_':
                    b[i][j] = 'o'
                    best = min(best, minimax(b, depth + 1, True, alpha, beta))
                    b[i][j] = '_'
                    beta = min(beta, best)
                    if beta <= alpha:
                        return best
        return best


def find_best_move(b, level):
    empties = [(i, j) for i in range(3) for j in range(3) if b[i][j] == '_']

    if level == 'easy' and random.random() < 0.7:
        return random.choice(empties)

    best_val = float('inf')
    candidates = []
    for (i, j) in empties:
        b[i][j] = 'o'
        move_val = minimax(b, 0, True, float('-inf'), float('inf'))
        b[i][j] = '_'
        if move_val < best_val:
            best_val = move_val
            candidates = [(i, j)]
        elif move_val == best_val:
            candidates.append((i, j))

    if level == 'medium' and random.random() < 0.35 and len(empties) > len(candidates):
        non_optimal = [e for e in empties if e not in candidates]
        return random.choice(non_optimal)

    return random.choice(candidates)


# ---------------------------------------------------------------------
# DOM REFERENCES
# ---------------------------------------------------------------------
board_el = document['board']
bubble_el = document['bubble']
fighter_player = document['fighterPlayer']
fighter_player_name = document['fighterPlayerName']
fighter_rival = document['fighterRival']
fighter_rival_name = document['fighterRivalName']
fighter_rival_avatar = document['fighterRivalAvatar']
score_label_x = document['scoreLabelX']
score_label_o = document['scoreLabelO']
score_x_el = document['scoreX']
score_o_el = document['scoreO']
score_draw_el = document['scoreDraw']
rank_select = document['rankSelect']
rank_caption = document['rankCaption']
reset_btn = document['resetBtn']
mode_select = document['modeSelect']

cells = {}  # (row, col) -> DOM element


# ---------------------------------------------------------------------
# RENDER HELPERS
# ---------------------------------------------------------------------
def burst_svg():
    return ('<svg class="burst" viewBox="0 0 100 100">'
            '<path d="M50 4 L58 38 L92 38 L64 56 L74 90 L50 68 L26 90 L36 56 L8 38 L42 38 Z" '
            'fill="#ffd23f" opacity="0.9"/></svg>')


def mark_svg(kind):
    if kind == 'x':
        return (
            '<svg class="mark" viewBox="0 0 60 60">'
            '<path class="mark-path mark-x" d="M12 12 L48 48" stroke-width="8" pathLength="1" '
            'style="stroke-dasharray:1;stroke-dashoffset:1;animation:drawMark .22s ease forwards;"/>'
            '<path class="mark-path mark-x" d="M48 12 L12 48" stroke-width="8" pathLength="1" '
            'style="stroke-dasharray:1;stroke-dashoffset:1;animation:drawMark .22s .1s ease forwards;"/>'
            '</svg>'
        )
    return (
        '<svg class="mark" viewBox="0 0 60 60">'
        '<circle class="mark-path mark-o" cx="30" cy="30" r="17" stroke-width="8" pathLength="1" '
        'style="stroke-dasharray:1;stroke-dashoffset:1;animation:drawMark .3s ease forwards;"/>'
        '</svg>'
    )


def build_board():
    board_el.html = ''
    cells.clear()
    for i in range(3):
        for j in range(3):
            cell = html.DIV(Class="cell selectable", tabindex="0")
            cell.attrs['data-row'] = str(i)
            cell.attrs['data-col'] = str(j)
            cell.bind('click', make_click_handler(i, j))
            cell.bind('keydown', make_keydown_handler(i, j))
            board_el <= cell
            cells[(i, j)] = cell


def make_click_handler(i, j):
    def handler(ev):
        on_cell_click(i, j)
    return handler


def make_keydown_handler(i, j):
    def handler(ev):
        if ev.key in ('Enter', ' '):
            ev.preventDefault()
            on_cell_click(i, j)
    return handler


def render():
    for i in range(3):
        for j in range(3):
            cell = cells[(i, j)]
            v = board[i][j]
            if v == '_':
                cell.html = ''
                cell.classList.add('selectable')
                cell.attrs['data-filled'] = ''
            elif not cell.attrs.get('data-filled'):
                cell.html = burst_svg() + mark_svg(v)
                cell.select('.burst')[0].classList.add('pop')
                cell.attrs['data-filled'] = '1'
                cell.classList.remove('selectable')
    update_active_fighter()


def update_active_fighter():
    if current_player == 'x' and not game_over:
        fighter_player.classList.add('active')
    else:
        fighter_player.classList.remove('active')
    if current_player == 'o' and not game_over:
        fighter_rival.classList.add('active')
    else:
        fighter_rival.classList.remove('active')


def set_bubble(text, cls=None):
    bubble_el.text = text
    bubble_el.class_name = 'bubble' + (' ' + cls if cls else '')


def bubble_for_turn():
    if mode == 'pvp':
        return "Player 1's move — make your mark!" if current_player == 'x' \
            else "Player 2's move — make your mark!"
    return 'Your move — make your mark!' if current_player == 'x' \
        else 'Rival is plotting a counter…'


# ---------------------------------------------------------------------
# GAME FLOW
# ---------------------------------------------------------------------
def on_cell_click(i, j):
    global current_player
    if game_over:
        return
    if mode == 'pve' and current_player != 'x':
        return
    if board[i][j] != '_':
        return

    board[i][j] = current_player
    render()
    if check_end():
        return

    current_player = 'o' if current_player == 'x' else 'x'
    set_bubble(bubble_for_turn())
    update_active_fighter()

    if mode == 'pve' and current_player == 'o':
        timer.set_timeout(machine_move, 500)


def machine_move():
    global current_player
    if game_over:
        return
    move = find_best_move(board, difficulty)
    if move:
        board[move[0]][move[1]] = 'o'
        render()
    if check_end():
        return
    current_player = 'x'
    set_bubble(bubble_for_turn())
    update_active_fighter()


def check_end():
    score = evaluate(board)
    if score == 10:
        end_game('x')
        return True
    if score == -10:
        end_game('o')
        return True
    if not is_moves_left(board):
        end_game('draw')
        return True
    return False


def end_game(result):
    global game_over
    game_over = True
    if result == 'x':
        msg = 'K.O.! Player 1 wins the round!' if mode == 'pvp' else 'K.O.! You win the round!'
        set_bubble(msg, 'win-x')
        scores['x'] += 1
        draw_win_line('#ff3b57')
        show_ribbon('x', 'K.O.!')
    elif result == 'o':
        msg = 'K.O.! Player 2 wins the round!' if mode == 'pvp' else 'Rival lands the finishing blow…'
        set_bubble(msg, 'win-o')
        scores['o'] += 1
        draw_win_line('#2f6fff')
        show_ribbon('o', 'K.O.!' if mode == 'pvp' else 'DEFEAT')
    else:
        set_bubble('Draw! Evenly matched.')
        scores['draw'] += 1
        show_ribbon('draw', 'DRAW!')
    update_scores()
    update_active_fighter()


def cell_center(row, col):
    return col * 100 + 50, row * 100 + 50


def draw_win_line(color):
    for line in WIN_LINES:
        (r1, c1), (r2, c2), (r3, c3) = line
        if board[r1][c1] != '_' and board[r1][c1] == board[r2][c2] == board[r3][c3]:
            x1, y1 = cell_center(r1, c1)
            x3, y3 = cell_center(r3, c3)
            wrap = html.DIV()
            wrap.html = (
                f'<svg class="win-line" viewBox="0 0 300 300">'
                f'<path d="M {x1} {y1} L {x3} {y3}" stroke="{color}" pathLength="1" '
                f'style="stroke-dasharray:1;stroke-dashoffset:1;'
                f'animation:drawMark .35s ease forwards;"/></svg>'
            )
            board_el <= wrap
            break


def show_ribbon(kind, text):
    overlay = html.DIV(Class='win-overlay')
    overlay.html = f'<div class="win-ribbon {kind}">{text}</div>'
    board_el <= overlay


def update_scores():
    score_x_el.text = str(scores['x'])
    score_o_el.text = str(scores['o'])
    score_draw_el.text = str(scores['draw'])


def new_round(*_args):
    global board, game_over, current_player
    board = [['_', '_', '_'] for _ in range(3)]
    game_over = False
    current_player = 'x'
    for cell in cells.values():
        cell.html = ''
        cell.attrs['data-filled'] = ''
        cell.classList.add('selectable')
    for el in list(board_el.select('.win-line')) + list(board_el.select('.win-overlay')):
        el.remove()
    set_bubble(bubble_for_turn())
    update_active_fighter()


def set_mode(m):
    global mode
    mode = m
    for b in mode_select.select('button'):
        if b.attrs.get('data-mode') == m:
            b.classList.add('active')
        else:
            b.classList.remove('active')

    if m == 'pvp':
        fighter_player_name.text = 'Player 1'
        fighter_rival_name.text = 'Player 2'
        fighter_rival_avatar.html = HUMAN2_AVATAR
        score_label_x.text = 'P1'
        score_label_o.text = 'P2'
        rank_select.classList.add('disabled')
        rank_caption.text = 'AI difficulty · switch to VS AI to use'
    else:
        fighter_player_name.text = 'You'
        fighter_rival_name.text = 'Rival AI'
        fighter_rival_avatar.html = ROBOT_AVATAR
        score_label_x.text = 'You'
        score_label_o.text = 'Rival'
        rank_select.classList.remove('disabled')
        rank_caption.text = 'AI difficulty · VS AI mode'
    new_round()


# ---------------------------------------------------------------------
# EVENT BINDINGS
# ---------------------------------------------------------------------
def on_reset_click(ev):
    new_round()


def on_rank_click(ev):
    global difficulty
    btn = ev.target
    # climb to the button element if a child (e.g. text node) was clicked
    while btn is not None and btn.tagName != 'BUTTON':
        btn = btn.parent
    if btn is None or mode != 'pve':
        return
    difficulty = btn.attrs.get('data-level')
    for b in rank_select.select('button'):
        b.classList.remove('active')
    btn.classList.add('active')
    new_round()


def on_mode_click(ev):
    btn = ev.target
    while btn is not None and btn.tagName != 'BUTTON':
        btn = btn.parent
    if btn is None:
        return
    set_mode(btn.attrs.get('data-mode'))


reset_btn.bind('click', on_reset_click)
rank_select.bind('click', on_rank_click)
mode_select.bind('click', on_mode_click)

# ---------------------------------------------------------------------
# INIT
# ---------------------------------------------------------------------
build_board()
render()
set_bubble(bubble_for_turn())
