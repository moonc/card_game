import pygame
import random

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, RED, GREEN, GRAY
)

class Button:
    """
    A simple Button class to draw a rectangle with text and detect clicks.
    """
    def __init__(self, x, y, w, h, text, font,
                 bg_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

        # Pre-render the text for this button
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        """
        Draw the button (rectangle + text).
        """
        pygame.draw.rect(surface, self.bg_color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, mouse_pos):
        """
        Check if the button was clicked by comparing the mouse_pos with its rect.
        """
        return self.rect.collidepoint(mouse_pos)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Blackjack (Dealer's Hand Hidden + Instant Win on 21)")

        self.clock = pygame.time.Clock()
        self.running = True

        # Set up fonts for rendering text
        self.font_large = pygame.font.SysFont("arial", 36, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24, bold=True)

        # Create the buttons
        self.btn_hit = Button(
            x=100, y=500, w=100, h=40,
            text="Hit", font=self.font_small,
            bg_color=GREEN, text_color=BLACK
        )
        self.btn_stand = Button(
            x=300, y=500, w=100, h=40,
            text="Stand", font=self.font_small,
            bg_color=GREEN, text_color=BLACK
        )
        self.btn_restart = Button(
            x=500, y=500, w=100, h=40,
            text="Restart", font=self.font_small,
            bg_color=GRAY, text_color=BLACK
        )

        # Start a new game/round
        self.new_round()

    def new_round(self):
        """Set up a new round of Blackjack."""
        self.deck = self.make_deck()
        random.shuffle(self.deck)

        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

        self.round_over = False
        self.winner_text = ""
        self.game_state = "PLAYER_TURN"  # or "DEALER_TURN" / "DONE"

        # OPTIONAL: Check if player starts with 21 (natural Blackjack).
        # If so, instantly end the round:
        #
        # if self.score_hand(self.player_hand) == 21:
        #     self.round_over = True
        #     self.game_state = "DONE"
        #     self.winner_text = "Blackjack! You win immediately."

    def make_deck(self):
        suits = ['♣', '♦', '♥', '♠']
        deck = []
        for suit in suits:
            for rank in range(1, 14):  # 1=Ace, 11=Jack, 12=Queen, 13=King
                deck.append((rank, suit))
        return deck

    def card_to_string(self, card):
        rank, suit = card
        if rank == 1:
            rank_str = 'A'
        elif rank == 11:
            rank_str = 'J'
        elif rank == 12:
            rank_str = 'Q'
        elif rank == 13:
            rank_str = 'K'
        else:
            rank_str = str(rank)
        return f"{rank_str}{suit}"

    def score_hand(self, hand):
        total = 0
        aces = 0

        for card in hand:
            rank, _ = card
            if rank > 10:
                total += 10  # J, Q, K
            elif rank == 1:
                aces += 1
                total += 1
            else:
                total += rank

        # Convert Aces from 1 to 11 if possible
        while aces > 0:
            if total + 10 <= 21:
                total += 10
            aces -= 1

        return total

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        self.quit()

    def handle_events(self):
        """Handle user clicks, window events, etc."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos

                    # Restart round
                    if self.btn_restart.is_clicked(mouse_pos):
                        self.new_round()

                    # If round not over, check Hit/Stand
                    if not self.round_over:
                        if self.game_state == "PLAYER_TURN":
                            if self.btn_hit.is_clicked(mouse_pos):
                                # Player draws a new card
                                self.player_hand.append(self.deck.pop())

                                player_total = self.score_hand(self.player_hand)
                                # Check bust
                                if player_total > 21:
                                    self.round_over = True
                                    self.game_state = "DONE"
                                    self.winner_text = "You busted! Dealer wins."
                                # NEW: Instantly win if hitting exactly 21
                                elif player_total == 21:
                                    self.round_over = True
                                    self.game_state = "DONE"
                                    self.winner_text = "You hit 21! You win."
                                # Otherwise, continue as normal

                            elif self.btn_stand.is_clicked(mouse_pos):
                                self.game_state = "DEALER_TURN"

    def update(self):
        if self.game_state == "DEALER_TURN":
            dealer_score = self.score_hand(self.dealer_hand)
            if dealer_score < 17:
                self.dealer_hand.append(self.deck.pop())
            else:
                self.game_state = "DONE"
                self.round_over = True
                self.determine_winner()

    def determine_winner(self):
        player_score = self.score_hand(self.player_hand)
        dealer_score = self.score_hand(self.dealer_hand)

        if dealer_score > 21:
            self.winner_text = "Dealer busted! You win."
        elif player_score > dealer_score:
            self.winner_text = "You win!"
        elif player_score < dealer_score:
            self.winner_text = "Dealer wins."
        else:
            self.winner_text = "It's a tie!"

    def draw_text(self, text, x, y, font=None, color=BLACK):
        if font is None:
            font = self.font_small
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw(self):
        self.screen.fill(WHITE)

        # Title
        self.draw_text("Blackjack!", 20, 20, font=self.font_large)

        # Player hand
        player_cards_str = ", ".join(self.card_to_string(c) for c in self.player_hand)
        player_score = self.score_hand(self.player_hand)
        self.draw_text(f"Your Hand: {player_cards_str} (score: {player_score})", 20, 100)

        # Dealer hand (hide second card if still player's turn)
        if self.game_state == "PLAYER_TURN" and not self.round_over:
            shown_dealer_cards = [self.card_to_string(self.dealer_hand[0])]
            if len(self.dealer_hand) > 1:
                shown_dealer_cards.extend(["??"] * (len(self.dealer_hand) - 1))
            dealer_score_display = ""
        else:
            shown_dealer_cards = [self.card_to_string(c) for c in self.dealer_hand]
            dealer_score_display = f"(score: {self.score_hand(self.dealer_hand)})"

        dealer_cards_str = ", ".join(shown_dealer_cards)
        self.draw_text(f"Dealer Hand: {dealer_cards_str} {dealer_score_display}", 20, 200)

        # Draw buttons
        self.btn_hit.draw(self.screen)
        self.btn_stand.draw(self.screen)
        self.btn_restart.draw(self.screen)

        if self.round_over:
            self.draw_text(self.winner_text, 20, 300, color=RED)
            self.draw_text("Click 'Restart' to play again.", 20, 340)
        else:
            if self.game_state == "PLAYER_TURN":
                self.draw_text("Your turn! Click 'Hit' or 'Stand'.", 20, 300)
            elif self.game_state == "DEALER_TURN":
                self.draw_text("Dealer's turn... (please wait)", 20, 300)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
