from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.animation import Animation
from kivy.uix.image import AsyncImage

from backend import Grid  # Importation de la classe Grid du backend

APP_COLORS = {
        'blue': [0.38, 0.698, 1, 1],  # Couleur de fond des cellules modifiables
        'dark_blue': [0.2, 0.4, 0.8, 1],  # Couleur des cellules préremplies
        'navy': [0, 0, 0.5, 1],  # Couleur de la cellule sélectionnée
        'green': [0.3, 0.8, 0.3, 1],  # Couleur verte
        'red': [0.8, 0.3, 0.3, 1],  # Couleur rouge
        'yellow': [0.8, 0.8, 0.3, 1],  # Couleur jaune
        'white': [1, 1, 1, 1],  # Texte blanc
        'grey': [0.7, 0.7, 0.7, 1], # Texte gris
        'black': [0, 0, 0, 1]  # Texte noir
    }

LEVELS = [
            (35, "Facile", APP_COLORS['green']),
            (50, "Intermédiaire", APP_COLORS['yellow']),
            (65, "Difficile", APP_COLORS['red']),
        ]

GRID_BACKEND = Grid()

class SudokuCell(Button):
    """
    Représente une cellule individuelle du Sudoku (bouton).

    Attributs :
        coordinates (tuple) : Les coordonnées (ligne, colonne) de la cellule dans la grille.
        parentWidget (SmallGrid) : Référence au parent (petite grille 3x3).
        font_size (int) : Taille de la police pour afficher les chiffres.
        halign (str) : Alignement horizontal du texte.
        multiline (bool) : Indique si plusieurs lignes sont autorisées (toujours False ici).
        background_color (list) : Couleur de fond de la cellule.
        foreground_color (list) : Couleur du texte de la cellule.
    """

    def __init__(self, coordinates, parentWidget):
        super().__init__()
        self.coordinates = coordinates
        self.parentWidget = parentWidget
        self.font_size = 32
        self.halign = 'center'
        self.multiline = False
        self.background_normal = ''

        self.background_color = APP_COLORS['blue']
        self.foreground_color = APP_COLORS['white']
        self.background_disabled_normal = ''
        self.background_down = ''

    def on_press(self):
        """
        Gère l'action lors du clic sur la cellule.
        - Sélectionne la cellule.
        - Désactive les boutons numériques invalides.
        """
        self.select_cell()
        self.disable_buttons()

    def select_cell(self):
        """
        Met en évidence la cellule sélectionnée et réinitialise la sélection des autres cellules.
        """
        self.parentWidget.parentWidget.parentWidget.selectedCell = self
        for smallgrid in self.parentWidget.parentWidget.children:
            for cell in smallgrid.children:
                if not cell.disabled:
                    anim = Animation(background_color=APP_COLORS['blue'], duration=0.2)
                    anim.start(cell)
        anim = Animation(background_color=APP_COLORS['navy'], duration=0.2)
        anim.start(self)


    def disable_buttons(self):
        """Désactive les boutons non valides pour la cellule sélectionnée."""
        gameScreen:GameScreen = self.parentWidget.parentWidget.parentWidget
        buttons = gameScreen.button_layout.children
        for button in buttons:
            button:Button = button
            if GRID_BACKEND.is_valid(col=self.coordinates[1], row=self.coordinates[0], number=int(button.text), initial=True):
                button.disabled = False
            else:
                button.disabled = True



class SmallGrid(GridLayout):
    """
    Représente une petite grille 3x3 dans la grande grille Sudoku.

    Attributs :
        row (int) : Indice de la ligne de la petite grille dans la grande grille.
        col (int) : Indice de la colonne de la petite grille dans la grande grille.
        parentWidget (BigGrid) : Référence au parent (grande grille).
    """

    def __init__(self, row, col, parentWidget):
        super().__init__()
        self.parentWidget = parentWidget
        self.cols = self.rows = 3
        self.spacing = [2, 2]

        for rowCel in range(3):
            for colCel in range(3):
                cell = SudokuCell(coordinates=(row*3+rowCel, col*3+colCel), parentWidget=self)
                self.add_widget(cell)


