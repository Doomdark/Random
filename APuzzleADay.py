# Solve the A-Puzzle-A-Day wooden puzzle tangram for the specified day

import copy
from collections import defaultdict
import argparse, random

G = [['Jan','Feb','Mar','Apr','May','Jun','.'],
     ['Jul','Aug','Sep','Oct','Nov','Dec','.'],
     ['1','2','3','4','5','6','7'],
     ['8','9','10','11','12','13','14'],
     ['15','16','17','18','19','20','21'],
     ['22','23','24','25','26','27','28'],
     ['29','30','31','.','.','.','.']]

Pieces = {}

# Describe the piece shapes as (dr,dc) pairs starting from (0,0)
Pieces['a'] = ((0,0), (0,1), (0,2), (1,1), (1,2))
Pieces['b'] = ((0,0), (0,1), (0,2), (1,0), (1,1), (1,2))
Pieces['c'] = ((0,0), (0,1), (0,2), (0,3), (1,1))
Pieces['d'] = ((0,0), (0,1), (1,1), (1,2), (1,3))
Pieces['e'] = ((0,0), (0,1), (1,1), (2,1), (2,2))
Pieces['f'] = ((0,0), (0,1), (0,2), (1,0), (1,2))
Pieces['g'] = ((0,0), (0,1), (0,2), (0,3), (1,0))
Pieces['h'] = ((0,0), (0,1), (0,2), (1,2), (2,2))

DEFAULT = '\033[0m'
BOLD    = '\033[1m'
RED     = '\033[38;5;1m'
GREEN   = '\033[38;5;2m'
YELLOW  = '\033[38;5;3m'
BLUE    = '\033[38;5;4m'
PURPLE  = '\033[38;5;5m'
CYAN    = '\033[38;5;6m'
WHITE   = '\033[38;5;7m'
GREY    = '\033[38;5;8m'

Colours = {}
Colours['a'] = RED
Colours['b'] = GREEN
Colours['c'] = YELLOW
Colours['d'] = BLUE
Colours['e'] = PURPLE
Colours['f'] = CYAN
Colours['g'] = WHITE
Colours['h'] = GREY

def date_locs(G, d):
    'Get the month/day locations on the board for the provided date.'
    month, day = d.split()
    mloc, dloc = None,None
    for r,row in enumerate(G):
        for c,col in enumerate(row):
            if col == month:
                mloc = (r,c)
                break
            if col == day:
                dloc = (r,c)
                return mloc, dloc

# There are only 8 possible orientations for any of these pieces

def mirrorv(piece):
    'Mirror in a vertical line.'
    # For each location invert the column number, then shift everything right by abs(max col).
    p = []
    maxc = max([c for r,c in piece])
    for r,c in piece:
        p.append((r,-c+maxc))
    return tuple(sorted(p))

def mirrorh(piece):
    'Mirror in a horizontal line.'
    # For each location invert the row number, then shift everything down by abs(max row).
    p = []
    maxr = max([r for r,c in piece])
    for r,c in piece:
        p.append((-r+maxr,c))
    return tuple(sorted(p))

def mirrord(piece):
    'Mirror in a diagonal line going from top left to bottom right.'
    # Swap the r and c coordinates
    p = []
    for r,c in piece:
        p.append((c,r))
    return tuple(sorted(p))

def get_all_orientations(piece):
    'Find all the possible orientations of the provided piece'
    p = set()
    p.add(piece)
    _piece = mirrorv(piece)
    p.add(_piece)
    _piece = mirrorh(_piece)
    p.add(_piece)
    _piece = mirrorv(_piece)
    p.add(_piece)
    _piece = mirrord(_piece)
    p.add(_piece)
    _piece = mirrorv(_piece)
    p.add(_piece)
    _piece = mirrorh(_piece)
    p.add(_piece)
    _piece = mirrorv(_piece)
    p.add(_piece)
    return p

def get_all_positions(piece):
    'Get the piece shapes shifted up/down/left/right to cover all possible offsets within the shape.'
    maxr = max([r for r,c in piece])
    maxc = max([c for r,c in piece])
    p = set()
    for r in range(maxr+1):
        for c in range(maxc+1):
            _piece = []
            for (dr,dc) in piece:
                nr,nc = dr-r,dc-c
                _piece.append((nr,nc))
            p.add(tuple(sorted(_piece)))
    return p

def print_pieces(pieces):
    'Print out all the original piece shapes and their letters'
    print()
    rows = [''] * 4
    for name,piece in pieces.items():
        colour = Colours[name]
        for r in range(4):
            row = ''
            for c in range(4):
                if (r,c) in piece: rows[r] += colour + '#' + DEFAULT
                else: rows[r] += ' '
            rows[r] += ' '
    header = ''.join([' {}   '.format(name) for name,_ in pieces.items()])
    print(header)
    for row in rows:
        print(row)

