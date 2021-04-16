class Note:
    def __init__(self, pitch, player=None, velocity=120, length=1/8):
        self.pitch = pitch
        self.velocity = velocity
        self.length = length
        self.player = player
    def seconds(self, tempo):
        # beats * (beats / minute) = beats * beats / 60 seconds
        return self.length * (tempo / 60)
    def play(self, player=None):
        if player:
            self.player = player
        # Turn on note using midi pitch and velocity
        self.player.note_on(self.pitch.midi, self.velocity)
    def update_key(self, key):
        self.key = key
        # Extract naturals from key
        self.key_notes = [n[0] for n in self.key]

        natural = self.pitch.natural
        # print(natural)

        # Natural is listed in key signature
        if natural in self.key_notes:
            # Get corresponding accidental
            acc = self.key[self.key_notes.index(natural)][1]
            # Shift pitch accordingly
            if acc == '_':
                self.pitch.step(-0.5)
            elif acc == '^' or acc == '#':
                self.pitch.step(+0.5)
    def info(self):
        self.pitch.info()
        print()
        for w in ['key', 'velocity', 'length']:
            value = getattr(self, w)
            print(w + ': ' + str(value))