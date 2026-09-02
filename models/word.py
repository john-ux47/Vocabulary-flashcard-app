class Word:
    def __init__(self, term, phonetic="", definitions=None, examples=None, 
                 synonyms=None, antonyms=None, simple_explanation="", 
                 ai_example="", memory_trick=""):
        self.term = term
        self.phonetic = phonetic
        self.definitions = definitions or []
        self.examples = examples or []
        self.synonyms = synonyms or []
        self.antonyms = antonyms or []
        self.simple_explanation = simple_explanation
        self.ai_example = ai_example
        self.memory_trick = memory_trick

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    