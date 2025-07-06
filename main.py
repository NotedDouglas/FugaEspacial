import pygame
import sys
import random
import sqlite3

# Inicia o pygame
pygame.init()


def criar_banco():
    conn = sqlite3.connect('score.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tempo INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def salvar_score(score):
    conn = sqlite3.connect('score.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (tempo) VALUES (?)', (score,))
    conn.commit()
    conn.close()


def obter_recorde():
    conn = sqlite3.connect('score.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(tempo) FROM scores')
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado if resultado else 0


def obter_top_scores(limite=5):
    conn = sqlite3.connect('score.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tempo FROM scores ORDER BY tempo DESC LIMIT ?', (limite,))
    resultados = cursor.fetchall()
    conn.close()
    return [r[0] for r in resultados]


# Cria o banco de dados se não existir
criar_banco()

# Configura a janela do jogo
LARGURA = 600
ALTURA = 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Fuga Estelar')

# Carrega as imagens
background = pygame.image.load('assets/background.jpg')
player = pygame.image.load('assets/Player1.png')
enemy = pygame.image.load('assets/Enemy1.png')
background_inicial = pygame.image.load('assets/telaInicial.png')
bomba_img = pygame.image.load("assets/bomba.png")

# Fonte
fonte = pygame.font.SysFont(None, 60)
fonte_score = pygame.font.SysFont(None, 36)


def tela_inicial():
    opcoes = ['JOGAR', 'SCORE']
    selecionado = 0
    while True:
        TELA.blit(background_inicial, (0, 0))
        titulo = fonte.render('Fuga Estelar', True, (255, 255, 255))
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 60))

        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = fonte_score.render(opcao, True, cor)
            TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 160 + i * 50))

        pygame.display.update()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN:
                    if opcoes[selecionado] == 'JOGAR':
                        return
                    elif opcoes[selecionado] == 'SCORE':
                        mostrar_score()


