from flask import Flask, render_template, request

app = Flask(__name__)

class PilesOfStonesGame:
    def __init__(self):
        self.piles = [0, 0, 0]
        self.players = []
        self.current_player = None
        self.min_pick = None
        self.max_pick = None
        self.scores = {}

    def start_game(self, settings):
        # Get game settings from the form
        self.piles = [
            int(settings['num_stones_pile1']),
            int(settings['num_stones_pile2']),
            int(settings['num_stones_pile3'])
        ]

        self.min_pick = int(settings['min_pick'])
        self.max_pick = int(settings['max_pick'])

        num_players = int(settings['num_players'])
        for i in range(num_players):
            player_name = settings[f'player_{i+1}']
            self.players.append(player_name)
            self.scores[player_name] = 0

        self.current_player = self.players[0]

    def play_turn(self, move):
        pile_index = int(move['pile_index'])
        stones_picked = int(move['stones_picked'])

        if (
            pile_index < 0
            or pile_index >= len(self.piles)
            or stones_picked < self.min_pick
            or stones_picked > self.max_pick
            or stones_picked > self.piles[pile_index]
        ):
            return "Invalid move! Try again."

        self.piles[pile_index] -= stones_picked
        self.scores[self.current_player] += stones_picked
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

        return None

    def check_game_over(self):
        return all(pile == 0 for pile in self.piles)

    def get_winner(self):
        max_score = max(self.scores.values())
        winners = [player for player, score in self.scores.items() if score == max_score]
        return winners

game = PilesOfStonesGame()

@app.route('/', methods=['GET','POST'])
def index():

    if request.method == 'POST':
        if 'start_game' in request.form:
            # game_id = str(uuid.uuid4())  # Generate a unique ID for the game instance
            game.start_game(request.form)
            return render_template('game.html', game=game)

        if 'play_turn' in request.form:
            error = game.play_turn(request.form)
            if error:
                return render_template('game.html', game=game, error=error)
            if game.check_game_over():
                winners = game.get_winner()
                return render_template('game_over.html', winners=winners)
            return render_template('game.html', game=game)

    return render_template('index.html', num_players=request.form.get('num_players'))


if __name__ == '__main__':
    app.run()
