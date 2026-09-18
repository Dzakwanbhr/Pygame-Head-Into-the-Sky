#library yg digunakan
import pygame
import random
import os

#initialization pygame
pygame.init()

#ukuran game window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#pembuatan output screen, dan judul display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Head Into The Clouds!")

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#load music dan sound
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0) #-1 untuk looping ketika musik habis, 0.0 adalah mulai musik dari detik 0.0
jump_fx = pygame.mixer.Sound('assets/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('assets/death.mp3')
death_fx.set_volume(0.5)

#game variable
SCROLL_THRESH = 200 #batas ketika player menyentuh batas ini, maka bg akan scroll naik
GRAVITY = 1 # kecepatan gravitasi atau kecepatan jatuh player
MAX_PLATFORMS = 10 #jumlah maximum platform yg dibuat per waktu
scroll = 0 #variable akan berubah didalam game setiap waktunya, untuk tau seberapa jauh scrolling bg
bg_scroll = 0 #variable scroll bg dimulai dari 0
game_over = False #kondisi game masih belum selesai
score = 0
fade_counter = 0 #variable awal animasi fade in
if os.path.exists('score.txt'): #jika file score.txt ada maka;
    with open('score.txt', 'r') as file: #buka file score.txt
        high_score = int(file.read()) #nominal integer pada file score.txt
else:
    high_score = 0 #jika tidak nilai akan 0

#define colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (133, 66, 111)

#variable font yg digunakan
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 25)

#gambar yang digunakan pada game
jumpy_image = pygame.image.load('assets/jumpy.png').convert_alpha() #untuk icon load  gambar player
bg_image = pygame.image.load('assets/bg.png').convert_alpha() #untuk load gambar background
platform_image = pygame.image.load('assets/platform.png').convert_alpha() #untuk load gambar platform

#fungsi output text ke screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col) #mengubah text menjadi gambar
    screen.blit(img, (x, y)) #text yg telah diubah menjadi gambar akan muncul dengan koordinat x,y yg ditentukan


#function untuk panel info skor
def draw_panel():
    pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, WHITE, (0,30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

#function for drawing the background
def draw_bg(bg_scroll):
	screen.blit(bg_image, (0, 0 + bg_scroll)) #scrolling bg dimulai dari titik koordinat 0,0
	screen.blit(bg_image, (0, -600 + bg_scroll)) #scroll bg dimulai dari 0, dan gambar yg dimuat sampai 600 pixel

#player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (45,65)) #settingan ukuran gambar player pada aplikasi
        self.width = 30 # lebar kotak
        self.height = 55 # tinggi kotak
        self.rect = pygame.Rect(0, 0, self.width, self.height) #lebar dan tinggi kotak yang menyatu dengan gambar player
        self.rect.center = (x,y) #posisi muncul pertama kali kotak
        self.vel_y = 0 #vel = velocity, kecepatan gerak ke atas dan ke bawah (y)
        self.flip = False

    def move(self):
        #reset variable
        scroll = 0
        dx = 0
        dy = 0

        #process keypresses
        key = pygame.key.get_pressed() #trigger tombol keyboard untuk move
        if key[pygame.K_a]: #tombol "A" akan menggerakan player ke kiri
            dx = -10 #kecepatan move player ke kiri
            self.flip = True #flip gambar player agar menghadap kiri
        if key[pygame.K_d]: #tombol "D" akan menggerakan player ke kanan
            dx = 10 #kecepatan move player ke kanan
            self.flip = False #gambar tidak akan flip jika move ke kanan
        if key[pygame.K_LEFT]: #tombol "A" akan menggerakan player ke kiri
            dx = -10 #kecepatan move player ke kiri
            self.flip = True #flip gambar player agar menghadap kiri
        if key[pygame.K_RIGHT]: #tombol "D" akan menggerakan player ke kanan
            dx = 10 #kecepatan move player ke kanan
            self.flip = False #gambar tidak akan flip jika move ke kanan

        #gravity
        self.vel_y += GRAVITY #kecepatan jatuh player setelah loncat
        dy += self.vel_y #artinya ketinggian loncat ditambah dengan nilai dy

        #biar ga off screen ketika gerak
        if self.rect.left + dx < 0: 
            dx =  0 - self.rect.left #nilai max sisi kiri kotak player (x) tidak akan melewati dari 0 display lebar layar
        if self.rect.right + dx > SCREEN_WIDTH: 
            dx = SCREEN_WIDTH - self.rect.right #nilai max sisi kanan kotak player (x) tidak akan melewati dari lebar layar atau 400

        #check collision with platforms
        for platform in platform_group:
            #ketika 2 rectangle bertemu (rec. player dan platform)
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): #ketika rectangle platform dan player telah bersinggungan
                #check if above the platform
                if self.rect.bottom < platform.rect.centery: # lebih kecil karena nilai keatas semakin negatif, jadi artinya ialah jika bagian bawah rect. player sudah diatas rect. platform
                    if self.vel_y > 0: #jika velocity/kecepatan sudah menjadi 0
                        self.rect.bottom = platform.rect.top # maka rect player bagian bawah dan rect platform bagian atas akan beradu
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()
            
        #cek jika player sudah diatas layar
        if self.rect.top <= SCROLL_THRESH: #jika rect bagian atas player sudah lebih kecil sama dengan batas scroll layar
            #if player is jumping
            if self.vel_y < 0: #ketika kecepatan loncat sudah kembali 0, 
                scroll = -dy #maka scroll bg dimulai
            
        
        #update rectangle position
        self.rect.x += dx #trigger agar fungsi gerak kiri kanan bisa digunakan
        self.rect.y += dy + scroll #trigger agar fungsi gerak keatas bisa digunakan

        return scroll

    def draw(self):
        screen.blit((pygame.transform.flip(self.image, self.flip, False)), (self.rect.x - 8 , self.rect.y - 3)) #memanggil fungsi agar muncul dilayar dan gambar berbalik jika loncat ke lawan posisi

