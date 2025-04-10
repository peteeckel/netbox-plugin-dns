def initialize_choice_names(cls):
    for choice in cls.CHOICES:
        setattr(cls, choice[0], choice[0])
    return cls
