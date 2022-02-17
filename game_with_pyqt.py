from PyQt5 import QtWidgets as qw 			#модуль для создания объектов 
from PyQt5.QtGui import QPixmap				#класс для создания изображений
from PyQt5.QtCore import Qt 				#класс для позиционирования текста внутри виджетов
from PyQt5.QtWidgets import QMessageBox 		#класс для создания всплывающих окон (использую для отображения ошибок)
from PyQt5.QtGui import QIcon 				#класс для вставки изображения в виде иконки для приложения
from PyQt5.QtGui import QFont
import sys									#модуль для корректной работы окна
import random
from time import sleep
from math import ceil
import csv

app_version = "1.3"

#Возникшие трудности:
#~Карточку необходимо размещать в специальном поле Frame, с который раньше не сталкивался, однако показалось удобным (СДЕЛАНО)
#~Шрифт новый (из интернета) установить пока не получилось (уже не планируется) (СДЕЛАНО)
#~Размещать все элементы на этапе заполнения карточки решил с помощью grid'ов, чтобы адаптировать под разные пропорции,
#	этого раньше не умел и найти разборов не удалось (их попросту не имелось). Проблему решил с помощью QtDesigner, в котором
#	сначала накидал примерный макет, затем перевёл в .py и разбирался с написанным (ПРОБЛЕМА РЕШЕНА) 
#~Появилась новая проблема: необходимо переписать весь интерфейс, используя grid'ы (убейте меня поскорее), нужна оптимизация (СДЕЛАНО)
#~Чтобы всё было понятно, нужно вынести все действия в логи, которое должно прокручиваться. Ага, да, КАК ЭТО СДЕЛАТЬ?!
#	короче, дело такое, решил за один вечер + автоматически скроллит вниз (теперь все действия отображаются в логах)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ОКНО С ИГРОЙ + ВСЯ МЕХАНИКА~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Window(qw.QWidget):
	def __init__(self):
		super().__init__()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ВЕРХНЕЕ ПОЛЕ С ОТОБРАЖЕНИЕМ ЗДОРОВЬЯ, МАНЫ И ОЧКОВ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		sizePolicy = qw.QSizePolicy(qw.QSizePolicy.Preferred, qw.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		self.setSizePolicy(sizePolicy)

		horizontal_self = qw.QHBoxLayout(self)
		vert_self = qw.QVBoxLayout()					#сам вертикальный grid, в котором будет верхняя панель, карточка и нижние кнопки
		layout_for_bars = qw.QGridLayout() 				#grid для верхней панели


		logs = qw.QFrame(self)							#для логов сделан отдельный фрейм
		logs.setStyleSheet("background-color: #839BA6; border-radius: 40px;")
		logs.setFixedSize(345, 760)						#с фиксированным размером

		vert_layout_for_log = qw.QVBoxLayout(logs)		#вертикальный грид для заголовка + скроллбар
		logs_title = qw.QLabel(logs)					#заголовок (вверху)
		logs_title.setText("It's logs")
		logs_title.setAlignment(Qt.AlignHCenter)
		logs_title.setStyleSheet("border: 2px solid white; border-radius: 10px; font-size: 21px; color: #F8DEC1;")


		self.log_scroll_area = qw.QScrollArea(logs)						#и сам скроллбар
		self.log_scroll_area.setMinimumSize(320, 700)					#ширина которого чуть больше ширины логов
		self.log_scroll_area.verticalScrollBar().setStyleSheet(	"QScrollBar:vertical {width: 20px; border-radius: 10px;}"
																		#задаёт стили самому скроллбару
																"QScrollBar::handle:vertical {border-radius: 10px; background-color: white;}"
																		#задаёт стили полосе прокрутки (которая перемещается)
																"QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical {background: none;}"
																		#убирает фон у подложки для скролла
																"QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {height: 0px;}")
																		#убирает кнопки у скроллбара
		self.log_attack = qw.QLabel(self.log_scroll_area)				#и создаю текстовый лейбл внутри скроллбара
		self.log_attack.setMinimumSize(300, 700)
		self.log_attack.setStyleSheet("font-size: 18px; color: white;")
		self.log_attack.setAlignment(Qt.AlignHCenter)
		self.log_scroll_area.setWidget(self.log_attack)					#и для скроллбара устанавливаю виджет - тот самый лейбл сверху
		
		vert_layout_for_log.addWidget(logs_title, 0, Qt.AlignTop)
		vert_layout_for_log.addWidget(self.log_scroll_area, 1, Qt.AlignBottom)


		self.point_w = qw.QLabel(self)									#поле для отображения очков
		self.point_w.setStyleSheet("font-size: 26px; color: white;")	#стили для этого поля
		self.point_w.setText('0')										#и текст (сначала = 0)
		self.point_w.setMinimumSize(10, 20)
		self.point_w.setAlignment(Qt.AlignHCenter)

		self.xp = qw.QProgressBar(self)									#создаю шкалу для здоровья
		self.xp.setStyleSheet(	"QProgressBar {"						#первоначальные настройки стилей
							"border-radius: 10px;"
							"border: 1px solid black;"
							"color: #dbde70;"
							"font-size: 20px;}"
							"QProgressBar::chunk {"						#настройки заполняющей шкалы
							"background-color: #ac050a;"
							"border-radius: 10px;}")
		self.xp.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)			#располагаю число по центру
		self.xp.setFormat("%p")											#данный формат позволяет не отображать % в конце
		self.xp.setMinimumSize(100, 30)							
		self.xp.setValue(100)											#в самом начале здоровье равно 100 единицам

		self.mana = qw.QProgressBar(self)								#создаю шкалу для маны
		self.mana.setStyleSheet(	"QProgressBar {"						
							"border-radius: 6px;"
							"border: 1px solid black;"
							"color: #dbde70;"
							"font-size: 20px;}" 
							"QProgressBar::chunk {"			
							"background-color: #018ab8;"
							"border-radius: 6px;}")
		self.mana.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)	
		self.mana.setFormat("%p")
		self.xp.setMinimumSize(100, 30)
		self.mana.setValue(100)

		layout_for_bars.addWidget(self.xp, 0, 0, 1, 4)
		layout_for_bars.addWidget(self.point_w, 0, 4, 1, 1)
		layout_for_bars.addWidget(self.mana, 0, 5, 1, 4)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ПОЛЕ ЧУТЬ НИЖЕ С ЗАЩИТОЙ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		style_defense = "font-size: 24px; color: white;"

		fiz_defense_img = qw.QLabel(self)								#поле для физической защиты
		fiz_defense_img.setPixmap(QPixmap(url_fiz_defense))				#открываю
		fiz_defense_img.setAlignment(Qt.AlignCenter)

		player_fiz_defense = qw.QLabel(self)							#кол-во физической защиты (%)
		player_fiz_defense.setText(str(player_fiz_def))					
		player_fiz_defense.setStyleSheet(style_defense)					#устанавливаю стили для текста

		mag_defense_img = qw.QLabel(self)								#поле для магической защиты
		mag_defense_img.setPixmap(QPixmap(url_mag_defense))				#открываю
		mag_defense_img.setAlignment(Qt.AlignCenter)

		player_mag_defense = qw.QLabel(self)							#поле для кол-ва магической защиты (%)
		player_mag_defense.setText(str(player_mag_def))					
		player_mag_defense.setStyleSheet(style_defense)

		damage_fiz_img = qw.QLabel(self)								#поле для изображения меча
		damage_fiz_img.setPixmap(QPixmap(url_fiz_damage))
		damage_fiz_img.setAlignment(Qt.AlignCenter)	

		damage_fiz = qw.QLabel(self)									#поле для физической атаки
		damage_fiz.setText(str(player_fiz_damage))
		damage_fiz.setStyleSheet(style_defense)

		menu_button = qw.QPushButton(self)
		menu_button.setStyleSheet("background-image: url(" + url_menu + ")")
		menu_button.setFixedSize(33, 30)
		menu_button.setFlat(True)
		menu_button.clicked.connect(self.menu_open)

		damage_mag_img = qw.QLabel(self)								#поле для меча
		damage_mag_img.setPixmap(QPixmap(url_mag_damage))
		damage_mag_img.setAlignment(Qt.AlignCenter)

		damage_mag = qw.QLabel(self)									#поле для магической атаки
		damage_mag.setText(str(player_mag_damage))
		damage_mag.setStyleSheet(style_defense)


		layout_for_bars.addWidget(fiz_defense_img, 1, 0, 1, 1)
		layout_for_bars.addWidget(player_fiz_defense, 1, 1, 1, 1)
		layout_for_bars.addWidget(damage_fiz_img, 1, 2, 1, 1)
		layout_for_bars.addWidget(damage_fiz, 1, 3, 1, 1)
		layout_for_bars.addWidget(menu_button, 1, 4, 1, 1)
		layout_for_bars.addWidget(damage_mag_img, 1, 5, 1, 1)
		layout_for_bars.addWidget(damage_mag, 1, 6, 1, 1)
		layout_for_bars.addWidget(mag_defense_img, 1, 7, 1, 1)
		layout_for_bars.addWidget(player_mag_defense, 1, 8, 1, 1)

		vert_self.addLayout(layout_for_bars)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~СОЗДАНИЕ КАРТОЧКИ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		self.card = qw.QFrame(self)								#создаю frame, в котором будут находиться объекты			
		self.card.setStyleSheet("border: 2px solid white; background-color: white; border-radius: 40px;")
		self.card.setFrameShape(qw.QFrame.StyledPanel)			
		self.card.setFrameShadow(qw.QFrame.Raised)
		self.card.setMinimumSize(400, 550)

		self.layout = qw.QVBoxLayout(self.card)					#создаю вертикальный grid 
		self.layout_grid = qw.QGridLayout()						#создаю grid для характеристик персонажей (внизу карточки)

		self.enemy_name = qw.QLabel(self.card)					#создаю обычное поле в карточке
		self.enemy_name.setStyleSheet("font-size: 24px;")
		font = QFont()
		font.setFamily("Segoe Print")
		self.enemy_name.setFont(font)
		self.enemy_name.setAlignment(Qt.AlignHCenter)			#размещаю поле по центру элемента grid'a 
		self.enemy_name.setMinimumSize(300, 40)

		self.enemy_img = qw.QLabel(self.card)
		self.enemy_img.setStyleSheet("padding: 20px;")
		self.enemy_img.setEnabled(True)
		self.enemy_img.setSizePolicy(sizePolicy)
		self.enemy_img.setAlignment(Qt.AlignHCenter)
		self.enemy_img.setMinimumSize(300, 400)

		self.enemy_xp = qw.QProgressBar(self.card)
		self.enemy_xp.setFormat("%v")
		self.enemy_xp.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
		self.enemy_xp.setMinimumSize(200, 30)
		self.enemy_xp.setStyleSheet(	"QProgressBar {"				#первоначальные настройки стилей
										"border-radius: 10px;"
										"border: 1px solid black;"
										"color: #dbde70;"
										"font-size: 20px;}"
										"QProgressBar::chunk {"			#настройки заполняющей шкалы
										"background-color: #ac050a;"
										"border-radius: 10px;}")


		self.enemy_damage = qw.QLabel(self.card)
		self.enemy_damage.setStyleSheet("font-size: 24px;")
		self.enemy_damage.setAlignment(Qt.AlignHCenter)
		self.enemy_damage.setMinimumSize(150, 30)

		self.enemy_magic_defense = qw.QLabel(self.card)
		self.enemy_magic_defense.setStyleSheet("font-size: 20px;")
		self.enemy_magic_defense.setAlignment(Qt.AlignHCenter)
		self.enemy_magic_defense.setMinimumSize(150, 30)

		self.enemy_fiz_defense = qw.QLabel(self.card)
		self.enemy_fiz_defense.setStyleSheet("font-size: 20px;")
		self.enemy_fiz_defense.setAlignment(Qt.AlignHCenter)
		self.enemy_fiz_defense.setMinimumSize(150, 30)

		#устанавливаю всё сверху вниз: сначала имя, затем изображение и только потом хар-ки (которые тоже
		#необходимо добавить в таблицу)

		self.layout.addWidget(self.enemy_name)							#а теперь в вертикальный grid добавляю виджеты
		self.layout.addWidget(self.enemy_img, 0, Qt.AlignHCenter)
		self.layout_grid.addWidget(self.enemy_xp, 0, 1, 1, 1)			#здесь добавляю виджеты в grid снизу (хар-ки)
		self.layout_grid.addWidget(self.enemy_damage, 0, 2, 1, 1)
		self.layout_grid.addWidget(self.enemy_magic_defense, 1, 2, 1, 1, alignment=Qt.AlignVCenter)
		self.layout_grid.addWidget(self.enemy_fiz_defense, 1, 1, 1, 1, alignment=Qt.AlignVCenter)		
		self.layout.addLayout(self.layout_grid)							#и добавляю один грид в другой

		#и добавляю в основной вертикальный grid всего приложения 

		vert_self.addWidget(self.card, 0, Qt.AlignHCenter)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ОПИСАНИЕ КНОПОК СНИЗУ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		buttons_style = [	"QPushButton {"								
							"border-radius: 10px;"
							"border: 1px solid black;"
							"font-size: 14px;"
							"font-weight: 600;"
							"color: black;"
							"background-color: white;}"
							"QPushButton:hover {"
							"background-color: #b3b3b3;}"]

		layout_for_buttons = qw.QGridLayout()

		button_player_hill = qw.QPushButton(self)
		button_player_hill.setText("Выпить зелье лечения")
		button_player_hill.setStyleSheet(buttons_style[0])
		button_player_hill.setMinimumSize(270, 40)
		button_player_hill.clicked.connect(hill)

		button_player_block = qw.QPushButton(self)
		button_player_block.setText("Выставить щит вперёд")
		button_player_block.setStyleSheet(buttons_style[0])
		button_player_block.setMinimumSize(270, 40)
		button_player_block.clicked.connect(block)

		button_player_fiz_damage = qw.QPushButton(self)
		button_player_fiz_damage.setText("Нанести урон мечом")
		button_player_fiz_damage.setStyleSheet(buttons_style[0])
		button_player_fiz_damage.setMinimumSize(270, 40)
		button_player_fiz_damage.clicked.connect(player_fiz_attack)

		button_player_mag_damage = qw.QPushButton(self)
		button_player_mag_damage.setText("Нанести урон магией")
		button_player_mag_damage.setStyleSheet(buttons_style[0])
		button_player_mag_damage.setMinimumSize(270, 40)
		button_player_mag_damage.clicked.connect(player_magic_attack)

		layout_for_buttons.addWidget(button_player_hill, 0, 1, 1, 1)
		layout_for_buttons.addWidget(button_player_block, 0, 2, 1, 1)
		layout_for_buttons.addWidget(button_player_fiz_damage, 1, 1, 1, 1)
		layout_for_buttons.addWidget(button_player_mag_damage, 1, 2, 1, 1)
		
		vert_self.addLayout(layout_for_buttons)

		horizontal_self.addLayout(vert_self)
		horizontal_self.addWidget(logs)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ЗАПОЛНЕНИЕ КАРТОЧКИ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def CreateEnemy(self, name, url, damage, mag_defense, fiz_defense):
		self.enemy_name.setText(name)					#устанавливаю имя противника в карточку
		self.enemy_img.setPixmap(QPixmap(url))			#устанавливаю картинку противника в карточку

		global enemy_xp_d
		self.enemy_xp.setMaximum(Enemy_char[enemy][2]) 	#устанавливаю максимум для шкалы здоровья
		self.enemy_xp.setValue(enemy_xp_d)				#устанавливаю в начале кол-во здоровья, равное максимуму
		self.enemy_xp.setFormat('%v'.format(enemy_xp_d))#устанавливаю хп противника в интовом формате

		self.enemy_damage.setText("Урон: " + str(damage))					#устанавливаю урон противника в карточку
		self.enemy_magic_defense.setText("Маг защ: " + str(mag_defense))	#устанавливаю магическую защиту в карточку
		self.enemy_fiz_defense.setText("Физ защ: " + str(fiz_defense))		#устанавливаю физическую защиту в карточку
		

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ОПИСАНИЕ ИЗМЕНЯЮЩИХСЯ ПЕРЕМЕННЫХ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def player_attack(self):			#функция нанесения физического урона противнику
		global enemy_xp_d, points

		if enemy_xp_d > 0:				
			points += 3												#за нанесения урона начисляются очки 
			self.point_w.setText(str(points))						#отображаю ккол-во очков
			self.enemy_xp.setValue(enemy_xp_d)						#меняю кол-во хп у противника
			self.enemy_xp.setFormat('{0:.2f}'.format(enemy_xp_d))	#и изменяю формат на float с двумя знаками после запятой
			self.enemy_attack()										#и вызываю функцию атаки противника
		else:
			self.died_enemy()										#ф-ия смерти противника

	def player_mag_attack(self):		#ф-ия магической атаки, аналогична физической
		global enemy_xp_d, player_mana, player_xp, points

		if enemy_xp_d > 0:
			points += 3
			self.point_w.setText(str(points))
			self.enemy_xp.setValue(enemy_xp_d)
			self.enemy_xp.setFormat('{0:.2f}'.format(enemy_xp_d))
			self.enemy_attack()
		else:
			self.died_enemy()

		self.mana.setValue(player_mana)

	def hill_xp(self):	
		global player_xp, player_mana
		self.xp.setValue(player_xp)
		self.xp.setFormat('{0:.2f}'.format(player_xp))
		self.mana.setValue(player_mana)

	def mana_regen(self):
		global player_mana, player_xp
		self.mana.setValue(player_mana)
		self.xp.setValue(player_xp)
		self.xp.setFormat('{0:.2f}'.format(player_xp))
		if player_xp <= 0:
			player_xp = 0
			self.log_update("Оу, кажется, мы проиграли")
			self.xp.setValue(player_xp)
			self.xp.setFormat("%p")
			game_over()

	def enemy_attack(self):
		global player_xp, Enemy_char, player_fiz_def, enemy

		player_damage = (Enemy_char[enemy][3] + Enemy_char[enemy][3]*random.uniform(-0.20, 0.20)) * (1 - player_fiz_def/100)
		player_xp -= player_damage
		self.log_update("Нам нанесли: " + str(round(player_damage, 2)))
		self.xp.setValue(player_xp)
		self.xp.setFormat('{0:.2f}'.format(player_xp))
		if player_xp <= 0:
			player_xp = 0
			self.log_update("Оу, кажется, мы проиграли")
			self.xp.setValue(player_xp)
			self.xp.setFormat("%p")
			game_over()

	def restart_game_win(self):
		global player_mana, player_xp, points, enemy_xp_d
		self.mana.setValue(player_mana)
		self.xp.setValue(player_xp)
		self.xp.setFormat("%p")
		self.point_w.setText(str(points))
		self.enemy_xp.setValue(enemy_xp_d)

	def died_enemy(self):
		global points, player_xp, player_mana
		points += 7
		self.point_w.setText(str(points))
		self.enemy_xp.setValue(0)
		self.enemy_xp.setFormat("%v")
		print("Ho-ho, enemy is died")
		player_xp = player_xp + 12 if (player_xp + 12 < 100) else 100
		player_mana = player_mana + 14 if (player_mana + 14 < 100) else 100 
		self.mana.setValue(player_mana)
		self.xp.setValue(player_xp)
		self.xp.setFormat('{0:.2f}'.format(player_xp))
		sleep(1)
		create_enemy()


	def log_update(self, text):		#ф-ия, которая добавляет текст в логи (плюс увеличивает размер лэйбла)
		if text == "restart":	
			self.log_attack.setText("")
			self.log_attack.adjustSize()
		else:
			self.log_attack.setText(self.log_attack.text() + "\n" + text)
			self.log_attack.adjustSize()
			self.log_scroll_area.verticalScrollBar().setValue(self.log_scroll_area.verticalScrollBar().maximum())
									#эту магическую строчку лучше не трогать - она устанавливает скролл на свой максимум
									#(автоматически скроллит вниз) 

	def menu_open(self):												#ф-ия открытия основного меню
		menu.stacked_widget.setCurrentIndex(0)							#переключаю виджеты
		menu.setStyleSheet("QMainWindow {background-image: url("+ url_menu_background +");}")
		menu.setFixedSize(560, 440)									#и устанавливаю иной размер (т.к. меньше, чем игра)
		qr = menu.frameGeometry()										#узнаёт размеры менюшки 
		qr.moveCenter(qw.QDesktopWidget().availableGeometry().center())	#находит центр экрана
		menu.move(qr.topLeft())											#и перемещает верхний левый край менюшки в центр 


