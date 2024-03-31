import argparse, sys, time
sys.setrecursionlimit(100_000)

class State:
    height = 6
    width = 7
    bottom = 0x01010101010101
    bottom_col = [1 << (col*8) for col in range(7)]
    top = 0x20202020202020
    top_col = [0x20 << (col*8) for col in range(7)]
    full = 0x3F3F3F3F3F3F3F
    alignments = [
        1, # vertical
        7, # diagonal down
        8, # horizontal
        9  # diagonal up
    ]

    def __init__(self, bitmap, mask):
        self.bitmap = bitmap
        self.mask = mask
        self.invmask = State.full ^ mask
        self.opp_bitmap = bitmap ^ mask
        self.key = bitmap + mask + State.bottom

    @classmethod
    def empty(cls):
        return cls(0, 0)
    
    @classmethod
    def from_moves(cls, s):
        state = cls.empty()
        for col in s:
            col = int(col) - 1
            state = state.place_col(col)
        return state
    
    @property
    def player(self):
        return self.mask.bit_count() % 2
    
    @property
    def symbol(self):
        return {0: "o", 1: "x"}[self.player]
    
    @property
    def opp_symbol(self):
        return {0: "x", 1: "o"}[self.player]
    
    def evaluation(self):
        good_threats = 0
        bad_threats = 0
        for alignment in State.alignments:
            good_pairs = (self.bitmap | self.invmask) & (self.bitmap >> alignment)
            good_threats |= good_pairs & (good_pairs >> alignment) & (good_pairs >> (alignment * 2))
            good_pairs = (self.bitmap | self.invmask) & (self.bitmap << alignment)
            good_threats |= good_pairs & (good_pairs << alignment) & (good_pairs << (alignment * 2))

            bad_pairs = (self.opp_bitmap | self.invmask) & (self.opp_bitmap >> alignment)
            bad_threats |= bad_pairs & (bad_pairs >> alignment) & (bad_pairs >> (alignment * 2))
            bad_pairs = (self.opp_bitmap | self.invmask) & (self.opp_bitmap << alignment)
            bad_threats |= bad_pairs & (bad_pairs << alignment) & (bad_pairs << (alignment * 2))
        
        return good_threats.bit_count() - bad_threats.bit_count()
    
    def heuristic_weak(bitmap):
        score = 0
        for alignment in State.alignments:
            pairs = bitmap & (bitmap >> alignment)
            score += (pairs & (pairs >> alignment)).bit_count()
            
        return score
    
    def aligned4(bitmap):
        for alignment in State.alignments:
            pairs = bitmap & (bitmap >> alignment)
            if pairs & (pairs >> (alignment * 2)):
                return True
            
        return False
    
    def win(self):
        return State.aligned4(self.bitmap)

    def loss(self):
        return State.aligned4(self.opp_bitmap)
    
    def no_moves(self):
        return bool(self.mask & State.top == State.top)
        
    def game_over(self):
        return self.no_moves() or self.win() or self.loss()

    def next_states(self):
        states = []
        for next_col in [3,4,2,5,1,6,0]:
            if self.col_free(next_col):
                states.append(self.place_col(next_col))
        states.sort(key = lambda next_state: State.heuristic_weak(next_state.opp_bitmap), reverse=True)
        #states.sort(key = lambda next_state: next_state.evaluation())
        return states

    def col_free(self, col):
        return not bool(self.mask & State.top_col[col])
    
    def place_col(self, col):
        new_bitmap = self.opp_bitmap
        newmask = self.mask | (self.mask + State.bottom_col[col])
        return State(new_bitmap, newmask)
    
    def __str__(self):
        s = ""
        for j in range(State.height - 1, -1, -1):
            for i in range(State.width):
                if self.mask & (1 << ((j + i*8))):
                    if self.bitmap & (1 << ((j + i*8))):
                        s += self.symbol + " "
                    else:
                        s += self.opp_symbol + " "
                else:
                    s += ". "
            s += str(j) + "\n"
        s += "1 2 3 4 5 6 7"
        return s

class Solver:

    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.reset_transpos = max_depth != -1
        self.transpos = dict()
    
    def best_state(self, state):
        p = -101
        best_state = None
        alpha, beta = -100, 100
        if self.reset_transpos:
            self.transpos = dict()
        for next_state in state.next_states():
            new_p = - self.alpha_beta_search(next_state, 1, 
                                                -beta, -alpha)
            if new_p > p:
                p = new_p
                best_state = next_state
            alpha = max(alpha, p)
            if alpha >= beta:
                break
        return best_state, p 

    def alpha_beta_search(self, state, depth, alpha, beta):
        p = self.transpos.get(state.key)
        if p:
            return p
        
        if state.win():
            return 100 - depth
        if state.loss():
            return -100 + depth
        if state.no_moves():
            return 0
        if depth == self.max_depth:
            return state.evaluation()
        
        p = -100
        for next_state in state.next_states():
            p = max(p, - self.alpha_beta_search(next_state, depth+1, 
                                                -beta, -alpha))
            alpha = max(alpha, p)
            if alpha >= beta:
                break

        self.transpos[state.key] = p
        return p





if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Connect 4 AI',
                    description='Play against a Connect 4 AI or let the AI play against itself.')
    parser.add_argument('--mode', choices=["play_self", "play_human"], default="play_self")
    parser.add_argument('--max_depth', type=int, default=14)
    parser.add_argument('--starting_moves', type=str, default="")
    parser.add_argument('--starting', action="store_true")
    args = parser.parse_args()

    state = State.from_moves(args.starting_moves) # 44444136666625222326
    solver = Solver(args.max_depth)
    print(state)
    print()
    processing_time = 0

    human = None
    if args.mode == "play_human":
        if args.starting:
            human = 0
        else:
            human = 1

    while not state.game_over():
        if state.player == human:
            while True:
                try:
                    col = int(input("Move: ")) - 1
                except ValueError:
                    print("Invalid move")
                    continue
                if (col < 7) and (col >= 0) and state.col_free(col):
                    state = state.place_col(col)
                    break
                else:
                    print("Invalid move")
        else:
            t = time.time()
            state, p = solver.best_state(state)
            processing_time += time.time() - t
            if p > 50:
                print(f"({state.opp_symbol}) can win in {(100 - p) // 2} moves.")
            elif p < -50:
                print(f"({state.opp_symbol}) can lose in {(100 + p) // 2} moves.")
            else:
                print("p =", p)
        print("---------------")
        print(state)
        print()
    
    if state.win():
        print(f"Win for ({state.symbol})")
    elif state.loss():
        print(f"Win for ({state.opp_symbol})")
    else:
        print("Draw")
    print("Processing time:", processing_time)