def mostrar_score():
    top_scores = obter_top_scores()
    while True:
        TELA.fill((0, 0, 0))
        titulo = fonte.render('Melhores Scores', True, (255, 255, 255))
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 40))

        for i, tempo in enumerate(top_scores):
            texto = fonte_score.render(f"{i + 1}º - {tempo} segundos", True, (255, 255, 255))
            TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 100 + i * 40))

        info = fonte_score.render('Pressione ESC para voltar', True, (150, 150, 150))
        TELA.blit(info, (LARGURA // 2 - info.get_width() // 2, ALTURA - 50))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return


# Chama a tela inicial antes de começar o jogo
tela_inicial()

# Criar retângulo para colisão
jogador = player.get_rect(topleft=(50, 50))
inimigo = enemy.get_rect(topleft=(300, 200))
velocidade = 4
vel_inimigo = 1
clock = pygame.time.Clock()
tempo_inicial = pygame.time.get_ticks()

bombas = []
tempo_ultima_bomba = 0
cooldown_bomba = 500

# Loop principal do jogo
jogar = True
while jogar:
    clock.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jogar = False

    # Movimentação do jogador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jogador.left > 0:
        jogador.x -= velocidade
    if teclas[pygame.K_RIGHT] and jogador.right < LARGURA:
        jogador.x += velocidade
    if teclas[pygame.K_UP] and jogador.top > 0:
        jogador.y -= velocidade
    if teclas[pygame.K_DOWN] and jogador.bottom < ALTURA:
        jogador.y += velocidade

    # Soltar bomba
    tempo_atual_ticks = pygame.time.get_ticks()
    if teclas[pygame.K_SPACE]:
        if tempo_atual_ticks - tempo_ultima_bomba > cooldown_bomba:
            bombas.append(jogador.center)
            tempo_ultima_bomba = tempo_atual_ticks

    # Movimentação do inimigo em direção ao jogador
    if inimigo.x < jogador.x:
        inimigo.x += vel_inimigo
    elif inimigo.x > jogador.x:
        inimigo.x -= vel_inimigo
    if inimigo.y < jogador.y:
        inimigo.y += vel_inimigo
    elif inimigo.y > jogador.y:
        inimigo.y -= vel_inimigo

    # Verifica colisão com o inimigo
    if jogador.colliderect(inimigo):
        TELA.fill((0, 0, 0))
        tempo_final = (pygame.time.get_ticks() - tempo_inicial) // 1000
        salvar_score(tempo_final)
        recorde = obter_recorde()

        texto = fonte.render('Game Over', True, (255, 255, 255))
        texto_score = fonte_score.render(f"Tempo: {tempo_final}s | Recorde: {recorde}s", True, (255, 255, 255))
        texto_restart = fonte_score.render("ENTER - Reiniciar | ESC - Sair", True, (200, 200, 200))

        TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, ALTURA // 2 - 40))
        TELA.blit(texto_score, (LARGURA // 2 - texto_score.get_width() // 2, ALTURA // 2))
        TELA.blit(texto_restart, (LARGURA // 2 - texto_restart.get_width() // 2, ALTURA // 2 + 40))
        pygame.display.update()

        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        jogador.topleft = (50, 50)
                        inimigo.topleft = (300, 200)
                        tempo_inicial = pygame.time.get_ticks()
                        bombas.clear()
                        esperando = False
                    elif evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        continue

    # Verifica colisão inimigo com bomba
    for bomba in bombas:
        bomba_rect = pygame.Rect(bomba[0] - bomba_img.get_width() // 2, bomba[1] - bomba_img.get_height() // 2,
                                 bomba_img.get_width(), bomba_img.get_height())
        if inimigo.colliderect(bomba_rect):
            TELA.fill((0, 0, 0))
            for b in bombas:
                TELA.blit(bomba_img, (b[0] - bomba_img.get_width() // 2, b[1] - bomba_img.get_height() // 2))

            tempo_final = (pygame.time.get_ticks() - tempo_inicial) // 1000
            salvar_score(tempo_final)
            recorde = obter_recorde()

            texto = fonte.render('Você Venceu!', True, (0, 255, 0))
            texto_score = fonte_score.render(f"Tempo: {tempo_final}s | Recorde: {recorde}s", True, (255, 255, 255))
            texto_restart = fonte_score.render("ENTER - Jogar Novamente | ESC - Sair", True, (200, 200, 200))

            TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, ALTURA // 2 - 40))
            TELA.blit(texto_score, (LARGURA // 2 - texto_score.get_width() // 2, ALTURA // 2))
            TELA.blit(texto_restart, (LARGURA // 2 - texto_restart.get_width() // 2, ALTURA // 2 + 40))
            pygame.display.update()

            esperando = True
            while esperando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_RETURN:
                            jogador.topleft = (50, 50)
                            inimigo.topleft = (300, 200)
                            tempo_inicial = pygame.time.get_ticks()
                            bombas.clear()
                            esperando = False
                        elif evento.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            break  # Sai do loop para evitar múltiplas execuções

    # Aumenta dificuldade com o tempo
    tempo_atual = (pygame.time.get_ticks() - tempo_inicial) // 1000

    # Desenha fundo, jogador, inimigo e bombas (BOMBAS DESENHADAS AQUI)
    TELA.blit(background, (0, 0))
    TELA.blit(player, jogador.topleft)
    TELA.blit(enemy, inimigo.topleft)
    for bomba in bombas:
        TELA.blit(bomba_img, (bomba[0] - bomba_img.get_width() // 2, bomba[1] - bomba_img.get_height() // 2))

    recorde = obter_recorde()
    texto_score = fonte_score.render(f"Tempo: {tempo_atual}s | Recorde: {recorde}s", True, (255, 255, 255))
    TELA.blit(texto_score, (10, 10))

    pygame.display.update()

# Encerra o jogo
pygame.quit()
sys.exit()