player_fiz_def = 31		#пока постоянная 	(физическая защита %)
player_mag_def = 46		#пока постоянная 	(магическая защита %)
player_fiz_damage = 23	#пока постоянная 	(физический урон)
player_mag_damage = 18	#пока постоянная 	(магический урон)
player_mana = 100		#изменяется			(мана)
player_xp = 100			#изменяется			(хит-поинты)
points = 0				#изменяется			(очки)
enemy_xp_d = 0			#изменяется			(хп противника)
enemy = 0				#изменяется			(номер противника в массиве)

url_mag_defense = "./png_for_game/blue.png"				#путь к картинке с магическим щитом
url_fiz_defense = "./png_for_game/white.png"			#путь к картинке с физическим щитом
url_mag_damage = "./png_for_game/blue_armor.png"
url_fiz_damage = "./png_for_game/white_armor.jpg"
url_backround = "./png_for_game/forest_3.jpg"			#путь к картинке с задним фоном
url_menu = "./png_for_game/m_menu.png"
url_window_icon = "./png_for_game/icon.jpg"
url_menu_background = "./png_for_game/back.png"

#массив характеристик противников
Enemy_char = [	["Орк-повар", "./png_for_game/ork_1.png", 48, 10, 23, 64],			#xp, damage, mag, fiz
				["Орк-воин", "./png_for_game/ork_3.jpg", 54, 12, 24, 68],
				["Малый орк-воин", "./png_for_game/ork_4.jpg", 42, 9, 18, 54],
				["Гоблин-менеджер", "./png_for_game/goblin_1.png", 32, 7, 36, 18],
				["Гоблин-вор", "./png_for_game/goblin_2.jpg", 29, 9, 64, 48],
				["Гоблин-дохлик", "./png_for_game/goblin_4.jpg", 13, 3, 32, 29],
				["Гоблин-алхимик", "./png_for_game/goblin_3.jpg", 36, 32, 89, 12],
				["Орк-воин (БОСС)", "./png_for_game/ork_2.png", 70, 18, 64, 86]]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ОПИСАНИЕ ДЕЙСТВИЙ ИГРОКА~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_enemy():							#функция, которая настраивает карточку
	global enemy_xp_d, enemy, points		
	if points > 100:						#два противника получились уж слишком сложные, поэтому появиться они могут не сразу
		enemy = random.randint(0, 7)
	elif points > 60:
		enemy = random.randint(0, 6)
	else:
		enemy = random.randint(0, 5)
	enemy_xp_d = Enemy_char[enemy][2]		#и здоровье противника изменяю на максимум для данного
	window.CreateEnemy(Enemy_char[enemy][0], Enemy_char[enemy][1], Enemy_char[enemy][3], Enemy_char[enemy][4], Enemy_char[enemy][5])
	