class BigGrid(GridLayout):
    """
    Représente la grande grille Sudoku contenant 9 petites grilles 3x3.

    Attributs :
        parentWidget (GameScreen) : Référence à l'écran de jeu.
    """

    def __init__(self, parentWidget):
        super().__init__()
        self.parentWidget = parentWidget
        self.cols = self.rows = 3
        self.spacing = (10, 10)  # Espacement entre les petites grilles

        # Création des 9 petites grilles
        for row in range(3):
            for col in range(3):
                small_grid = SmallGrid(row, col, parentWidget=self)
                self.add_widget(small_grid) # Ajoute la petite grille à la mise en page

    def set_grid_value(self):
        """
        Met à jour les valeurs de la grande grille en fonction des données du backend.

        Fonctionnement :
        - Met à jour les cellules avec les valeurs actuelles.
        - Configure les cellules comme modifiables ou verrouillées selon le backend.
        """
        grid_values = [box.value for box in GRID_BACKEND.get_81()][::-1]
        for i, small_grid in enumerate(self.children):
            values = grid_values[i * 9:(i + 1) * 9]

            for j, value in enumerate(values):
                cell = small_grid.children[j]
                row, col = cell.coordinates
                if GRID_BACKEND.grid[row][col].value == 0:
                    cell.text = ''
                    cell.disabled = False
                    cell.background_color = APP_COLORS['blue']
                elif not GRID_BACKEND.grid[row][col].locked:
                    cell.disabled = False
                    cell.text = str(value)
                    cell.background_color = APP_COLORS['blue']
                else:
                    cell.disabled = False
                    cell.text = str(value)
                    cell.background_color = APP_COLORS['dark_blue']
                    cell.disabled_color = APP_COLORS['white']
                    cell.disabled = True
        if self.parent.parent.selectedCell:
            self.parent.parent.selectedCell.background_color=APP_COLORS['navy']

class GameScreen(Screen):
    """
    Représente l'écran de jeu principal avec la grille Sudoku et les options.

    Attributs :
        parentWidget (SudokuApp) : Référence à l'application principale.
        name (str) : Nom de l'écran.
        selectedCell (SudokuCell) : Référence à la cellule actuellement sélectionnée.
        grid (BigGrid) : Grande grille 9x9 affichée dans l'écran.
    """

    def __init__(self, parentWidget, name):
        """ initialise l'ecran principal"""
        super().__init__()
        self.parentWidget = parentWidget
        self.name = name
        self.selectedCell = None
        main_layout = BoxLayout(orientation='vertical') # Mise en page principale verticale

        # Boutons pour sélectionner les chiffres (1 à 9)
        self.button_layout = GridLayout(cols=9, size_hint=(1, 0.1))
        for number in range(1, 10):
            button = Button(text=str(number), font_size=32)
            button.bind(on_release=self.clickButton)
            self.button_layout.add_widget(button)

        # Grande grille 9x9
        self.grid = BigGrid(self)

        main_layout.add_widget(self.grid)
        main_layout.add_widget(self.button_layout)
        self.add_widget(main_layout)

        back_to_menu_button = Button(text="Retour au Menu", size_hint=(1, 0.1), font_size=32)
        back_to_menu_button.on_release = self.back_to_menu
        main_layout.add_widget(back_to_menu_button)

    def start_game(self, lvl):
        """
        Démarre une nouvelle partie avec le niveau de difficulté choisi.

        Paramètres :
            lvl (int) : Niveau de difficulté choisi (nombre de cellules vides dans la grille).
        """
        GRID_BACKEND.generate(lvl)
        self.selectedCell = None
        self.grid.set_grid_value()

    def clickButton(self, value):
        """
        Gère les clics sur les boutons numériques pour insérer des valeurs dans une cellule.

        Paramètres :
            value (Button) : Bouton numérique cliqué (texte représentant un chiffre entre 1 et 9).
        """
        if self.selectedCell == None:
            return
        coordinates = self.selectedCell.coordinates

        GRID_BACKEND.set_element(coordinates[1], coordinates[0], int(value.text))

        self.grid.set_grid_value()

        if self.is_grid_full():
            self.got_resolved()

    def back_to_menu(self, instance=None):
        """
        Retourne à l'écran du menu principal.

        Paramètres :
            instance (Button, optionnel) : Bouton déclenchant l'action.
        """
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu' # change l'ecran actif

    def is_grid_full(self):
        """
        Vérifie si la grille est entièrement remplie.

        Retour :
            bool : True si toutes les cellules sont remplies, sinon False.
        """
        for row in GRID_BACKEND.grid:
            for cell in row:
                if cell.value == 0:
                    return False
        return True

    def got_resolved(self):
        """
        Passe à l'écran de victoire si la grille est correctement résolue.
        """
        if GRID_BACKEND.is_solved():
            self.manager.transition = SlideTransition(direction='down')
            self.manager.current = 'win' # change l'ecran actif





