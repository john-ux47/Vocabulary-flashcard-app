from datetime import date

class Flashcard:
    def __init__(self, word_dict, repetitions=0, interval=1, 
                 ease_factor=2.5, next_review_date=None, last_reviewed=None):
        self.word_dict = word_dict 
        self.repetitions = repetitions
        self.interval = interval   
        self.ease_factor = ease_factor
        self.next_review_date = next_review_date or str(date.today())
        self.last_reviewed = last_reviewed

    def is_due(self) -> bool:
        today_str = str(date.today())
        return self.next_review_date <= today_str

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)