from random import randint, shuffle, sample

# Classe représentant une case de la grille
class Box:
    def __init__(self, value: int, locked: bool = False):
        """
        Initialise une case de Sudoku avec une valeur et un indicateur si la case est verrouillée ou non.
        
        Args:
            value (int): La valeur de la case (0 pour une case vide).
            locked (bool): Indique si la case est verrouillée (True) ou modifiable (False).
        """
        self.value = value
        self.locked = locked
    
    def __str__(self) -> str:
        """
        Représentation d'une case sous forme de chaîne. 
        Retourne un point '.' si la case est vide (0), sinon sa valeur.
        
        Returns:
            str: La représentation de la case.
        """
        return str(self.value) if self.value != 0 else '.'

# Classe représentant une grille de Sudoku
class Grid:
    def __init__(self):
        """
        Initialise une grille 9x9 vide (toutes les cases à 0).
        """
        self.grid = [[Box(0) for _ in range(9)] for _ in range(9)]
        self.initial_grid = [[Box(0) for _ in range(9)] for _ in range(9)]
    
    def __str__(self) -> str:
        """
        Représentation lisible de la grille sous forme de chaîne de caractères.
        Inclut des séparateurs pour diviser la grille en blocs 3x3.
        
        Returns:
            str: La représentation de la grille.
        """
        string = ""
        horizontal_separator = "+-------+-------+-------+\n"
        
        for i, row in enumerate(self.grid):
            if i % 3 == 0:
                string += horizontal_separator
            for j, box in enumerate(row):
                if j % 3 == 0:
                    string += "| "
                string += ". " if box.value == 0 else str(box.value) + " "
            string += "|\n"
        string += horizontal_separator
        return string
    
    def generate(self, level: int) -> None:
        """
        Génère une grille de Sudoku partiellement remplie selon le niveau de difficulté.
        
        Args:
            level (int): Nombre de cases à vider après la génération de la solution.
        """
        # Réinitialisation de la grille à vide
        self.grid = [[Box(0) for _ in range(9)] for _ in range(9)]

        # Remplissage de quelques cases initiales avec des valeurs valides
        for _ in range(10):
            row, col = randint(0, 8), randint(0, 8)
            
            while self.grid[row][col].value != 0:
                row, col = randint(0, 8), randint(0, 8)
                
            liste_elements = list(range(1, 10))
            shuffle(liste_elements)

            while not self.is_valid(col, row, liste_elements[0]) and len(liste_elements) > 0:
                liste_elements.pop(0)
            self.grid[row][col].value = liste_elements[0]
        
        # Résolution de la grille
        self.solve()

        # Vidage de quelques cases en fonction du niveau de difficulté
        for _ in range(level):
            row, col = randint(0, 8), randint(0, 8)
            
            while self.grid[row][col].value == 0:
                row, col = randint(0, 8), randint(0, 8)
            self.grid[row][col].value = 0

        # Convertir les entiers en objets Box avec statut verrouillé ou non
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                self.grid[x][y].locked = True if self.grid[x][y].value else False
        self.initial_grid = [[Box(cell.value, cell.locked) for cell in row] for row in self.grid]

    def is_valid(self, col: int, row: int, number: int, initial: bool = False) -> bool:
        """
        Vérifie si un élément peut être placé à une position donnée sans violer les règles du Sudoku.
        
        Args:
            col (int): Colonne où placer l'élément.
            row (int): Ligne où placer l'élément.
            number (int): Valeur à placer dans la case.
            initial (bool): Indique si la vérification se fait sur la grille initiale.
        
        Returns:
            bool: True si l'élément peut être placé, sinon False.
        """
        grid = self.initial_grid if initial else self.grid
        
        if not (0 <= col <= 8) or not (0 <= row <= 8) or not (1 <= number <= 9):
            return False
        if grid[row][col].locked:
            return False
        # Vérifie la ligne et la colonne
        for test in range(9):
            if number == grid[row][test].value or grid[test][col].value == number:
                return False

        # Vérifie le bloc 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j].value == number:
                    return False
        return True

    def find_empty_cell(self) -> tuple[int, int] | None:
        """
        Trouve une cellule vide (valeur 0) dans la grille.
        
        Returns:
            tuple[int, int] | None: Un tuple (row, col) ou None si aucune cellule vide n'est trouvée.
        """
        for row in range(9):
            for col in range(9):
                if self.grid[row][col].value == 0:
                    return (row, col)
        return None

    def solve(self) -> bool:
        """
        Résout la grille en utilisant la technique de backtracking.
        
        Returns:
            bool: True si une solution est trouvée, sinon False.
        """
        cell = self.find_empty_cell()
        if cell is None:
            return True
        
        row, col = cell

        for number in sample(range(1, 10), 9):  # Génére les nombres de 1 à 9 dans un ordre aléatoire
            if self.is_valid(col, row, number):
                self.grid[row][col].value = number
                if self.solve():
                    return True
                # Retour en arrière si la solution ne fonctionne pas
                self.grid[row][col].value = 0
        return False

    def is_allowed(self, col: int, row: int) -> bool:
        """
        Vérifie si une case donnée peut être modifiée par l'utilisateur.
        
        Args:
            col (int): Colonne de la case.
            row (int): Ligne de la case.
        
        Returns:
            bool: True si la case est modifiable (non verrouillée), sinon False.
        """
        return not self.grid[row][col].locked

    def set_element(self, col: int, row: int, element: int) -> bool:
        """
        Définit un élément dans la grille si l'emplacement est valide et modifiable.
        
        Args:
            col (int): Colonne de la case.
            row (int): Ligne de la case.
            element (int): Valeur à insérer dans la case.
        
        Returns:
            bool: True si l'insertion a été effectuée, sinon False.
        """
        
        if not self.is_valid(col, row, element, initial=True):
            return False

        self.grid[row][col].value = element
        return True

    def get_9x9(self) -> list[list[Box]]:
        """
        Retourne la grille sous forme de liste 9x9 d'objets Box.
        
        Returns:
            list[list[Box]]: La grille de Sudoku.
        """
        return self.grid

    def get_81(self, rb: int = 0, cb: int = 0, row: int = 0, col: int = 0, g: list[Box] = None) -> list[Box]:
        """
        Retourne la grille sous forme de liste linéaire de 81 objets Box.
        
        Args:
            rb (int): Bloc de ligne.
            cb (int): Bloc de colonne.
            row (int): Ligne dans le bloc.
            col (int): Colonne dans le bloc.
            g (list[Box]): Liste des cases.
        
        Returns:
            list[Box]: La grille de Sudoku sous forme linéaire.
        """
        if g is None:
            g = []
        if rb == 3:
            return g
        if cb == 3:
            return self.get_81(rb + 1, 0, 0, 0, g)
        if row == 3:
            return self.get_81(rb, cb + 1, 0, 0, g)
        if col == 3:
            return self.get_81(rb, cb, row + 1, 0, g)
        
        g.append(self.grid[rb*3 + row][cb*3 + col])
        return self.get_81(rb, cb, row, col + 1, g)
    
    def is_solved(self, row: int = 0, col: int = 0) -> bool:
        """
        Vérifie si la grille est résolue.
        
        Args:
            row (int): Ligne actuelle.
            col (int): Colonne actuelle.
        
        Returns:
            bool: True si la grille est résolue, sinon False.
        """
        if row > 8:
            return True
        
        value = self.grid[row][col].value

        if not (1 <= value <= 9):
            return False
        
        for test in range(9):
            if (test != col and value == self.grid[row][test].value) or (row != test and self.grid[test][col].value == value):
                return False

        # Vérifie le bloc 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if i != row%3 or j != col%3:
                    if self.grid[start_row + i][start_col + j].value == value:
                        return False
        
        return self.is_solved(row+(1 if col==8 else 0), (col+1)%9)
                
g = Grid()
print(g.generate(0))