def print_board(board):
    'Print the board out, including a nice perimeter.'
    for r in range(-1,len(board)+1):
        row = ''
        if   r == -1:         row = GREY + '┌──────┐' + DEFAULT
        elif r == len(board): row = GREY + '└───┘' + DEFAULT
        else:
            row = ''
            for c in range(-1,len(board[0])+1):
                if c == -1: row += GREY + '│' + DEFAULT
                elif c == len(board[0]):
                    if board[r][c-1][0] == '.':
                        if   r == 1: row += GREY + '┐' + DEFAULT
                        elif r == 6: row += GREY + '┘' + DEFAULT
                    else: row += GREY + '│' + DEFAULT
                elif (r,c) == month_loc: row += BOLD + WHITE + 'M' + DEFAULT
                elif (r,c) == day_loc  : row += BOLD + WHITE + 'D' + DEFAULT
                elif board[r][c][0] == '.':
                    if   r == 0: row += GREY + '│' + DEFAULT
                    elif r == 1: row += GREY + '└' + DEFAULT
                    elif r == 6:
                        if   c == 3: row += GREY + '┌' + DEFAULT
                        elif c == 7: row += GREY +'┌' + DEFAULT
                        else: row += GREY +'─' + DEFAULT
                else:
                    piece  = board[r][c][0]
                    colour = Colours[piece]
                    row += colour + '#' + DEFAULT
        print(row)

def next_free_loc(loc, board):
    'Get the next square (in reading order) that is not occupied.'
    sr,sc = loc
    started = False
    R,C = len(board), len(board[0])
    for r in range(R):
        if not started and r < sr: continue
        for c in range(C):
            if not started and c < sc: continue
            started = True
            if free_loc((r,c), board):
                return (r,c)

def free_loc(loc, board):
    'Is this location available to put a shape on?'
    r,c = loc
    if 0<=r<len(board) and 0<=c<len(board[0]):
        if board[r][c] not in list(PIECES.keys()) + ['.'] and (r,c) != month_loc and (r,c) != day_loc:
            return True
    return False

# Get all orientations for all pieces

PIECES = defaultdict(list)

# Make a dictionary with all the piece orientations in it for each shape
for name,piece in Pieces.items():
    # For all of those orientations get the up/down/left/right shifted positions
    for orientation in get_all_orientations(piece):
        PIECES[name].extend(get_all_positions(orientation))

def dfs(loc, board, pieces):
    'Try to fit the remaining pieces onto the provided board.'
    global solutions, args, MIN, MAX
    r,c = loc
    # Try each piece in turn
    for name,orientations in pieces.items():
        # Try to place the piece on the board
        for locs in orientations:
            good = True
            # Make a copy of the board for this new piece orientation test
            _board = copy.deepcopy(board)
            # Test each of the piece locations for being on the board
            for dr,dc in locs:
                nr,nc = r+dr,c+dc
                # Piece outside of the board boundary or already occupied?
                if not free_loc((nr,nc), _board):
                    good = False
                    break
                # Place the piece into the location
                _board[nr][nc] = name
            # This orientation didn't work, try the next one
            if not good:
                continue
            else: # The piece fitted OK
                # If there are remaining pieces then try the next one
                if len(pieces) > 1:
                    remaining_pieces = {k:v for k,v in pieces.items() if k != name}
                    # Find the next free board square to place a piece
                    nr,nc = next_free_loc((0,0), _board)
                    dfs((nr,nc), _board, remaining_pieces)
                else: # Finished! Print out the board
                    if args.all or args.minmax:
                        if _board not in solutions:
                            solutions.append(_board)
                        return
                    # Not trying to find all the solutions
                    print_pieces(Pieces)
                    print_board(_board)
                    exit()

        # The piece didn't fit, try the next one
    # None of the pieces fitted. Go back to Old Kent Road

# Parse the inputs
parser = argparse.ArgumentParser()
parser.add_argument('--all',    action='store_true', help='Calculate all of the possible solutions rather than just the first.')
parser.add_argument('--minmax', action='store_true', help='Determine the two dates with maximum and minimum solutions.')
args = parser.parse_args()

month_loc, day_loc = None, None

# List of solutions if we're finding all of them
solutions = []

# Shuffle the order of the PIECES dictionary for a bit of banter
l = list(PIECES.items())
random.shuffle(l)
PIECES = dict(l)

# Run the solver
if args.minmax:
    S = defaultdict(list)

    for month in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']:
        for day in ['1','2','3','4','5','6','7',
                    '8','9','10','11','12','13','14',
                    '15','16','17','18','19','20','21',
                    '22','23','24','25','26','27','28',
                    '29','30','31']:
            date = month + ' ' + day
            print(date)
            month_loc, day_loc = date_locs(G, date)
            # Solve it
            dfs((0,0), G, PIECES)
            # How many solutions for this date?
            S[len(solutions)].append(date)
            solutions = []
    # Which is the min/max?
    MAX = max(S.keys())
    dates = ', '.join(S[MAX])
    print('There are a maximum of {} solutions for these dates:'.format(MAX), dates)
    MIN = min(S.keys())
    dates = ', '.join(S[MIN])
    print('There are a minimum of {} solutions for these dates:'.format(MIN), dates)

else: # Solve for a particular date
    date = input('Input the required date, e.g. Feb 26: ')
    # Get the location of the day and month on the grid
    month_loc, day_loc = date_locs(G, date)
    # Solve it
    dfs((0,0), G, PIECES)
    # If we want all the solutions then print out how many there are for this date
    if args.all:
        print('There are {} solutions for {}'.format(len(solutions), date))
