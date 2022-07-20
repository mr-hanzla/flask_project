from flask import (
    Blueprint,
    Flask,
    flash,
    render_template,
    redirect,
    url_for,
    request,
    session
)

bp = Blueprint('ttt', __name__, url_prefix='/ttt')

def is_board_present():
    if 'board' in session:
        return True
    return False

def is_board_empty():
    for row in session['board']:
        if None in row:
            return True
    return False

def is_board_present_and_empty():
    return is_board_present() and is_board_empty()

def row_check(row, other_player):
    if is_board_present():
        return other_player not in session['board'][row] and None not in session['board'][row]
    return False

def col_check(col, other_player):
    for i in range(3):
        if session['board'][i][col] == other_player or session['board'][i][col] == None:
            return False
    return True


@bp.route('/game')
def game():
    if not is_board_present():
        session['board'] = [[None, None, None], [None, None, None], [None, None, None]]
        session['turn'] = 'X'
        session['winner'] = None

    return render_template('TTT/game.html', game={
        'board': session['board'],
        'turn': session['turn'],
        'winner': session['winner'],
    })

@bp.route('/move/<int:row>/<int:col>')
def move(row, col):

    if not is_board_present():
        return redirect(url_for('ttt.game'))
    
    turn = session['turn']
    session['board'][row][col] = turn
    
    other_player = 'O' if turn == 'X' else 'X'
    
    if row_check(row, other_player) or col_check(col, other_player):
        session['winner'] = turn
        return redirect(url_for('ttt.game'))

    if not is_board_empty():
        session['winner'] = 'N'
    session['turn'] = other_player
    return redirect(url_for('ttt.game'))



@bp.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('ttt.game'))