class MenuScreen(Screen):
    """
    Écran principal pour sélectionner le niveau de difficulté ou passer aux regles

    Attributs :
        kwargs (dict) : Arguments supplémentaires pour initialiser l'écran.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        title_label = Label(
            text="Bienvenue dans notre app Sudoku !",
            font_size=40,
            size_hint=(1, 0.2),
            color=APP_COLORS['white']
        )
        layout.add_widget(title_label)

        instruction_label = Label(
            text="Choisissez un niveau de difficulté :",
            font_size=24,
            size_hint=(1, 0.1),
            color=APP_COLORS['grey']
        )
        layout.add_widget(instruction_label)

        # Conteneur pour les boutons de niveau
        button_container = GridLayout(cols=3, spacing=20, size_hint=(1, 3))


        for level, text, color in LEVELS:
            button = Button(
                text=text,
                font_size=24,
                background_color=color,
                color=APP_COLORS['white'],
                size_hint=(0.8, 0.8)
            )
            button.bind(on_release=lambda instance, lvl=level: self.select_level(lvl))
            button_container.add_widget(button)

        layout.add_widget(button_container)

        # Pied de page
        footer_label = Label(
            text="Amusez-vous bien !",
            font_size=20,
            size_hint=(1, 0.1),
            color=APP_COLORS['grey']
        )
        layout.add_widget(footer_label)

        center_layout = BoxLayout(orientation='vertical')

        button_rules = Button(
            text='Afficher les règles du jeu',
            font_size=24,
            background_color=APP_COLORS['dark_blue'],
            color=APP_COLORS['white'],
            size_hint=(1, 0.0),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centre le bouton horizontalement et verticalement
        )
        button_rules.on_release = self.show_rules

        # Ajoutez le bouton au layout centré
        center_layout.add_widget(button_rules)
        layout.add_widget(center_layout)


        self.add_widget(layout)

    def select_level(self, level):
        """
        Passe à l'écran de jeu et démarre une partie avec le niveau de difficulté choisi.

        Paramètres :
            level (int) : Niveau de difficulté choisi (nombre de cellules vides dans la grille).
        """
        self.manager.get_screen('game').start_game(level)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'

    def show_rules(self):
        """
        Passe à l'écran affichant les règles du jeu.
        """
        self.manager.transition = SlideTransition(direction='up')
        self.manager.current = 'rules'



class RuleScreen(Screen):
    """
    Écran affichant les règles du jeu.

    Attributs :
        name (str) : Nom de l'écran.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        title_label = Label(
            text="Règles du jeu",
            font_size=40,
            size_hint=(1, 0.1),  # Adjusted size_hint to prevent overflow
            color=APP_COLORS['white']
        )
        layout.add_widget(title_label)

        # Add an image at the top
        img = AsyncImage(source='./Assets/rules.png', size_hint=(1, 0.3))
        layout.add_widget(img)

        rules_text = (
            "1. Le but du jeu est de remplir une grille de 9x9 avec des chiffres.\n"
            "2. Chaque ligne doit contenir les chiffres de 1 à 9 sans répétition.\n"
            "3. Chaque colonne doit également contenir les chiffres de 1 à 9 sans répétition.\n"
            "4. Chaque sous-grille de 3x3 doit contenir les chiffres de 1 à 9 sans répétition.\n"
            "5. Les chiffres déjà présents dans la grille ne peuvent pas être modifiés.\n"
            "6. Le jeu est terminé lorsque toutes les cases sont remplies correctement."
        )

        rules_label = Label(
            text=rules_text,
            font_size=24,
            size_hint=(1, 0.8),
            color=APP_COLORS['grey'],
            halign='left',
            valign='center',
        )
        rules_label.bind(size=rules_label.setter('text_size'))  # For text wrapping
        layout.add_widget(rules_label)

        back_button = Button(
            text='Retour au Menu',
            font_size=24,
            background_color=APP_COLORS['dark_blue'],
            color=APP_COLORS['white'],
            size_hint=(1, 0.1),  # Adjusted size_hint to match title label
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centre le bouton horizontalement et verticalement
        )
        back_button.bind(on_release=self.show_menu)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def show_menu(self, instance):
        """
        Retourne à l'écran du menu principal.

        Paramètres :
            instance (Button) : Bouton déclenchant l'action.
        """
        self.manager.transition = SlideTransition(direction='down')
        self.manager.current = 'menu'  # Retourne à l'écran du menu principal



