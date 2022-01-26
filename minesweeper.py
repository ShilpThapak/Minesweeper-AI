import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells.copy()
        else:
            return None
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        else:
            return None
        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1
        # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        # raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # All possible cells
        self.all_cells = []
        for i in range(self.height):
            for j in range(self.width):
                    self.all_cells.append((i, j))


    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print(f"safe moves: {self.safes}")
        print(f"mines detected: {self.mines}")
        # 1.
        self.moves_made.add(cell)
        print(f"added {cell} to moves made")
        
        # 2.
        self.mark_safe(cell)
        print(f"marked {cell} as safe in all sentences")
        
        # 3.
        set_of_cells = set()
        i = cell[0]
        j = cell[1]
        i_list = [i-1, i, i+1]
        j_list = [j-1, j, j+1]

        for x in i_list:
            for y in j_list:
                if x >= 0 and x < self.width and y >=0 and y < self.height and (x , y) != (i, j):
                    set_of_cells.add((x, y))
        sentence_obj = Sentence(set_of_cells, count)
        print(f"Found {count} mines in these cells: {set_of_cells}")
        
        if sentence_obj not in self.knowledge:
            self.knowledge.append(sentence_obj)

        # 4.
        mines = sentence_obj.known_mines()
        safes = sentence_obj.known_safes()
        print(mines, safes)
        for sentence in self.knowledge:
            if sentence == sentence_obj:
                continue
            if mines is not None:
                mines_copy = sentence_obj.known_mines().copy()
                for mine in mines_copy:
                    sentence.mark_mine(mine)
                    self.mark_mine(mine)
                    print(f"{mine} marked as mine.")
            if safes is not None:
                safes_copy = sentence_obj.known_safes().copy()
                for safe in safes_copy:
                    sentence.mark_safe(safe)
                    self.mark_safe(safe)
                    print(f"{safe} marked as safe.")
        
        for sentence in self.knowledge:
            # moves_made_cells = sentence.cells.intersection(self.moves_made)
            moves_not_made_cells = sentence.cells.difference(self.moves_made)
            # no_of_moves_made_cells = len(moves_made_cells)
            if len(moves_not_made_cells) == sentence.count:
                for cell in moves_not_made_cells:
                    self.mark_mine(cell)

            mines_in_cells = sentence.cells.intersection(self.mines)
            possible_safe_cells = sentence.cells.difference(mines_in_cells)
            if sentence.count == len(mines_in_cells):
                for cell in possible_safe_cells:
                    self.mark_safe(cell)
            

        # if mines is not None:
        #     mines_copy = mines.copy()
        #     for mine in mines_copy:
        #         sentence_obj.mark_mine(mine)
        #         self.mark_mine(mine)
        #         print(f"{mine} marked as mine.")
        # if safes is not None:
        #     safes_copy = safes.copy()
        #     for safe in safes_copy:
        #         sentence_obj.mark_safe(safe)
        #         self.mark_safe(safe)
        #         print(f"{safe} marked as safe.")

        # 5.
        for sentence in self.knowledge:
            for item in self.knowledge:
                # print(sentence.cells)
                if item == sentence:
                    continue
                if item.cells.issubset(sentence.cells):
                    new_set = sentence.cells.difference(item.cells)
                    new_count = sentence.count - item.count
                    new_sentence = Sentence(new_set, new_count)
                # if sentence.cells.issubset(item.cells):
                #     new_set = item.cells.difference(sentence.cells)
                #     new_count = item.count - sentence.count
                #     new_sentence = Sentence(new_set, new_count)
                #     if len(new_sentence.cells) != 0:
                #         self.knowledge.append(new_sentence)
            # print(sentence.cells, sentence.count)
        
        if mines is not None:
            mines_copy = mines.copy()
            for mine in mines_copy:
                sentence_obj.mark_mine(mine)
                self.mark_mine(mine)
                print(f"{mine} marked as mine.")
        if safes is not None:
            safes_copy = safes.copy()
            for safe in safes_copy:
                sentence_obj.mark_safe(safe)
                self.mark_safe(safe)
                print(f"{safe} marked as safe.")


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                print(cell)
                return cell
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = set(self.all_cells).difference(self.mines).difference(self.moves_made)
        possible_moves = list(possible_moves)
        if len(possible_moves) != 0:
            move_to_be_made = random.choice(possible_moves)
            print(move_to_be_made)
            return move_to_be_made
        else:
            return None