def player_fiz_attack():					#функция, описывабщая нанесение физического урона по противнику
	global player_fiz_damage, enemy_xp_d
	enemy_damage = (player_fiz_damage + player_fiz_damage*random.uniform(-0.20, 0.20)) * (1 - Enemy_char[0][5]/100)
	enemy_xp_d -= enemy_damage
											#добавил элемент рандома, теперь урон будет +- 20% от заданного
	window.log_update("Нанесён урон противнику: " + str(round(enemy_damage, 2)))
	window.player_attack()					#вызывается функция изменения количества хп на окне

def player_magic_attack():					#функция, которая описывает нанесение магического урона по противнику
	global player_mag_damage, enemy_xp_d, player_mana, enemy
	player_cost_mag = 20					#цена заклинания 
	if player_mana >= player_cost_mag:
		enemy_damage = (player_mag_damage + player_mag_damage*random.uniform(-0.20, 0.20)) * (1 - Enemy_char[enemy][4]/100)
		enemy_xp_d -= enemy_damage
											#добавил элемент рандома, теперь урон будет +- 20% от заданного

		player_mana -= player_cost_mag 		#уменьшается мана
		window.log_update("Прошёл урон магией\nпо противнику: " + str(round(enemy_damage, 2)))
		window.player_mag_attack() 			#и вызываются функции изменения текста в окне
	else:
		window.log_update("Куда всю ману слил?\nНужно больше 20")

