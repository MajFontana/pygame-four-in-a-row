import pygame
import time
import random
import math

##### UI SETTINGS #####
W_SIZE = [800, 800]
BOARD_COLOR = [6, 78, 122]
BG_COLOR = [20, 133, 204]
FPS = 29
MIN_BANNER = 0.05
OFFSET = 0.25
HOLE_SIZE = 0.9
#FONT = "monospace"
TXT_SIZE = 0.075
TXT_COLOR = [240, 240, 240]
MAXDIM = 150
TXT_TIME = 3
DESPAWN_TIME = 1
TXT_SPEED = 3.5

##### GAME SETTINGS #####
FIELD_SIZE = [7, 6]
GOAL = 4
GRAVITY = 50
PLAYERS = [[[196, 20, 20], "Red", 0], [[247, 244, 25], "Yellow", 0]]

##### FUNCTIONS #####
def render_still():
    for pos in grid:
        cont = grid[pos]
        if not cont[1] == None:
            screen.blit(tokens[cont[1]], cont[0])

def render_loose():
    global count
    global falling
    tpos = None
    if type(falling) == type(list()):
        fallen = int(round((time.time() - falling[0]) ** 2 * gravity / 2))
        if not "popout" in falling:
            tpos = [xsnaps[falling[2]], fallen - r]
            slot = grid[(falling[2], falling[1])]
            if tpos[1] >= slot[0][1]:
                tpos[1] = slot[0][1]
                grid[(falling[2], falling[1])][1] = cplayer
                count += 1
                update_game([falling[2], falling[1]])
                falling = "popout"
        else:
            tpos = [xsnaps[falling[2]], fallen - int(round(tokensize))]
            if tpos[1] >= -r:
                tpos[1] = -r
                falling = False
    elif type(falling) == type(int()):
        falling = [time.time(), falling, xslot]
    elif falling == "popout":
        falling = [time.time(), None, xslot, "popout"]
        tpos = [xsnaps[xslot], -int(round(tokensize))]
    if not tpos:
        tpos = [xsnaps[xslot], -r]
    screen.blit(tokens[cplayer], tpos)

def render_main():
    screen.blit(board, bpos)

def flip_events():
    global run
    global count
    global falling
    global xslot
    mpos = pygame.mouse.get_pos()
    xslot = min(FIELD_SIZE[0] - 1, max(0, int((mpos[0] - (bpos[0] + offset / 2)) / (tokensize + offset))))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if falling == False:
                    dest = None
                    for y in range(FIELD_SIZE[1]):
                        if grid[(xslot, y)][1] == None:
                            dest = y
                            break
                    if not dest == None:
                        falling = y

def update_game(pos):
    global gameover
    wcheck = range(max(0, pos[0] - (GOAL - 1)), min(FIELD_SIZE[0], pos[0] + GOAL))
    hcheck = range(max(0, pos[1] - (GOAL - 1)), min(FIELD_SIZE[1], pos[1] + GOAL))
    drurange = range(max(min(wcheck) - pos[0], min(hcheck) - pos[1]), min(max(wcheck) - pos[0], max(hcheck) - pos[1]) + 1)
    drdrange = range(max(min(wcheck) - pos[0], -(max(hcheck) - pos[1])), min(max(wcheck) - pos[0], -(min(hcheck) - pos[1])) + 1)
    check = [[(x, pos[1]) for x in wcheck], [(pos[0], y) for y in hcheck], [(i + pos[0], i + pos[1]) for i in drurange], [(i + pos[0], -(i - pos[1])) for i in drdrange]]
    for ch in check:
        if len(ch) >= GOAL:
            pts = 0
            for spos in ch:
                if grid[spos][1] == cplayer:
                    pts += 1
                    if pts == GOAL:
                        gameover = cplayer
                        break
                else:
                    pts = 0
    if gameover == False and count == FIELD_SIZE[0] * FIELD_SIZE[1]:
        gameover = -1

def despawn():
    global despawning
    if not despawning:
        full = [pos for pos in grid if grid[pos][1] != None]
        despawning = [time.time(), DESPAWN_TIME / len(full)]
    else:
        if time.time() - despawning[0] >= despawning[1]:
            full = [pos for pos in grid if grid[pos][1] != None]
            if full:
                grid[random.choice(full)][1] = None
                despawning[0] = time.time()
            else:
                despawning = False

