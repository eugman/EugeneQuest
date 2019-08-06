import math

def NormalizedScoreToLevel(score: float) -> float:
    return 0.5 * (math.sqrt(8*score + 1) + 1)



def ScoreToLevel(score: float, start: float, end: float, reversed: bool = False) -> float:
    range = end - start

    scalar = 45 / range

    normalizedScore = (score - start) * scalar

    #Use reversed when bigger jumps are easier intially and the last few points are difficult.
    if reversed:
        level = NormalizedScoreToLevel(45-normalizedScore)
        level = 11 - level
    else:
        level = NormalizedScoreToLevel(normalizedScore)

    return level

def NextGoal(level : float, start: float, end: float, reversed: bool = False) -> float:
    nextLevel = math.ceil(level + 0.001)

    return LevelToScore(nextLevel, start, end, reversed)
    

def LevelToScore(level : float, start: float, end: float, reversed: bool = False) -> float:

    range = end - start

    scalar =  45 / range

    if reversed:
        level = 11 - level
        target = level * (level - 1) / 2
        return end - (target / scalar)
    else:
        target = level * (level - 1) / 2
        return (target / scalar) + start