class WinScreen(Screen):
    """
    Écran affiché lorsque le joueur résout correctement une grille.

    Attributs :
        kwargs (dict) : Arguments supplémentaires pour initialiser l'écran.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()

    def create_ui(self):
        """
        Configure l'interface utilisateur de l'écran de victoire.
        """
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Add a congratulatory image or logo
        img = AsyncImage(source='./Assets/win.png', size_hint=(1, 0.4))
        layout.add_widget(img)

        # Add congratulatory message
        label = Label(
            text="Félicitations !\nVous avez gagné !",
            font_size='24sp',
            halign='center',
            valign='middle',
            size_hint=(1, 0.3),
            color=APP_COLORS['yellow']
        )
        label.bind(size=label.setter('text_size'))  # For text wrapping
        layout.add_widget(label)

        # Add buttons
        buttons_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)

        restart_button = Button(
            text="Retourner au menu",
            size_hint=(0.5, 1),
            on_release=self.show_menu
        )
        quit_button = Button(
            text="Quitter",
            size_hint=(0.5, 1),
            on_release=self.on_quit
        )

        buttons_layout.add_widget(restart_button)
        buttons_layout.add_widget(quit_button)

        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def show_menu(self, instance):
        """
        Retourne à l'écran du menu principal.

        Paramètres :
            instance (Button) : Bouton déclenchant l'action.
        """
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'  # Retourne à l'écran du menu principal

    def on_quit(self, instance):
        """
        Ferme l'application.

        Paramètres :
            instance (Button) : Bouton déclenchant l'action.
        """
        App.get_running_app().stop()


class SudokuApp(App):
    """
    Application principale pour le jeu Sudoku.

    Méthodes :
        build() : Initialise l'application et configure les écrans.
    """
    def build(self):
        self.icon = "./Assets/logo.png"
        self.title = 'Sudokube -- Pablo et Ezé'
        sm = ScreenManager()  # Gestionnaire des écrans
        sm.add_widget(MenuScreen(name='menu'))  # Ajout de l'écran du menu
        sm.add_widget(GameScreen(self, name='game'))  # Ajout de l'écran de jeu
        sm.add_widget(RuleScreen(name='rules'))
        sm.add_widget(WinScreen(name='win'))
        sm.current = 'menu'  # Écran initial défini sur le menu principal
        return sm


if __name__ == "__main__":
    SudokuApp().run()
