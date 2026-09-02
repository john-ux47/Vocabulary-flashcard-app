from models.flashcard import Flashcard
from datetime import date, timedelta

class SpacedRepetition:
    @staticmethod
    def update_card(card: Flashcard, quality: int) -> Flashcard:
        if quality < 2:
            card.repetitions = 0
            card.interval = 1
        else:
            card.repetitions += 1
            if card.repetitions == 1:
                card.interval = 1
            elif card.repetitions == 2:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.ease_factor)
        
        card.ease_factor = max(1.3, card.ease_factor + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02)))
        card.last_reviewed = str(date.today())
        card.next_review_date = str(date.today() + timedelta(days=card.interval))
        
        return card