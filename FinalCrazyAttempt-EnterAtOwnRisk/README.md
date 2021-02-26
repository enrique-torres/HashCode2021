# Explanation

For our initial idea, we give weights to each road based on the points obtained by the cars that pass through them. More points = that stoplight gets more green light time. The relationship is not linear though, we tried different sublinear functions (e.g. sqrt or log) so 10x the score does not mean 10x green light time, just ~2x or something like that

Anyway, we wrote this when there were 30 minutes remaining:

It creates an initial schedule using the logic from before, but now we had two ideas:

- (commented code) Sample random cars, try to follow their path, give more weight to the stoplights along the path proportional to the time that the car had to wait

- (current implementation, un-commented code) Try to simulate all the cars at the same time. Similar idea, more wait time on average = more points. Repeat this improvement a few times and hope that it gets better (spoiler: it doesn't). Do not forget to multiply the results by 72, or else it does not work.


