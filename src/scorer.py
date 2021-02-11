# Python program to keep scores for Suraj TR's "Who is this Plusser?" competition.
# Author: Umesh P. Narendran, Feb 2021.

import re
import sys

# Change this to True to print debug statements to stdout.
debug = False


class AaplaScorer:

    def __init__(self, infile, outfile):
        """
        :param infile: The input textfile.  Format: "<Guesser> <Guess>"
        :param outfile: The output LaTeX file.  Contains code for the resulting table, to be included in main file.
        """
        self.infile, self.outfile = infile, outfile

        # Internal maps.
        self.guessMap = dict()  # Guesser -> Last guess.
        self.guessNo = dict()   # Guesser -> Last guess' comment number.
        self.nAnswers = dict()  # Guesser -> Number of answers posted.

        # Input line format.  <guesser> <guess>
        self.format = re.compile(r"([a-zA-Z]+)[ \t]+([a-zA-Z]+)")

        # Initialized to None.  When the answer is revealed, "Answer <guess"" will be added as the first line
        # in the input file.
        self.answer = None

        # Serial number of a comment.
        self.comment_no = 0

    def score(self):
        """Reads the input file, compute scores, and creates the output file."""
        self.__read_data()

        if debug:
            scorer.__print_map()

        self.__sort_and_print_results()

    def __add_suggestion(self, guesser, guess):
        """ Adds a guesser and the guess to various maps."""

        if guesser in self.guessMap:
            # This guesser has already given answer.

            self.nAnswers[guesser] += 1
            old_guess = self.guessMap[guesser]
            if old_guess != guess:
                # Guesser has changed the guess.
                self.comment_no += 1
                self.guessMap[guesser] = guess
                self.guessNo[guesser] = self.comment_no
                if debug:
                    print("%s has a new guess %s, rank = %d" % (guesser, guess, self.comment_no))
            else:
                # Guesser repeated last guess.  Ignore.
                if debug:
                    print("%s repeated the guess %s" % (guesser, guess))
        else:
            # This is this guesser's first guess.
            self.comment_no += 1
            self.nAnswers[guesser] = 1
            self.guessMap[guesser] = guess
            self.guessNo[guesser] = self.comment_no

            if debug:
                print("%s has the FIRST guess %s, rank = %d" % (guesser, guess, self.comment_no))

    def __print_map(self):
        """Print the guess map for debugging."""

        for guesser in self.guessMap:
            print ("\\%s & \\%s & %d\\\\" % (guesser, self.guessMap[guesser], self.guessNo[guesser]))

    def __read_data(self):
        """ Reads data from an input text file.  Each entry is in the form of format."""

        with open(self.infile, "r") as fp:
            line = fp.readline()
            line = line[:-1]
            while line:
                m = self.format.match(line)
                if m:
                    guesser, guess = m.group(1), m.group(2)
                    if guesser == "Answer":
                        self.answer = guess
                    else:
                        self.__add_suggestion(guesser, guess)
                line = fp.readline()

    def __sort_and_print_results(self):
        """Prints a table with results as LaTeX code. """
        # Line formats.

        # <Guess> & <Number> & <Guesser> & <Comment Number> & <Suraj Points> & <Umesh Points> & <Blank>
        no_bonus_line_format = "%-25s & %2d & %-10s & %2d & %2d & %2d & \\\\\n"

        # <Guess> & <Number> & <Guesser> & <Comment Number> & <Suraj Points> & <Umesh Points> & (<Original points> + 1)
        bonus_line_format = "%-25s & %2d & %-10s & %2d & %2d & %2d & (%d + 1)\\\\\n"

        guess_list = []
        for guesser in self.guessMap:
            guess = self.guessMap[guesser]
            no = self.guessNo[guesser]
            guess_list.append([guess, no, guesser])

        # Sort the entries in the alphabetical order of the guesses, and then the comment number.
        guess_list.sort(key=lambda x: (x[0], x[1]))

        # If the answer is revealed, sort it as the first entry.
        if self.answer is not None:
            guess_list.sort(key=lambda x: x[0] != self.answer)

        sub_no = 0
        old_guess = ""

        with open(self.outfile, "w") as fp:

            # Print table heading.
            fp.write("\\begin{tabular}{|l|rl|r|r|rc|}\n")
            fp.write("\\hline\n")
            fp.write("\\textbf{Guess} & \\multicolumn{2}{c|}{\\textbf{Guesser}} & \\textbf{\\#}")
            fp.write(" & \\multicolumn{3}{c|}{\\textbf{Points}} \\\\\n")
            fp.write("\\cline{5-7}\n")
            fp.write("& & &  & \\textbf{Suraj} & \\multicolumn{2}{c|}{\\textbf{Umesh}} \\\\\n")

            for element in guess_list:
                (guess, no, guesser) = element
                if old_guess != guess:
                    fp.write("\\hline\n")
                    sub_no = 1
                    if self.answer is not None and self.answer == guess:
                        guess_name = "\\textbf{" + guess + "}"
                    else:
                        guess_name = guess
                    old_guess = guess
                else:
                    sub_no += 1
                    guess_name = " "

                suraj_points = 5 if sub_no == 1 else 2
                umesh_points = 11 - sub_no if sub_no < 11 else 0

                if self.answer is None:
                    # The answer is not yet revealed.  Print in alphabetical order, and points for all.
                    fp.write(no_bonus_line_format % (
                        guess_name, sub_no, guesser, no, suraj_points, umesh_points))
                elif self.answer == guess:
                    # Print with the answer as first entry, and points given only to the correct guessers.
                    if self.nAnswers[guesser] == 1 and umesh_points > 0:
                        # Give one bonus point if the guesser had only one guess.
                        fp.write(bonus_line_format % (
                            guess_name, sub_no, guesser, no, suraj_points, umesh_points + 1, umesh_points))
                    else:
                        # Just the points if not guessed at the first attempt.
                        fp.write(no_bonus_line_format % (
                            guess_name, sub_no, guesser, no, suraj_points, umesh_points))

                else:
                    # 0 points for wrong guesses.
                    fp.write(no_bonus_line_format % (guess_name, sub_no, guesser, no, 0, 0))

            fp.write("\\hline\n")
            fp.write("\\end{tabular}\n")


# The main program.
# Usage: python <prog> <input-file> <output-file>
if __name__ == "__main__":
    scorer = AaplaScorer(sys.argv[1], sys.argv[2])
    scorer.score()
