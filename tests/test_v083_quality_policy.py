
def quality(points, confidence):
    if points >= 5 and confidence >= 0.65: return "CONFIDENT"
    if points >= 3: return "REVIEW"
    return "UNKNOWN"

assert quality(6, .90) == "CONFIDENT"
assert quality(5, .65) == "CONFIDENT"
assert quality(5, .40) == "REVIEW"
assert quality(3, .10) == "REVIEW"
assert quality(2, .99) == "UNKNOWN"
print("5/5 v0.8.3 quality policy tests passed")