def hill():									#функция применения лечащего заклинания
	global player_xp, player_mana
	player_hill = 15						#кол-во восстанавливаемого здоровья
	hill_cost = 10							#и цена заклинания
	if player_mana >= hill_cost: 			#если достаточно маны для применения
		if player_xp == 100:
			window.log_update("И кого ты лечить собрался?")
		elif player_xp + player_hill < 100: 	#если, конечно, есть куда увеличивать
			player_xp += player_hill
			player_mana -= hill_cost			#то уменьшаю количество здоровья
			window.log_update("+" + str(player_hill) + " к хп")
			window.hill_xp()					#функция изменения хп в окне
			window.enemy_attack()
		else:
			player_xp = 100	
			player_mana -= hill_cost			#то уменьшаю количество здоровья
			window.log_update("+" + str(player_hill) + " к хп")
			window.hill_xp()					#функция изменения хп в окне
			window.enemy_attack()
		sleep(0.1)							#немного задержки, чтобы игрок видел, что происходит лечение, а только затем наносится урон				
	else:
		window.log_update("Куда всю ману слил?\nНужно больше 10")

def block():								#функция блокирования части урона и восстановления маны
	global player_mana, player_xp, enemy 	
	mana_regen = 15							#количество регенерации маны
	player_damage = (Enemy_char[enemy][3] + Enemy_char[enemy][3]*random.uniform(-0.20, 0.20)) * (1 - (player_fiz_def + 30)/100)
	player_xp -= player_damage
	if player_mana + mana_regen > 100: 		#мана регенится только в том случае, если её меньше 100
		player_mana = 100 					
	else:
		player_mana += mana_regen 
	window.log_update("Нам нанесли: " + str(round(player_damage, 2)))			
	window.mana_regen()

