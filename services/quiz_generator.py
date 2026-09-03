import random

class QuizGenerator:
    def __init__(self, flashcards: list):
        self.cards = flashcards

    def generate_quiz(self, num_questions=5):
        if len(self.cards) < 2:
            return []

        questions = []
        sample_cards = random.sample(self.cards, min(num_questions, len(self.cards)))

        for target_card in sample_cards:
            term = target_card["word_dict"]["term"]
            defs = target_card["word_dict"].get("definitions", [])
            correct_def = defs[0] if defs else "No definition available"
            
            other_defs = [
                c["word_dict"]["definitions"][0] 
                for c in self.cards 
                if c["word_dict"]["term"] != term and c["word_dict"].get("definitions")
            ]
            
            wrong_choices = random.sample(other_defs, min(3, len(other_defs)))
            options = wrong_choices + [correct_def]
            random.shuffle(options)

            questions.append({
                "word": term,
                "correct_answer": correct_def,
                "options": options
            })

        return questions
    