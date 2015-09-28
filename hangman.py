#!/usr/bin/env python

from collections import defaultdict
from operator import or_

DEFAULT_FILENAME = '/etc/dictionaries-common/words'
LETTER_SET = map(chr, range(ord('a'), ord('z')+1))

class Solver(object):

	def next(self, word, lifes, options):
		"""
		Get next character and confidence. Input to this should be
			already sanitized.
		@param word The current word. Unknowns are marked as '-'
		@param lifes Number of lifes remaining
		@param options An enumerable object containing letter options
		@returns A tuple, the first of which being the next char,
			and the next being confidence value
		"""
		for a in options:
			return (a, 0.0)


class NGramStats(object):

	def stats(self, length, filename=DEFAULT_FILENAME):
		stat = defaultdict(int)
		f = open(filename, 'r')
		if not f:
			raise Exception()
		for word in f.readlines():
			word = word.lower().strip()
			if word.isalpha():
				for i in range(len(word) - length + 1):
					stat[word[i:i+length]] += 1
		# canonicalization
		total = sum(stat.values())
		return defaultdict(float, {key: stat[key] * 1.0 / total for key in stat.keys()})

class NGramSolver(Solver):

	def __init__(self, stat, n):
		self.data = stat
		self.n = n

	def next(self, word, lifes, options):
		word =  ''.join([ c if c.isalnum() else '-' for c in word ])
		ans = defaultdict(lambda: 0.0)
		for i in range(len(word) - self.n + 1):
			v = word[i:i + self.n]
			if not v.isalpha():
				for x in options:
					ans[x] += self.data[v.replace('-', x)]
		# print {a: ans[a] for a in list(reversed(sorted(ans.keys(), key=ans.get)))[:10]}
		char = max(ans, key=ans.get)
		return (char, ans[char] / self.n)


class DictParser(object):

	def parse(self, filename=DEFAULT_FILENAME):
		f = open(filename, 'r')
		if not f:
			raise Exception()
		return {key.lower().strip() for key in f.readlines()}
			
class DictSolver(Solver):

	def __init__(self, dct, lim=1000):
		self.dct = dct
		self.lim = lim

	def next(self, word, lifes, options):
		potentials = {}
		for wd in self.dct:
			if len(wd) == len(word):
				pair = zip(wd, word)
				conflict = filter(lambda x: x[1].isalpha() and x[0] != x[1], pair)
				newmatch = filter(lambda x: not x[1].isalpha(), pair)
				if not conflict:
					new_letters = set(zip(*newmatch)[0])
					if not new_letters.intersection(set(word)):
						# New matches should have no letters that 
						#  should've revealed already if correct
						if new_letters.intersection(set(options)) == new_letters:
							# All new letters should be in potentials
							potentials[wd] = new_letters
		if not potentials:
			for x in options:
				return (x, 0)
		letters = reduce(set.union, potentials.values())
		# print potentials
		# We try to split into two even sets so that after this
		#   query, the candidate set size is minimized
		count_occurrence = {x: -sum([int(x in wd) for wd in potentials.keys()]) for x in letters}
		#print count_occurrence
		choice = min(letters, key=count_occurrence.get)
		return (choice, -count_occurrence[choice] * 1.0 / len(potentials))
			

class Bot(Solver):

	def __init__(self):
		self.bots = [NGramSolver(NGramStats().stats(n), n) for n in range(1,4)]
		self.bots.append(DictSolver(DictParser().parse()))
			
	def next(self, word, lifes, options):
		ret = [self.bots[i].next(word, lifes, options) for i in range(len(self.bots))]
		print ret
		choice_pair = min(ret, key=lambda x: -x[1])
		return choice_pair
	
def main():
	demo()
	Bot()

def demo():
	bot = Bot()
	bot.next('a--le', 5, ''.join(LETTER_SET))
	bot.next('a--le', 5, 'bpcdefg')
	bot.next('-----', 5, 'bpcdefg')
	bot.next('a----', 5, ''.join(LETTER_SET))
	bot.next('v-v-d', 5, 'aeiou')
	
def demo2():
	print DictSolver(DictParser().parse()).next('a--le', 5, ''.join(LETTER_SET))
	print DictSolver(DictParser().parse()).next('a--le', 5, 'bpcdefg')
	print DictSolver(DictParser().parse()).next('-----', 5, 'bpcdefg')
	print DictSolver(DictParser().parse()).next('a----', 5, ''.join(LETTER_SET))
	return
	test1()
	test2(1)
	test2(2)
	test2(3)
	

def test2(n):
	data = NGramStats().stats(n)
	s = NGramSolver(data, n)
	print s.next('v-v-d', 5, 'aeiou')

def test1():
	data = NGramStats().stats(3)
	tops = sorted(data.keys(), key=data.get)
	print {a: data[a] for a in list(reversed(tops))[:10]}

if __name__ == '__main__':
	main()