def restart_game():							#ф-ия выставления стартовых параметров после проигрыша
	global player_mana, player_xp, points, enemy_xp_d
	player_mana = 100
	player_xp = 100
	points = 0
	enemy_xp_d = 0
	window.log_update("restart")
	window.restart_game_win()
	create_enemy()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ДИАЛОГОВОЕ ОКНО ДЛЯ ЗАПИСИ В ТАБЛИЦУ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class game_over(qw.QDialog):							#функция отображения сообщения с проигрышем
	def __init__(self):
		super().__init__()
		global points, window
		self.setWindowTitle("Конец игры")
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)	#убирает вопросительный знак рядом с крестиком
		self.setFixedSize(500, 220)

		vert_layout = qw.QVBoxLayout(self)

		text = qw.QLabel(self)
		text.setText("Вы набрали " + str(points) + " очков! Поздравляю!\nЖелаете внести своё имя в историю?")
		text.setAlignment(Qt.AlignHCenter)
		text.setStyleSheet("font-size: 24px; font-weight: 600;")

		self.text_error = qw.QLabel(self)
		self.text_error.setAlignment(Qt.AlignHCenter)

		name = qw.QLineEdit(self)
		name.setMinimumSize(300, 40)
		name.setMaxLength(20)
		name.setStyleSheet("border-radius: 5px; border: 1px solid black; font-size: 20px;")
		name.setAlignment(Qt.AlignHCenter)

		hor_layout = qw.QHBoxLayout()

		buttons_style = '''	QPushButton {								
								border-radius: 10px;
								border: 1px solid black;
								font-size: 14px;
								font-weight: 600;
								color: black;
								background-color: white;}
								QPushButton:hover {
								background-color: #b3b3b3;}'''

		button_ok = qw.QPushButton(self)
		button_ok.setText("Ок")
		button_ok.setFixedSize(140, 40)
		button_ok.setStyleSheet(buttons_style)
		button_ok.clicked.connect(lambda: [self.input_in_table(name.text()), restart_game(), self.close()] if (name.text() != "") else [self.text_error.setText("Пожалуйста, введите имя"), self.text_error.setStyleSheet("font-size: 20px; font-weight: 450;")])

		button_table = qw.QPushButton(self)
		button_table.setText("Таблица лидеров")
		button_table.setFixedSize(140, 40)
		button_table.setStyleSheet(buttons_style)

		button_cancel = qw.QPushButton(self)
		button_cancel.setText("Нет")
		button_cancel.setFixedSize(140, 40)
		button_cancel.setStyleSheet(buttons_style)
		button_cancel.clicked.connect(lambda: [self.close(), restart_game()])

		hor_layout.addWidget(button_ok)
		hor_layout.addWidget(button_table)
		hor_layout.addWidget(button_cancel)

		vert_layout.addWidget(text, 0, Qt.AlignHCenter)
		vert_layout.addWidget(self.text_error, 0, Qt.AlignHCenter)
		vert_layout.addWidget(name, 0, Qt.AlignHCenter)
		vert_layout.addLayout(hor_layout)

		self.show()

	def input_in_table(self, name):		#функция внесения данных в таблицу лидеров
		flag = 0
		with open("table.csv", "r") as file:				#сначала открываю csv файл и читаю его в словарь
			reader = csv.reader(file, delimiter=";")
			table = {row[0]:int(row[1]) for row in reader}	#компактная запись таблицы в словарь

			name_mass = []			#массив под имена
			point_mass = []			#массив под очки

			for line in table:								#переношу словарь в массив
				name_mass.append(line)						
				point_mass.append(table[line])

			place = 0

			for i in range(len(point_mass)):				#и ищу место, куда вставить нашего "героя"
				if (points > point_mass[i]) and (flag == 0):
					point_mass.insert(i, points)
					name_mass.insert(i, name)
					place = i + 1
					flag = 1
					break
			if flag == 0:									#ну а если вставить некуда, то только в конец
				point_mass.append(points)
				name_mass.append(name)

		try:																#дальше записываю два новых массива в таблицу
			if points == 0: 													
				self.text_error.setText("Фи, даже записывать не буду, зелёный!")		#если 0 очков набрано, то не судьба
				self.text_error.setStyleSheet("font-size: 20px; font-weight: 450;")
			else:
				self.text_error.setText("Поздравляю, ты оказался на " + str(place) + " месте!")
				self.text_error.setStyleSheet("font-size: 20px; font-weight: 450;")
				with open("table.csv", "w", newline="") as file:
					writer = csv.writer(file, delimiter=";")

					for i in range (len(name_mass)):
						writer.writerow([name_mass[i], point_mass[i]])
		except PermissionError:												#если открыта таблица в момент записи
				self.text_error.setText("Не трожь руками таблицу, сука!")
				self.text_error.setStyleSheet("font-size: 20px; font-weight: 450;")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ОПИСАНИЕ ТАБЛИЦЫ ЛИДЕРОВ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Table(qw.QWidget):
	def __init__(self):
		global window
		super().__init__()
		main_layout = qw.QVBoxLayout(self)

		horiz_top = qw.QHBoxLayout()

		menu_button = qw.QPushButton(self)
		menu_button.setStyleSheet("background-image: url(" + url_menu + ");")
		menu_button.setFixedSize(33, 30)
		menu_button.setFlat(True)
		menu_button.clicked.connect(window.menu_open)

		menu_button_1 = qw.QPushButton(self)
		menu_button_1.setStyleSheet("background-image: url(" + url_menu + ");")
		menu_button_1.setFixedSize(33, 30)
		menu_button_1.setFlat(True)
		menu_button_1.clicked.connect(window.menu_open)

		name_of_page = qw.QLabel(self)
		name_of_page.setText("Смельчаки, достойные огласки")
		font = QFont()
		font.setFamily("Segoe Print")
		name_of_page.setFont(font)
		name_of_page.setStyleSheet("font-size: 24px; font-weight: 900;")
		name_of_page.setAlignment(Qt.AlignHCenter)

		horiz_top.addWidget(menu_button, 0, Qt.AlignLeft)
		horiz_top.addWidget(name_of_page, 0, Qt. AlignHCenter)
		horiz_top.addWidget(menu_button_1, 0, Qt.AlignRight)

		self.table_of_lids = qw.QTableWidget(self)
		self.table_of_lids.setFixedSize(280, 402)
		self.table_of_lids.setColumnCount(2)
		self.table_of_lids.setHorizontalHeaderLabels(["Имя", "Очки"])
		self.table_open()

		main_layout.addLayout(horiz_top)
		main_layout.addWidget(self.table_of_lids, 0, Qt.AlignHCenter)

	def table_open(self):
		with open("table.csv", "r") as file:
			reader = csv.reader(file, delimiter=";")

			table = {row[0]:int(row[1]) for row in reader}

			name_mass = []			#массив под имена
			point_mass = []			#массив под очки

			for line in table:								#переношу словарь в массив
				name_mass.append(line)						
				point_mass.append(table[line])

		if len(point_mass) <= 10:
			self.table_of_lids.setRowCount(len(point_mass))
			self.table_of_lids.setFixedSize(271, 45*len(point_mass))
			for i in range(len(point_mass)):
				self.table_of_lids.setItem(i, 0, qw.QTableWidgetItem(name_mass[i]))
				self.table_of_lids.setItem(i, 1, qw.QTableWidgetItem(str(point_mass[i])))
		else:
			self.table_of_lids.setRowCount(10)
			for i in range(10):
				self.table_of_lids.setItem(i, 0, qw.QTableWidgetItem(name_mass[i]))
				self.table_of_lids.setItem(i, 1, qw.QTableWidgetItem(point_mass[i]))




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ГЛАВНОЕ МЕНЮ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Menu(qw.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("РПГшечка")
		self.setWindowIcon(QIcon(url_window_icon))
		self.setStyleSheet("QMainWindow {background-image: url(./png_for_game/back.png);}")
		sizePolicy = qw.QSizePolicy(qw.QSizePolicy.Preferred, qw.QSizePolicy.Preferred)	#необходимо для растягивания окна
		sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		self.setSizePolicy(sizePolicy)													#устанавливается политика размера окна
		self.setFixedSize(560, 440)

		self.stacked_widget = qw.QStackedWidget(self)				#создаю виджет с виджетами (стакер)

		main_menu = qw.QWidget()									#виджет основного меню
		main_vert_layout = qw.QVBoxLayout(main_menu)				#вертикальный грид для кнопок

		app_name = qw.QLabel(main_menu)
		app_name.setText("РПГшечка")
		font = QFont()
		font.setFamily("Segoe Print")
		app_name.setFont(font)
		app_name.setStyleSheet("font-size: 24px; font-weight: 900;")
		app_name.setFixedHeight(170)
		app_name.setAlignment(Qt.AlignHCenter|Qt.AlignBottom)

		buttons_style = ''' QPushButton {	
							border-radius: 10px;
							border: 1px solid black;
							font-size: 14px;
							font-weight: 600;
							color: black;
							background-color: white;}
							QPushButton:hover {
							background-color: #b3b3b3;}
		'''

		button_1 = qw.QPushButton(main_menu)
		button_1.setText("ИГРАТЬ!")
		button_1.setStyleSheet(buttons_style)
		button_1.setFixedSize(350, 40)
		button_1.clicked.connect(self.game_open)
															#при нажатии на кнопку, запускается игра, в стакер добавляется виджет
															#с игрой и переключается окно на главное меню
		button_2 = qw.QPushButton(main_menu)
		button_2.setText("Таблица лидеров")
		button_2.setStyleSheet(buttons_style)
		button_2.setFixedSize(350, 40)
		button_2.clicked.connect(self.create_table)

		button_3 = qw.QPushButton(main_menu)
		button_3.setText("Магазин")
		button_3.setStyleSheet(buttons_style)
		button_3.setFixedSize(350, 40)

		button_4 = qw.QPushButton(main_menu)
		button_4.setText("Выйти из игры")
		button_4.setStyleSheet(buttons_style)
		button_4.setFixedSize(350, 40)
		button_4.clicked.connect(lambda: sys.exit())

		horizontal_bottom = qw.QHBoxLayout()
		autor = qw.QLabel(main_menu)
		autor.setText("Автор: Антоха")

		version = qw.QLabel(main_menu)
		version.setText("version: " + app_version)

		horizontal_bottom.addWidget(autor, 0 , Qt.AlignLeft|Qt.AlignBottom)
		horizontal_bottom.addWidget(version, 0 , Qt.AlignRight|Qt.AlignBottom)

		main_vert_layout.addWidget(app_name)
		main_vert_layout.addWidget(button_1, 0, Qt.AlignHCenter)
		main_vert_layout.addWidget(button_2, 0, Qt.AlignHCenter)
		main_vert_layout.addWidget(button_3, 0, Qt.AlignHCenter)
		main_vert_layout.addWidget(button_4, 0, Qt.AlignHCenter)
		main_vert_layout.addLayout(horizontal_bottom)

		self.stacked_widget.addWidget(main_menu)
		self.stacked_widget.addWidget(window)
		self.stacked_widget.addWidget(table)
		self.stacked_widget.setCurrentIndex(0)

		self.setCentralWidget(self.stacked_widget)

	def game_open(self):
		self.setStyleSheet("QMainWindow {background-image: url("+ url_backround +");}")
		restart_game()
		self.stacked_widget.setCurrentIndex(1)
		self.setMinimumSize(1000, 800)
		qr = self.frameGeometry()
		cp = qw.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def create_table(self):
		self.setStyleSheet("QMainWindow {background-color: white;}")
		self.setFixedSize(560, 500)
		self.stacked_widget.setCurrentIndex(2)
		table.table_open()
		qr = self.frameGeometry()
		cp = qw.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())



def app():
	global menu, window, table
	application = qw.QApplication (sys.argv)				#инициализация pyqt	
	window = Window()
	table = Table()
	menu = Menu()											#создание прототипа класса окна
	menu.show()												#показ созданного окна
	sys.exit(application.exec_())							#без этой строчки окно закрывается сразу же

if __name__ == "__main__":
	app()
