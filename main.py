import sys
import string
import queue
import collections


# Created by Isaiah Kim.
# 
# Code divided up into:
#   INPUT HANDLING
#   GLOBAL VARIABLES
#   DATA STRUCTURES
#   CONSTANTS
#   FUNCTIONS
#   SCRIPT
#   
# The purpose of this is to find the Levenshtein distance between two given
# words and with each of the four possible operations given different "costs".
# Additionally, no interim step can be less than three letters long.
# The code prints out the minimum cost of the transformation, or -1 if no such
# thing is possible.


### INPUT HANDLING ###

input_file = open("input.txt", "r")

try: 
  first_line = [int(i) for i in input_file.readline().strip().split()]
except ValueError:
  input_file.close()
  sys.exit("ERROR: Element in first line of input\
    cannot be converted into an integer.")

cost_count = len(first_line)
if cost_count != 4:
  input_file.close()
  sys.exit("ERROR: There are " + str(cost_count) + 
    " integers in the first line of input, when there should be four.")

add_cost, delete_cost, change_cost, anagram_cost = \
  [int(i) for i in first_line]

dict_file = open("words_alpha.txt", "r")
word_list = dict_file.read().strip().split()
dict_file.close()

start_word = input_file.readline().strip().lower()
end_word = input_file.readline().strip().lower()

if input_file.readline() != '':
  input_file.close()
  sys.exit("ERROR: There are more than three lines of input.")

input_file.close()

if start_word == '':
  sys.exit("ERROR: Second line of input is missing.")
if end_word == '':
  sys.exit("ERROR: Third line of input is missing.")

if len(start_word) < 3:
  sys.exit("ERROR: Starting word is too short.")
if len(end_word) < 3:
  sys.exit("ERROR: Ending word is too short.")

if start_word not in word_list:
  sys.exit("ERROR: Starting word is not in the dictionary.")
if end_word not in word_list:
  sys.exit("ERROR: Ending word is not in the dictionary.")
  
### GLOBAL VARIABLES ###

solution = False # If true, any op with a cost over the min_cost is ignored
min_cost = -1    # No purpose unless solution is true

### DATA STRUCTURES ###


# word_queue stores interim words by priority, but the priority of a word
# does not directly correspond to the Levenshtein distance between the
# start_word and said word.
# 
# word_costs is a dictionary containing the actual cheapest found
# Levenshtein distance to achieve that word.
# 
# word_costs, the dictionary, is raw cost while word_queue, the PriorityQueue
# also incorporates a heuristic to help improve average runttime.
# 
# This allows the search for the fastest route to the end_word to transform
# from a Depth First Search into a A* Search with a better average runtime. 
# The heuristic() function is also consistent, and never assumes an operation
# that is unnecessary. This permits a condition in the script to break out of
# the loop when estimated costs get too high instead of worrying about an edge
# case where the correct answer is lost due to a poor heuristic evaluation.
word_queue = queue.PriorityQueue()
word_costs = {}

### CONSTANTS ###

alphabet = string.ascii_lowercase
end_len = len(end_word) # Number of letters in end_word

# Necessary for the heuristic to properly estimate how much it costs
# to change out a letter. add_op+delete_op could do what a change_op does.
# There are situations where only a change_op works, but this heuristic
# needs to be simple for runtime sake.
change_estimate = min(change_cost, add_cost + delete_cost)

### FUNCTIONS ###

def check_word(word, cost, bypass=False):
  global solution, min_cost
  if (word == end_word) and ((not solution) or (cost < min_cost)):
    solution = True
    min_cost = cost
    print(word)
    print(cost)
    return True
  elif bypass or (word in word_list):
    # Added if first or cheapest instance of the word
    if (word not in word_costs) or \
      (word_costs[word] > cost):
      new_cost = cost + heuristic(word)
      if (not solution) or (new_cost < min_cost):
        word_queue.put((new_cost, word))
        word_costs[word] = cost
    return False

# Roughly evaluates each word's "distance" to the end_word 
# NOTE: Not sure how to quickly evaluate the need for anagram_op
# Currently vulnerable to expensive anagram costs and repeated 
# letters. Also some time is wasted on adding/changing letters
# in an obviously poor location. 
def heuristic(word):
  bias = 0
  len_dif = len(word) - end_len 
  if len_dif > 0:
    bias += len_dif * delete_cost
  else: # -= not += as len_dif is not positive in this case
    bias -= len_dif * add_cost 

  bias += max(0, # Letters that must be changed w/ change_op
    max(         # or an add_op/delete_op combination
    len([x for x in word if x not in end_word]) - len_dif, 
    len([x for x in end_word if x not in word]) + len_dif)
    ) * change_estimate
  return bias
  
# n letters, n+1 places to add a letter
def add_op(word, cost):
  for i in range(len(word) + 1):
    for letter in alphabet:
      if check_word(word[:i] + letter + word[i:], cost):
        return

def delete_op(word, cost):
  for i in range(len(word)):
    if check_word(word[:i] + word[i+1:], cost):
      return

def change_op(word, cost):
  for i in range(len(word)):
    for letter in alphabet:
      if check_word(word[:i] + letter + word[i+1:], cost):
        return

def anagram_op(word, cost):
  for real_word in word_list:
    if collections.Counter(real_word) == collections.Counter(word):
      check_word(real_word, cost, True) 
  
### SCRIPT ###
    
word_queue.put((0, start_word))
word_costs[start_word] = 0
while not word_queue.empty():
  target = word_queue.get()[1]
  print(target)
  old_cost = word_costs[target]
  if (old_cost > min_cost) and solution:
    break # Don't waste time if we don't find a better answer
  if (not solution) or (old_cost + add_cost < min_cost):
    add_op(target, old_cost+add_cost)
  if ((not solution) or (old_cost + delete_cost < min_cost)) and \
    (len(target) > 3): # Ensure all steps are three letters or longer
    delete_op(target, old_cost+delete_cost)
  if (not solution) or (old_cost + change_cost < min_cost):
    change_op(target, old_cost+change_cost)
  if (not solution) or (old_cost + anagram_cost < min_cost):
    anagram_op(target, old_cost+anagram_cost)
print(min_cost)