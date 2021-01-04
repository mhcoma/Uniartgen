ranges_old:list[range] = [
	range(1, 10),
	range(5, 15),
	range(20, 30),
	range(25, 35),
	range(30, 40),
	range(2, 12),
	range(45, 80)
]

ranges_new:list[range] = []

result = True
while True:
	x = ranges_old[0]
	count = 0
	for i in range(1, len(ranges_old)):
		xs = set(x)
		y = ranges_old[i - count]
		ip = xs.intersection(y)
		if len(ip) > 0:
			begin = min(x.start, y.start)
			end = max(x.stop, y.stop)
			x = range(begin, end)
			ranges_old.pop(i - count)
			count += 1
			result = False
	ranges_new.append(x)
	ranges_old.pop(0)
	if result or len(ranges_old) == 0:
		break

print(ranges_new)