#Platform class
class Platform(pygame.sprite.Sprite): #sprite menggunakan class untuk menampilkan gambar platform
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self) # untuk menampilkan gambar platform
        self.image = pygame.transform.scale(platform_image, (width, 21)) #ukuran platform dalam game
        self.moving = moving #untuk platform bergerak
        self.move_counter = random.randint(0, 15) #bergerak antara 0 - 15 pixel
        self.direction = random.choice([-1, 1]) #bergerak ke arah kiri atau kanan
        self.speed = random.randint(1, 2) #kecepatan platform bergerak antara 1 - 2
        self.rect = self.image.get_rect() #kotak dibuat untuk permukaan gambar
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        #platform bergerak kekiri kanan bila dia sebuah platform bergerak
        if self.moving == True: #kondisi akan true
            self.move_counter += 1 #platform akan bergerak
            self.rect.x += self.direction * self.speed #arah gerak dikalikan kecepatan gerak platform

        # ubah arah gerak platform jika sudah bergeser ke titik maximum layar
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1 #jika value positif akan menjadi negatif, dan sebaliknya, krn dikalikan 1, maka arah akan berubah
            self.move_counter = 0 #lalu dikembalikan ke 0

        #update vertical position
        self.rect.y += scroll

        #check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT: #jika rectangle sudah melewati ketinggian layar,
            self.kill() #maka hapus platform

#player setting
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150) #spawn pertama kali player

#create sprite group
platform_group = pygame.sprite.Group() #untuk menggrouping sprites

#create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

#main game loop
run = True #agar layar tetap muncul sampai kita menekan tombol close
while run:

    clock.tick(FPS) #trigger variable fps diatas

    if game_over == False:
        scroll = jumpy.move() #berfungsi agar player bisa bergerak, dan bg scrolling

        #draw background
        bg_scroll += scroll
        if bg_scroll >= 600: #jika gambar display sebesar 600 pixel telah habis,
            bg_scroll = 0 #maka gambar bg akan mulai update, dari 0 pixel
        draw_bg(bg_scroll) #command eksekusi scrolling bg

        #generate platforms
        if len(platform_group) < MAX_PLATFORMS: 
            p_w = random.randint(40, 80) #lebar platform yg dibuar
            p_x = random.randint(0, SCREEN_WIDTH - p_w) #maximum lebar munculnya platform
            p_y = platform.rect.y - random.randint(80, 120) #maximum ketinggian muncul platform
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 2000:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving) #eksekusi variabel diatas
            platform_group.add(platform) #mengrouping platform yg dibuat
        
        
        #update platforms
        platform_group.update(scroll) # mengeksekusi agar group platform yg telah di update muncul

        #update score
        if scroll > 0:
            score += scroll

        #buat garis di display dengan high score sebelumnya
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3) #garis yg muncul di batas high score yg dicapai sblmnya
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH) #highscore paling besar yg dibuat sebelumnya akan muncul dalam game
        #draw sprites
        platform_group.draw(screen) #platform digambar pada layar
        jumpy.draw() #memanggil gambar player

        #draw panel
        draw_panel() #panel skor yg running di pojok kiri atas

        #check game over
        if jumpy.rect.top > SCREEN_HEIGHT: #ketika player jatuh &keluar screen maka,
            game_over = True #game akan selesai
            death_fx.play()
    else:
        #black screen akan menutupi display
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 11 #kecepatan fade in
            pygame.draw.rect(screen, BLACK, (0, 0, fade_counter, SCREEN_HEIGHT)) #konfigurasi black screen
        else:
            #teks akan keluar dengan format kalimat, ukuran font, warna font, dan koordinat x,y
            draw_text('GAME OVER!', font_big, WHITE, 130, 200) 
            draw_text("SCORE: " + str(score), font_big, WHITE, 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 33, 300)
            #update high score
            if score > high_score: #jika score lebih besar dari high score yg telah ada maka;
                high_score = score #replace dengan nominal highscore tertinggi yg baru dibuat;
                with open('score.txt', 'w') as file: #dengan menuliskannya pada score.txt
                    file.write(str(high_score))
            key = pygame.key.get_pressed()   
            if key[pygame.K_SPACE]: #jiks tombol spacebar di klik maka akan terjadi command yg dibawah ini
                #reset variables
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                #reposisi player
                jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                #reset platforms
                platform_group.empty()
                #starting platform
                platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
                platform_group.add(platform)


    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #dimaksudkan jika kita mengklik close maka program akan stop,
            #update high score
            if score > high_score:
                high_score =score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score)) #fungsi disini juga dibuat agar setelah apk di close high score tidak akan reset
            run = False # dan running menjadi false yg artinya program akan berhenti

    #update display window
    pygame.display.update() # memunculkan semua gambar untuk ditampilkan
    
pygame.quit() #keluar aplikasi, dibutuhkan command diatas untuk close aplikasi