def render_text():
    global label
    if not label:
        if txt:
            msg = txt.pop(0)
            label = [font.render(msg[0], False, msg[1]), time.time()]
    else:
        td = time.time() - label[1]
        if td < TXT_TIME:
            d = td - halft
            k = (abs(d) / halft) ** TXT_SPEED
            lsize = label[0].get_size()
            alpha = int(round(MAXDIM - k * MAXDIM))
            pos = [int(round((W_SIZE[0] - lsize[0]) / 2)), int(round((W_SIZE[1] / 2 - lsize[1] / 2) + (W_SIZE[1] + txtsize * 5) / 2 * math.copysign(k, -d)))]
            overlay.fill([0, 0, 0])
            overlay.set_alpha(alpha)
            screen.blit(overlay, [0, 0])
            screen.blit(label[0], pos)
        else:
            label = None

def game_over():
    global gameover
    global count
    global won
    if not gameover == -2:
        txt.append(["GAME OVER", TXT_COLOR])
        if gameover == -1:
            txt.append(["YOU TIED!", TXT_COLOR])
        else:
            txt.append(["%s WON!" % PLAYERS[gameover][1].upper(), PLAYERS[gameover][0]])
            won = gameover
            if not gameover == 0:
                PLAYERS.insert(0, PLAYERS.pop(gameover))
        gameover = -2
    else:
        if not txt and not label:
            count = 0
            despawn()
            if not despawning:
                if won != 0:
                    tokens.insert(0, tokens.pop(won))
                gameover = False

##### GRAPHICS SETUP #####
relsize = [FIELD_SIZE[i] + (FIELD_SIZE[i] + 1) * OFFSET for i in range(2)]
ratio = (W_SIZE[0] / relsize[0]) / (W_SIZE[1] / relsize[1])
if ratio < 1:
    banner = MIN_BANNER * W_SIZE[0]
    num = W_SIZE[0] - banner * 2
    fieldsize = [int(round(num)), int(round(relsize[1] / relsize[0] * num))]
    tokensize = num / relsize[0]
else:
    banner = MIN_BANNER * W_SIZE[0]
    num = W_SIZE[1] - banner * 2
    fieldsize = [int(round(relsize[0] / relsize[1] * num)), int(round(num))]
    tokensize = num / relsize[1]
bpos = [int(round((W_SIZE[i] - fieldsize[i]) / 2)) for i in range(2)]
gravity = GRAVITY * fieldsize[1]
rr = tokensize / 2
r = int(round(rr))
rh = int(round(rr * HOLE_SIZE))
halft = TXT_TIME / 2
size = FIELD_SIZE[0] * FIELD_SIZE[1]
offset = tokensize * OFFSET
board = pygame.Surface(fieldsize, pygame.SRCALPHA)
overlay = pygame.Surface(W_SIZE)
board.fill(BOARD_COLOR)
grid = {}
txtsize = int(round(W_SIZE[1] * TXT_SIZE))
xsnaps = []
for x in range(FIELD_SIZE[0]):
    xpos = int(round((x + 1) * offset + x * rr * 2 + r))
    xsnaps.append(bpos[0] + xpos - r)
    for y in range(FIELD_SIZE[1]):
        pos = [xpos, int(round((y + 1) * offset + y * rr * 2 + r))]
        grid[(x, FIELD_SIZE[1] - y - 1)] = [[pos[0] + bpos[0] - r, pos[1] + bpos[1] - r], None]
        pygame.draw.circle(board, [0, 0, 0, 0], pos, rh)
tokens = [pygame.Surface([int(round(tokensize))] * 2, pygame.SRCALPHA) for p in PLAYERS]
for i, data in enumerate(PLAYERS):
    pygame.draw.circle(tokens[i], data[0], [r] * 2, r)

##### GAME SETUP #####
count = 0
falling = "popout"
gameover = False
txt = []
label = None
despawning = False

##### PYGAME SETUP #####
pygame.init()
clock = pygame.time.Clock()
font = pygame.font.Font("Pixeled.ttf", txtsize)
screen = pygame.display.set_mode(W_SIZE)

##### MAIN LOOP #####
run = True
while run:
    cplayer = count % len(PLAYERS)
    flip_events()
    screen.fill(BG_COLOR)
    if gameover == False:
        render_loose()
    render_still()
    render_main()
    if not type(gameover) == type(bool()):
        game_over()
    render_text()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
