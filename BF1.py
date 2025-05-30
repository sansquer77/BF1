import streamlit as st
import sqlite3
import bcrypt
import jwt as pyjwt
import pandas as pd
from datetime import datetime, timedelta
import ast
import os
import matplotlib.pyplot as plt
import dash

DB_PATH = 'bolao_f1Prod.db'
JWT_SECRET = st.secrets["JWT_SECRET"]
JWT_EXP_MINUTES = 120

REGULAMENTO = """
REGULAMENTO BF1-2025

O BF1-2025 terá início, oficialmente, em 16 de março, no dia do GP da Austrália e término em 07 de dezembro, quando será disputado o último GP, o de Abu Dhabi.

Inscrições para o BF1 estão liberadas a partir de qualquer etapa.
A inscrição é de R$200,00 a ser pago no ato da inscrição via PIX.
Em caso de desistência da participação durante o campeonato a taxa de inscrição não será devolvida.
Cabe ressaltar, que a pontuação do novo participante será 80% da pontuação do participante mais mal colocado no bolão no momento da inscrição e terá 0 pontos na aposta de campeão, caso ocorra após o início do campeonato.

As apostas dos participantes devem ser efetuadas até o horário programado da corrida e compartilhadas via formulário padrão que está no grupo do WhatsApp. Fica facultado ao participante a geração de um print da tela do aplicativo com a aposta e o horário da mensagem para futuras validações, mas cabe ressaltar que a ferramenta possui um Time Stamp do horário de envio das mensagens.

a. O participante pode enviar quantas apostas quiser até o horário limite, sendo válida a última enviada.  
b. Apostas registradas após o horário da largada, por exemplo 09:01 sendo a corrida às 09h serão desconsideradas.  
c. Os horários das corridas deste ano são:

Grande Prêmio | Data | Horário  
--- | --- | ---  
1  Grande Prêmio da Austrália           | 16 de março         | 01:00  
2  Grande Prêmio da China Sprint        | 22 de março         | 00:00  
3  Grande Prêmio da China               | 23 de março         | 04:00  
4  Grande Prêmio do Japão               | 6 de abril          | 02:00  
5  Grande Prêmio do Bahrain             | 13 de abril         | 12:00  
6  Grande Prêmio da Arábia Saudita      | 20 de abril         | 14:00  
7  Grande Prêmio de Miami Sprint        | 3 de maio           | 13:00  
8  Grande Prêmio de Miami               | 4 de maio           | 17:00  
9  Grande Prêmio da Emília-Romanha      | 18 de maio          | 10:00  
10 Grande Prêmio de Mônaco              | 25 de maio          | 10:00  
11 Grande Prêmio da Espanha             | 1 de junho          | 10:00  
12 Grande Prêmio do Canadá              | 15 de junho         | 15:00  
13 Grande Prêmio da Áustria             | 29 de junho         | 10:00  
14 Grande Prêmio da Grã-Bretanha        | 6 de julho          | 11:00  
15 Grande Prêmio da Bélgica Sprint      | 26 de julho         | 07:00  
16 Grande Prêmio da Bélgica             | 27 de julho         | 10:00  
17 Grande Prêmio da Hungria             | 3 de agosto         | 10:00  
18 Grande Prêmio dos Países Baixos      | 31 de agosto        | 10:00  
19 Grande Prêmio da Itália              | 7 de setembro       | 10:00  
20 Grande Prêmio do Azerbaijão          | 21 de setembro      | 08:00  
21 Grande Prêmio de Singapura           | 5 de outubro        | 09:00  
22 Grande Prêmio dos EUA Sprint         | 18 de outubro       | 14:00  
23 Grande Prêmio dos EUA                | 19 de outubro       | 16:00  
24 Grande Prêmio da Cidade do México    | 26 de outubro       | 17:00  
25 Grande Prêmio de São Paulo Sprint    | 8 de novembro       | 11:00  
26 Grande Prêmio de São Paulo           | 9 de novembro       | 14:00  
27 Grande Prêmio de Las Vegas           | 22 de novembro      | 01:00  
28 Grande Prêmio do Catar Sprint        | 29 de novembro      | 11:00  
29 Grande Prêmio do Catar               | 30 de novembro      | 13:00  
30 Grande Prêmio de Abu Dhabi           | 7 de dezembro       | 10:00  

O participante que não efetuar a sua aposta ATÉ O PRAZO DEFINIDO DO ITEM-3, irá concorrer com a mesma aposta da última corrida.  
Quando se tratar da primeira vez que a aposta não for feita, e apenas neste caso, será computado 100% dos pontos.  
Caso o apostador não aposte na primeira corrida do campeonato, como não haverá base para repetição da aposta a pontuação será 80% do pior pontuador para esta corrida e o benefício do item “a” deste tópico será mantido.  
Para o segundo atraso em diante os pontos sofrerão um desconto de 25%.

Pontuação

Cada participante deve indicar o campeão e o vice do campeonato de pilotos e a equipe vencedora do campeonato de construtores ANTES do início da primeira prova do ano em formulário específico.  
A pontuação será 150 pontos se acertar o campeão, 100 se acertar o vice, 80 acertando equipe – Que serão somados à pontuação ao final do campeonato.

Cada participante possui 15 (quinze) fichas para serem apostadas a cada corrida da seguinte maneira:  
A aposta deve conter no mínimo 3 pilotos de equipes diferentes (Apostou no Hamilton, não pode apostar no Leclerc por ex.)  
Sem limite de ficha por piloto, vale 13 / 1 / 1, desde que respeitada a regra acima.  
As corridas Sprint seguem a mesma regra, sendo consideradas provas válidas para a pontuação.  
Deve ser indicado o piloto que irá chegar em 11º lugar em todas as provas e em caso de acerto será computado 25 pontos.

A pontuação do participante será a multiplicação das fichas apostadas em cada piloto pelo número de pontos que ele obteve na prova (fichas x pontos) + pontuação do 11º lugar.  
As apostas serão lançadas na planilha de controle que está hospedada no OneDrive, sendo que o placar atualizado será publicado na página do grupo e no WhatsApp após as corridas.

Critérios de Desempate

Caso haja empate de pontos na classificação final, as posições serão definidas pelos seguintes critérios, na ordem:  
Quem tiver apostado antes mais vezes no ano  
Quem mais vezes acertou o 11º lugar  
Quem acertou o campeão  
Quem acertou a equipe campeã  
Quem acertou o vice

Forma de pagamento e premiação

A premiação será um voucher de 50% do fundo arrecadado das inscrições para o primeiro colocado, 30% para o segundo e 20% para o terceiro gastarem nas bebidas de sua escolha a serem adquiridas após a definição dos vencedores e escolha dos prêmios.

A premiação será realizada em um Happy-Hour a ser agendado entre os participantes em data e local a serem definidos posteriormente ao final do campeonato.
"""

# --- BANCO E FUNÇÕES DE DADOS ---
def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = db_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
email TEXT UNIQUE,
senha_hash TEXT,
perfil TEXT,
status TEXT DEFAULT 'Ativo',
faltas INTEGER DEFAULT 0)''')
    usuario_master = st.secrets["usuario_master"]
    email_master = st.secrets["email_master"]
    senha_master = st.secrets["senha_master"]
    senha_hash = bcrypt.hashpw(senha_master.encode(), bcrypt.gensalt())
    c.execute('''INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil, status, faltas)
VALUES (?, ?, ?, ?, ?, ?)''',
    (usuario_master, email_master, senha_hash, 'master', 'Ativo', 0))

    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
equipe TEXT,
status TEXT DEFAULT 'Ativo'
)''')
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,    
data TEXT,
status TEXT DEFAULT 'Ativo',
tipo TEXT DEFAULT 'Normal'
)''')
    c.execute('''CREATE TABLE IF NOT EXISTS apostas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario_id INTEGER,
prova_id INTEGER,
data_envio TEXT,
pilotos TEXT,
fichas TEXT,
piloto_11 TEXT,
nome_prova TEXT,
automatica INTEGER DEFAULT 0,
FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
FOREIGN KEY(prova_id) REFERENCES provas(id)
)''')
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
prova_id INTEGER PRIMARY KEY,
posicoes TEXT,
FOREIGN KEY(prova_id) REFERENCES provas(id)
)''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
apostador TEXT,
data TEXT,
horario TEXT,
aposta TEXT,
nome_prova TEXT
)''')
    conn.commit()
    conn.close()

@st.cache_data
def get_usuarios_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM usuarios', conn)
    conn.close()
    return df
@st.cache_data
def get_pilotos_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM pilotos', conn)
    conn.close()
    return df
@st.cache_data
def get_provas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df
@st.cache_data
def get_apostas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM apostas', conn)
    conn.close()
    return df
@st.cache_data
def get_resultados_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    return df
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode()  # converte para bytes
    return bcrypt.checkpw(password.encode(), hashed)
def generate_token(user_id, perfil, status):
    payload = {
        'user_id': user_id,
        'perfil': perfil,
        'status': status,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    token = pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token
def decode_token(token):
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except pyjwt.ExpiredSignatureError:
        return None
    except Exception:
        return None
def cadastrar_usuario(nome, email, senha, perfil='participante', status='Ativo'):
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status, faltas) VALUES (?, ?, ?, ?, ?, ?)', 
                  (nome, email, senha_hash, perfil, status, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
def get_user_by_email(email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, senha_hash, perfil, status, faltas FROM usuarios WHERE email=?', (email,))
    user = c.fetchone()
    conn.close()
    return user
def get_user_by_id(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, perfil, status, faltas FROM usuarios WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def autenticar_usuario(email, senha):
    user = get_user_by_email(email)
    if user and check_password(senha, user[3]):
        return user
    return None

def salvar_aposta(usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova, automatica=0):
    conn = db_connect()
    c = conn.cursor()
    data_envio = datetime.now().isoformat()
    c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova, automatica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11, nome_prova, automatica))
    conn.commit()
    conn.close()

def registrar_log_aposta(apostador, aposta, nome_prova):
    conn = db_connect()
    c = conn.cursor()
    agora = datetime.now()
    data = agora.strftime('%Y-%m-%d')
    horario = agora.strftime('%H:%M:%S')
    c.execute('INSERT INTO log_apostas (apostador, data, horario, aposta, nome_prova) VALUES (?, ?, ?, ?, ?)',
              (apostador, data, horario, aposta, nome_prova))
    conn.commit()
    conn.close()

def calcular_pontuacao_lote(apostas_df, resultados_df, provas_df):
    pontos_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    pontos_sprint = [8, 7, 6, 5, 4, 3, 2, 1]  # Para Sprint
    resultados = {}
    for _, row in resultados_df.iterrows():
        resultados[row['prova_id']] = ast.literal_eval(row['posicoes'])
    # Cria um dicionário de tipos das provas
    tipos_prova = dict(zip(provas_df['id'], provas_df['tipo'] if 'tipo' in provas_df.columns else ['Normal']*len(provas_df)))
    pontos = []
    for _, aposta in apostas_df.iterrows():
        prova_id = aposta['prova_id']
        if prova_id not in resultados:
            pontos.append(None)
            continue
        res = resultados[prova_id]
        pilotos = aposta['pilotos'].split(",")
        fichas = list(map(int, aposta['fichas'].split(",")))
        piloto_11 = aposta['piloto_11']
        automatica = int(aposta['automatica'])
        pt = 0
        tipo = tipos_prova.get(prova_id, 'Normal')
        if tipo == 'Sprint':
            # Pontuam só os 8 primeiros (8 para 1º, 7 para 2º, ..., 1 para 8º)
            for p, f in zip(pilotos, fichas):
                for pos, nome in res.items():
                    pos_int = int(pos)
                    if pos_int <= 8 and nome == p:
                        pt += f * pontos_sprint[pos_int-1]
            # Bônus para 11º colocado na Sprint também
            if '11' in res and res['11'] == piloto_11:
                pt += 25
        else:
            # Prova normal
            for p, f in zip(pilotos, fichas):
                for pos, nome in res.items():
                    pos_int = int(pos)
                    if pos_int <= 10 and nome == p:
                        pt += f * pontos_f1[pos_int-1]
            if '11' in res and res['11'] == piloto_11:
                pt += 25
        if automatica >= 2:
            pt = int(pt * 0.75)
        pontos.append(pt)
    return pontos

def gerar_aposta_automatica(usuario_id, prova_id, nome_prova, apostas_df, provas_df):
    provas_df = provas_df.sort_values('data')
    idx_prova = provas_df[provas_df['id'] == prova_id].index[0]
    if idx_prova == 0:
        return False, "Não há prova anterior para copiar a aposta."
    prova_ant_id = provas_df.iloc[idx_prova-1]['id']
    ap_ant = apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['prova_id'] == prova_ant_id)]
    if ap_ant.empty:
        return False, "Participante não tem aposta anterior para copiar."
    ap_ant = ap_ant.iloc[0]
    pilotos_ant = ap_ant['pilotos'].split(",")
    fichas_ant = list(map(int, ap_ant['fichas'].split(",")))
    piloto_11_ant = ap_ant['piloto_11']
    num_auto = len(apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['automatica'] >= 1)])
    salvar_aposta(usuario_id, prova_id, pilotos_ant, fichas_ant, piloto_11_ant, nome_prova, automatica=num_auto+1)
    return True, "Aposta automática gerada!"

# --- INICIALIZAÇÃO E MENU ---
st.set_page_config(page_title="Bolão F1 2025", layout="wide")
init_db()

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "Login"
if 'token' not in st.session_state:
    st.session_state['token'] = None

def menu_master():
    return [
        "Painel do Participante",
        "Gestão de Usuários",
        "Cadastro de novo participante",
        "Gestão do campeonato",
        "Gestão de Apostas",
        "Atualização de resultados",
        "Log de Apostas",
        "Classificação",
        "Dash F1",
        "Exportar/Importar Excel",
        "Regulamento",
        "Logout"
    ]
def menu_admin():
    return [
        "Painel do Participante",
        "Gestão de Apostas",
        "Atualização de resultados",
        "Log de Apostas",
        "Classificação",
        "Dash F1",
        "Regulamento",
        "Logout"
    ]
def menu_participante():
    return [
        "Painel do Participante",
        "Log de Apostas",
        "Classificação",
        "Dash F1",
        "Regulamento",
        "Logout"
    ]

def get_payload():
    token = st.session_state.get('token')
    if not token:
        st.session_state['pagina'] = "Login"
        st.stop()
    payload = decode_token(token)
    if not payload:
        st.session_state['pagina'] = "Login"
        st.session_state['token'] = None
        st.stop()
    return payload

# --- Login, Esqueceu a Senha e Criar Usuário Inativo ---
if st.session_state['pagina'] == "Login":
    st.title("Login")
    if 'esqueceu_senha' not in st.session_state:
        st.session_state['esqueceu_senha'] = False
    if 'criar_usuario' not in st.session_state:
        st.session_state['criar_usuario'] = False

    if not st.session_state['esqueceu_senha'] and not st.session_state['criar_usuario']:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            if st.button("Entrar"):
                user = autenticar_usuario(email, senha)
                if user:
                    token = generate_token(user[0], user[4], user[5])
                    st.session_state['token'] = token
                    st.session_state['pagina'] = "Painel do Participante"
                    st.success(f"Bem-vindo, {user[1]}!")
                else:
                    st.error("Usuário ou senha inválidos.")
        with col2:
            if st.button("Esqueceu a senha?"):
                st.session_state['esqueceu_senha'] = True
        with col3:
            if st.button("Criar usuário"):
                st.session_state['criar_usuario'] = True

    elif st.session_state['esqueceu_senha']:
        st.subheader("Redefinir senha")
        email_reset = st.text_input("Email cadastrado")
        nova_senha = st.text_input("Nova senha", type="password")
        if st.button("Salvar nova senha"):
            user = get_user_by_email(email_reset)
            if user:
                conn = db_connect()
                c = conn.cursor()
                nova_hash = hash_password(nova_senha)
                c.execute('UPDATE usuarios SET senha_hash=? WHERE email=?', (nova_hash, email_reset))
                conn.commit()
                conn.close()
                st.success("Senha redefinida com sucesso! Faça login com a nova senha.")
                st.session_state['esqueceu_senha'] = False
            else:
                st.error("Email não cadastrado.")
        if st.button("Voltar para login"):
            st.session_state['esqueceu_senha'] = False

    elif st.session_state['criar_usuario']:
        st.subheader("Criar novo usuário")
        nome_novo = st.text_input("Nome completo")
        email_novo = st.text_input("Email")
        senha_novo = st.text_input("Senha", type="password")
        if st.button("Cadastrar usuário"):
            if cadastrar_usuario(nome_novo, email_novo, senha_novo, perfil='participante', status='Inativo'):
                st.success("Usuário criado com sucesso! Aguarde aprovação do administrador.")
                st.session_state['criar_usuario'] = False
            else:
                st.error("Email já cadastrado.")
        if st.button("Voltar para login", key="voltar_login_criar"):
            st.session_state['criar_usuario'] = False

# ---------------- MENU LATERAL ----------------
if st.session_state['token']:
    payload = get_payload()
    perfil = payload['perfil']
    if perfil == 'master':
        menu = menu_master()
    elif perfil == 'admin':
        menu = menu_admin()
    else:
        menu = menu_participante()
    escolha = st.sidebar.radio("Menu", menu)
    st.session_state['pagina'] = escolha

# ---------------- PAINEL DO PARTICIPANTE ----------------
if st.session_state['pagina'] == "Painel do Participante" and st.session_state['token']:
    payload = get_payload()
    user = get_user_by_id(payload['user_id'])
    st.title("Painel do Participante")
    st.write(f"Bem-vindo, {user[1]} ({user[3]}) - Status: {user[4]}")
    st.cache_data.clear()
    provas = get_provas_df()
    pilotos_df = get_pilotos_df()
    pilotos_ativos_df = pilotos_df[pilotos_df['status'] == 'Ativo']
    pilotos = pilotos_ativos_df['nome'].tolist()
    equipes = pilotos_ativos_df['equipe'].tolist()
    pilotos_equipe = dict(zip(pilotos, equipes))
    if user[4] == "Ativo":
        if len(provas) > 0 and len(pilotos_df) > 2:
            prova_id = st.selectbox("Escolha a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            nome_prova = provas[provas['id']==prova_id]['nome'].values[0]
            apostas_df = get_apostas_df()
            aposta_existente = apostas_df[(apostas_df['usuario_id'] == user[0]) & (apostas_df['prova_id'] == prova_id)]
            pilotos_apostados_ant = []
            fichas_ant = []
            piloto_11_ant = ""
            if not aposta_existente.empty:
                aposta_existente = aposta_existente.iloc[0]
                pilotos_apostados_ant = aposta_existente['pilotos'].split(",")
                fichas_ant = list(map(int, aposta_existente['fichas'].split(",")))
                piloto_11_ant = aposta_existente['piloto_11']
            else:
                fichas_ant = []
                piloto_11_ant = ""
            st.write("Escolha seus pilotos e distribua 15 fichas entre eles (mínimo 3 pilotos de equipes diferentes):")
            max_linhas = 5
            pilotos_aposta = []
            fichas_aposta = []
            for i in range(max_linhas):
                mostrar = False
                if i < 3:
                    mostrar = True
                elif i == 3 and len([p for p in pilotos_aposta if p != "Nenhum"]) == 3 and sum(fichas_aposta) < 15:
                    mostrar = True
                elif i == 4 and len([p for p in pilotos_aposta if p != "Nenhum"]) == 4 and sum(fichas_aposta) < 15:
                    mostrar = True
                if mostrar:
                    col1, col2 = st.columns([3,1])
                    with col1:
                        piloto_sel = st.selectbox(
                            f"Piloto {i+1}",
                            ["Nenhum"] + pilotos,
                            index=(pilotos.index(pilotos_apostados_ant[i]) + 1) if len(pilotos_apostados_ant) > i and pilotos_apostados_ant[i] in pilotos else 0,
                            key=f"piloto_aposta_{i}"
                        )
                    with col2:
                        if piloto_sel != "Nenhum":
                            valor_ficha = st.number_input(
                                f"Fichas para {piloto_sel}", min_value=0, max_value=15,
                                value=fichas_ant[i] if len(fichas_ant) > i else 0,
                                key=f"fichas_aposta_{i}"
                            )
                            pilotos_aposta.append(piloto_sel)
                            fichas_aposta.append(valor_ficha)
                        else:
                            pilotos_aposta.append("Nenhum")
                            fichas_aposta.append(0)
            pilotos_validos = [p for p in pilotos_aposta if p != "Nenhum"]
            fichas_validas = [f for i, f in enumerate(fichas_aposta) if pilotos_aposta[i] != "Nenhum"]
            equipes_apostadas = [pilotos_equipe[p] for p in pilotos_validos]
            total_fichas = sum(fichas_validas)
            pilotos_11_opcoes = [p for p in pilotos if p not in pilotos_validos]
            if not pilotos_11_opcoes:
                pilotos_11_opcoes = pilotos
            piloto_11 = st.selectbox(
                "Palpite para 11º colocado", pilotos_11_opcoes,
                index=pilotos_11_opcoes.index(piloto_11_ant) if piloto_11_ant in pilotos_11_opcoes else 0
            )
            erro = None
            if st.button("Efetivar Aposta"):
                if len(set(pilotos_validos)) != len(pilotos_validos):
                    erro = "Não é permitido apostar em dois pilotos iguais."
                elif len(set(equipes_apostadas)) != len(equipes_apostadas):
                    erro = "Não é permitido apostar em dois pilotos da mesma equipe."
                elif len(pilotos_validos) < 3:
                    erro = "Você deve apostar em pelo menos 3 pilotos de equipes diferentes."
                elif total_fichas != 15:
                    erro = "A soma das fichas deve ser exatamente 15."
                elif piloto_11 in pilotos_validos:
                    erro = "O 11º colocado não pode ser um dos pilotos apostados."
                if erro:
                    st.error(erro)
                else:
                    salvar_aposta(
                        user[0], prova_id, pilotos_validos,
                        fichas_validas,
                        piloto_11, nome_prova, automatica=0
                    )
                    aposta_str = f"Prova: {nome_prova}, Pilotos: {pilotos_validos}, Fichas: {fichas_validas}, 11º: {piloto_11}"
                    registrar_log_aposta(user[1], aposta_str, nome_prova)
                    st.success("Aposta registrada/atualizada!")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("Administração deve cadastrar provas e pilotos antes das apostas.")
    else:
        st.info("Usuário inativo: você só pode visualizar suas apostas anteriores.")

    # --- Exibição detalhada das apostas do participante ---
    st.subheader("Minhas apostas detalhadas")
    apostas_df = get_apostas_df()
    resultados_df = get_resultados_df()
    provas_df = get_provas_df()
    apostas_part = apostas_df[apostas_df['usuario_id'] == user[0]].sort_values('prova_id')

    pontos_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    pontos_sprint = [8, 7, 6, 5, 4, 3, 2, 1]
    bonus_11 = 25  # Ajuste se necessário
        
    if not apostas_part.empty:
        # Cria uma aba para cada aposta (nome da prova)
        nomes_abas = [f"{ap['nome_prova']} ({ap['prova_id']})" for _, ap in apostas_part.iterrows()]
        abas = st.tabs(nomes_abas)
        for aba, (_, aposta) in zip(abas, apostas_part.iterrows()):
            with aba:
                prova_id = aposta['prova_id']
                prova_nome = aposta['nome_prova']
                fichas = list(map(int, aposta['fichas'].split(',')))
                pilotos_apostados = aposta['pilotos'].split(',')
                piloto_11_apostado = aposta['piloto_11']
                automatica = aposta.get('automatica', 0)
    
                tipo_prova = provas_df[provas_df['id'] == prova_id]['tipo'].values[0] if not provas_df[provas_df['id'] == prova_id].empty else 'Normal'
    
                resultado_row = resultados_df[resultados_df['prova_id'] == prova_id]
                if not resultado_row.empty:
                    try:
                        posicoes_dict = ast.literal_eval(resultado_row.iloc[0]['posicoes'])
                    except Exception:
                        posicoes_dict = {}
                else:
                    posicoes_dict = {}
    
                dados = []
                total_pontos = 0
    
                if tipo_prova == 'Sprint':
                    pontos_lista = pontos_sprint
                    n_pos = 8
                else:
                    pontos_lista = pontos_f1
                    n_pos = 10
    
                piloto_para_pos = {v: int(k) for k, v in posicoes_dict.items()}
    
                for i in range(n_pos):
                    aposta_piloto = pilotos_apostados[i] if i < len(pilotos_apostados) else ""
                    ficha = fichas[i] if i < len(fichas) else 0
                    pos_real = piloto_para_pos.get(aposta_piloto, None)
                    pontos = 0
                    if pos_real is not None and 1 <= pos_real <= n_pos:
                        pontos = ficha * pontos_lista[pos_real - 1]
                    total_pontos += pontos
                    dados.append({
                        "Piloto Apostado": aposta_piloto,
                        "Fichas": ficha,
                        "Posição Real": pos_real if pos_real is not None else "-",
                        "Pontos": pontos
                    })
    
                piloto_11_real = posicoes_dict.get(11, "")
                pontos_11_col = bonus_11 if piloto_11_apostado == piloto_11_real else 0
                total_pontos += pontos_11_col
    
                if automatica and int(automatica) >= 2:
                    total_pontos = int(total_pontos * 0.75)
    
                st.markdown(f"#### {prova_nome} ({tipo_prova})")
                st.dataframe(pd.DataFrame(dados), hide_index=True)
                st.write(f"**11º Apostado:** {piloto_11_apostado} | **11º Real:** {piloto_11_real} | **Pontos 11º:** {pontos_11_col}")
                st.write(f"**Total de Pontos na Prova:** {total_pontos}")
                st.markdown("---")
    else:
        st.info("Nenhuma aposta registrada.")


# --- GESTÃO DE USUÁRIOS (apenas master) ---
if st.session_state['pagina'] == "Gestão de Usuários" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão de Usuários")
        st.cache_data.clear()
        usuarios = get_usuarios_df()

        # Remove a coluna de hash de senha se existir
        if 'senha_hash' in usuarios.columns:
            usuarios = usuarios.drop(columns=['senha_hash'])

        if len(usuarios) == 0:
            st.info("Nenhum usuário cadastrado.")
        else:
            st.dataframe(usuarios)
            st.write("Selecione um usuário para editar, excluir ou alterar status/perfil:")
            usuario_id = st.selectbox("Usuário", usuarios['id'])
            usuario = usuarios[usuarios['id'] == usuario_id].iloc[0]
            novo_nome = st.text_input("Nome", value=usuario['nome'], key="edit_nome")
            novo_email = st.text_input("Email", value=usuario['email'], key="edit_email")
            novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if usuario['status'] == "Ativo" else 1, key="edit_status")
            novo_perfil = st.selectbox("Perfil", ["participante", "admin"], index=0 if usuario['perfil'] == "participante" else 1, key="edit_perfil")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Atualizar usuário"):
                    if usuario['nome'] == "Password":
                        st.warning("Não é permitido alterar o status ou perfil do usuário master.")
                    else:
                        conn = db_connect()
                        c = conn.cursor()
                        c.execute('UPDATE usuarios SET nome=?, email=?, status=?, perfil=? WHERE id=?',
                                  (novo_nome, novo_email, novo_status, novo_perfil, usuario_id))
                        conn.commit()
                        conn.close()
                        st.success("Usuário atualizado!")
                        st.cache_data.clear()
                        st.rerun()

            with col2:
                if st.button("Excluir usuário"):
                    if usuario['nome'] == "Password":
                        st.warning("Não é permitido excluir o usuário master.")
                    else:
                        conn = db_connect()
                        c = conn.cursor()
                        c.execute('DELETE FROM usuarios WHERE id=?', (usuario_id,))
                        conn.commit()
                        conn.close()
                        st.success("Usuário excluído!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- CADASTRO DE NOVO PARTICIPANTE (apenas master) ---
if st.session_state['pagina'] == "Cadastro de novo participante" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.cache_data.clear()
        st.title("Cadastro de novo participante")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            if cadastrar_usuario(nome, email, senha):
                st.success("Usuário cadastrado com sucesso!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Email já cadastrado.")
    else:
        st.warning("Acesso restrito ao usuário master.")

import pandas as pd
from datetime import datetime

# --- GESTÃO DO CAMPEONATO (Pilotos e Provas) ---
if st.session_state['pagina'] == "Gestão do campeonato" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão do Campeonato")
        tab1, tab2 = st.tabs(["Pilotos", "Provas"])

        # --- PILOTOS ---
        with tab1:
            st.subheader("Adicionar novo piloto")
            nome_piloto = st.text_input("Nome do novo piloto", key="nome_novo_piloto")
            equipe_piloto = st.text_input("Nome da equipe do piloto", key="equipe_novo_piloto")
            status_piloto = st.selectbox("Status do piloto", ["Ativo", "Inativo"], key="status_novo_piloto")
            if st.button("Adicionar piloto", key="btn_add_piloto_form"):
                if not nome_piloto.strip():
                    st.error("Informe o nome do piloto.")
                elif not equipe_piloto.strip():
                    st.error("Informe o nome da equipe.")
                else:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('INSERT INTO pilotos (nome, equipe, status) VALUES (?, ?, ?)', (nome_piloto.strip(), equipe_piloto.strip(), status_piloto))
                    conn.commit()
                    conn.close()
                    st.success("Piloto adicionado!")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("---")
            st.subheader("Pilotos cadastrados")
            pilotos = get_pilotos_df()
            if len(pilotos) == 0:
                st.info("Nenhum piloto cadastrado.")
            else:
                for idx, row in pilotos.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([3,3,2,2,2])
                    with col1:
                        novo_nome = st.text_input(f"Nome piloto {row['id']}", value=row['nome'], key=f"pl_nome_{row['id']}")
                    with col2:
                        nova_equipe = st.text_input(f"Equipe piloto {row['id']}", value=row['equipe'], key=f"pl_eq_{row['id']}")
                    with col3:
                        novo_status = st.selectbox(f"Status piloto {row['id']}", ["Ativo", "Inativo"], index=0 if row.get('status', 'Ativo') == "Ativo" else 1, key=f"pl_status_{row['id']}")
                    with col4:
                        if st.button("Editar piloto", key=f"pl_edit_{row['id']}"):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('UPDATE pilotos SET nome=?, equipe=?, status=? WHERE id=?', (novo_nome, nova_equipe, novo_status, row['id']))
                            conn.commit()
                            conn.close()
                            st.success("Piloto editado!")
                            st.cache_data.clear()
                            st.rerun()
                    with col5:
                        if st.button("Excluir piloto", key=f"pl_del_{row['id']}"):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('DELETE FROM pilotos WHERE id=?', (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("Piloto excluído!")
                            st.cache_data.clear()
                            st.rerun()

        # --- PROVAS ---
        with tab2:
            st.subheader("Adicionar nova prova")
            nome_prova = st.text_input("Nome da nova prova", key="nome_nova_prova")
            data_prova_str = st.text_input("Data da nova prova (DD/MM/AAAA)", key="data_nova_prova")
            status_prova = st.selectbox("Status da prova", ["Ativo", "Inativo"], key="status_nova_prova")
            tipo_prova = st.selectbox("Tipo da prova", ["Normal", "Sprint"], key="tipo_nova_prova")
            if st.button("Adicionar prova", key="btn_add_prova_form"):
                if not nome_prova.strip():
                    st.error("Informe o nome da prova.")
                else:
                    try:
                        data_prova = datetime.strptime(data_prova_str, "%d/%m/%Y")
                        conn = db_connect()
                        c = conn.cursor()
                        c.execute('INSERT INTO provas (nome, data, status, tipo) VALUES (?, ?, ?, ?)', (nome_prova.strip(), data_prova.strftime("%Y-%m-%d"), status_prova, tipo_prova))
                        conn.commit()
                        conn.close()
                        st.success("Prova adicionada!")
                        st.cache_data.clear()
                        st.rerun()
                    except ValueError:
                        st.error("Data inválida! Use o formato DD/MM/AAAA.")

            st.markdown("---")
            st.subheader("Provas cadastradas")
            provas = get_provas_df()
            if len(provas) == 0:
                st.info("Nenhuma prova cadastrada.")
            else:
                for idx, row in provas.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([3,3,2,2,2])
                    with col1:
                        novo_nome = st.text_input(f"Nome prova {row['id']}", value=row['nome'], key=f"pr_nome_{row['id']}")
                    with col2:
                        if pd.notnull(row['data']) and str(row['data']).strip() != "":
                            try:
                                data_formatada = pd.to_datetime(row['data']).strftime("%d/%m/%Y")
                            except Exception:
                                data_formatada = "Data inválida"
                        else:
                            data_formatada = "Data não informada"
                        nova_data_str = st.text_input(f"Data prova {row['id']} (DD/MM/AAAA)", value=data_formatada, key=f"pr_data_{row['id']}")
                    with col3:
                        novo_status = st.selectbox(f"Status prova {row['id']}", ["Ativo", "Inativo"], index=0 if row.get('status', 'Ativo') == "Ativo" else 1, key=f"pr_status_{row['id']}")
                    with col4:
                        if st.button("Editar prova", key=f"pr_edit_{row['id']}"):
                            try:
                                nova_data = datetime.strptime(nova_data_str, "%d/%m/%Y")
                                conn = db_connect()
                                c = conn.cursor()
                                c.execute('UPDATE provas SET nome=?, data=?, status=? WHERE id=?', (novo_nome, nova_data.strftime("%Y-%m-%d"), novo_status, row['id']))
                                conn.commit()
                                conn.close()
                                st.success("Prova editada!")
                                st.cache_data.clear()
                                st.rerun()
                            except ValueError:
                                st.error("Data inválida! Use o formato DD/MM/AAAA.")
                    with col5:
                        if st.button("Excluir prova", key=f"pr_del_{row['id']}"):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('DELETE FROM provas WHERE id=?', (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("Prova excluída!")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- GESTÃO DE APOSTAS (apenas master/admin) ---
if st.session_state['pagina'] == "Gestão de Apostas" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Gestão de Apostas")
        provas_df = get_provas_df()
        usuarios_df = get_usuarios_df()
        apostas_df = get_apostas_df()
        resultados_df = get_resultados_df()
        pilotos_df = get_pilotos_df()
        participantes = usuarios_df[usuarios_df['status'] == 'Ativo']
        provas_df = provas_df.sort_values('data')
        tabs = st.tabs(participantes['nome'].tolist())
        for idx, part in enumerate(participantes.itertuples()):
            with tabs[idx]:
                st.subheader(f"Apostas de {part.nome}")
                apostas_part = apostas_df[apostas_df['usuario_id'] == part.id]
                apostas_dict = dict(zip(apostas_part['prova_id'], apostas_part.itertuples()))
                for _, prova in provas_df.iterrows():
                    st.write(f"**Prova:** {prova['nome']} ({prova['data']})")
                    if prova['id'] in apostas_dict:
                        ap = apostas_dict[prova['id']]
                        data_hora = ap.data_envio[:16] if ap.data_envio else "Data não registrada"
                        st.success(f"Aposta registrada em {data_hora}")
                    else:
                        st.warning("Sem aposta registrada.")
                        if st.button(f"Gerar aposta automática para {prova['nome']}", key=f"auto_{part.id}_{prova['id']}"):
                            # Incrementa o campo faltas do usuário
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('SELECT faltas FROM usuarios WHERE id=?', (part.id,))
                            faltas_atual = c.fetchone()
                            faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
                            c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, part.id))
                            conn.commit()
                            conn.close()
                            # Tenta copiar aposta anterior
                            ok, msg = gerar_aposta_automatica(part.id, prova['id'], prova['nome'], apostas_df, provas_df)
                            if ok:
                                st.cache_data.clear()  # Limpa o cache antes de buscar a aposta recém-criada!
                                nova_aposta_df = get_apostas_df()
                                filtro = (
                                    (nova_aposta_df['usuario_id'] == part.id) &
                                    (nova_aposta_df['prova_id'] == prova['id'])
                                )
                                resultado = nova_aposta_df[filtro]
                                if not resultado.empty:
                                    nova_aposta = resultado.iloc[0]
                                    aposta_str = f"Prova: {prova['nome']}*, Pilotos: {nova_aposta['pilotos']}, Fichas: {nova_aposta['fichas']}, 11º: {nova_aposta['piloto_11']}"
                                    registrar_log_aposta(part.nome, aposta_str, f"{prova['nome']}*")
                                else:
                                    st.warning("Aposta automática gerada, mas não foi possível registrar no log (aposta não encontrada no banco).")
                                st.success(msg)
                                st.rerun()
                            else:
                                resultado_row = resultados_df[resultados_df['prova_id'] == prova['id']]
                                pilotos_nao_pontuaram = []
                                piloto_11_nao = None
                                if not resultado_row.empty:
                                    resultado = ast.literal_eval(resultado_row.iloc[0]['posicoes'])
                                    pontuaram = set(resultado.get(str(pos), "") for pos in range(1, 11))
                                    todos_pilotos = set(pilotos_df['nome'])
                                    pilotos_nao_pontuaram = list(todos_pilotos - pontuaram)
                                    piloto_11 = resultado.get("11", None)
                                    pilotos_11_opcoes = [p for p in todos_pilotos if p != piloto_11]
                                    piloto_11_nao = pilotos_11_opcoes[0] if pilotos_11_opcoes else list(todos_pilotos)[0]
                                else:
                                    pilotos_nao_pontuaram = [pilotos_df['nome'].iloc[0]]
                                    piloto_11_nao = pilotos_df['nome'].iloc[0]
                                piloto_aposta = pilotos_nao_pontuaram[0] if pilotos_nao_pontuaram else pilotos_df['nome'].iloc[0]
                                salvar_aposta(
                                    part.id,
                                    prova['id'],
                                    [piloto_aposta],
                                    [15],
                                    piloto_11_nao,
                                    prova['nome'],
                                    automatica=1
                                )
                                # Incrementa o campo faltas do usuário novamente (caso gere aposta "zerada")
                                conn = db_connect()
                                c = conn.cursor()
                                c.execute('SELECT faltas FROM usuarios WHERE id=?', (part.id,))
                                faltas_atual = c.fetchone()
                                faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
                                c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, part.id))
                                conn.commit()
                                conn.close()
                                st.cache_data.clear()
                                # Registrar no log com "*"
                                nova_aposta_df = get_apostas_df()
                                filtro = (
                                    (nova_aposta_df['usuario_id'] == part.id) &
                                    (nova_aposta_df['prova_id'] == prova['id'])
                                )
                                resultado = nova_aposta_df[filtro]
                                if not resultado.empty:
                                    nova_aposta = resultado.iloc[0]
                                    aposta_str = f"Prova: {prova['nome']}*, Pilotos: {nova_aposta['pilotos']}, Fichas: {nova_aposta['fichas']}, 11º: {nova_aposta['piloto_11']}"
                                    registrar_log_aposta(part.nome, aposta_str, f"{prova['nome']}*")
                                else:
                                    st.warning("Aposta automática gerada, mas não foi possível registrar no log (aposta não encontrada no banco).")
                                st.success(f"Aposta automática gerada: 15 fichas em {piloto_aposta}, 11º colocado: {piloto_11_nao}")
                                st.rerun()
    else:
        st.warning("Acesso restrito ao administrador/master.")

# --- CLASSIFICAÇÃO ---
import plotly.graph_objects as go
if st.session_state['pagina'] == "Classificação" and st.session_state['token']:
    st.title("Classificação Geral do Bolão")
    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()
    apostas_df = get_apostas_df()
    resultados_df = get_resultados_df()
    participantes = usuarios_df[usuarios_df['status'] == 'Ativo']
    provas_df = provas_df.sort_values('data')
    tabela_classificacao = []
    tabela_detalhada = []

    for idx, part in participantes.iterrows():
        apostas_part = apostas_df[apostas_df['usuario_id'] == part['id']].sort_values('prova_id')
        pontos_part = calcular_pontuacao_lote(apostas_part, resultados_df, provas_df)
        total = sum([p for p in pontos_part if p is not None])
        tabela_classificacao.append({
            "Participante": part['nome'],
            "Total de Pontos": total
        })
        tabela_detalhada.append({
            "Participante": part['nome'],
            "Pontos por Prova": pontos_part
        })

    df_class = pd.DataFrame(tabela_classificacao).sort_values("Total de Pontos", ascending=False).reset_index(drop=True)
    st.subheader("Classificação Geral")
    st.table(df_class)

    st.subheader("Pontuação por Prova")
    provas_nomes = provas_df['nome'].tolist()
    participantes_nomes = [p['Participante'] for p in tabela_detalhada]
    dados_cruzados = {}
    for idx, prova in enumerate(provas_nomes):
        linha = {}
        for part in tabela_detalhada:
            linha[part['Participante']] = part['Pontos por Prova'][idx] if idx < len(part['Pontos por Prova']) and part['Pontos por Prova'][idx] is not None else 0
        dados_cruzados[prova] = linha
    df_cruzada = pd.DataFrame(dados_cruzados).T
    df_cruzada = df_cruzada.reindex(columns=participantes_nomes, fill_value=0)
    st.dataframe(df_cruzada)

    st.subheader("Evolução da Pontuação Acumulada")
    if not df_cruzada.empty:
        fig = go.Figure()
        for participante in participantes_nomes:
            pontos_acumulados = df_cruzada[participante].cumsum()
            fig.add_trace(go.Scatter(
                x=provas_nomes,
                y=pontos_acumulados,
                mode='lines+markers',
                name=participante
            ))
        fig.update_layout(
            title="Evolução da Pontuação Acumulada",
            xaxis_title="Prova",
            yaxis_title="Pontuação Acumulada",
            xaxis_tickangle=-45,
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)),
            margin=dict(l=40, r=20, t=60, b=80),
            plot_bgcolor='rgba(240,240,255,0.9)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados para exibir o gráfico de evolução.")

# --- ATUALIZAÇÃO DE RESULTADOS (apenas master/admin) ---
if st.session_state['pagina'] == "Atualização de resultados" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Atualizar Resultado Manualmente")
        provas = get_provas_df()
        pilotos_df = get_pilotos_df()
        pilotos_ativos_df = pilotos_df[pilotos_df['status'] == 'Ativo']
        resultados_df = get_resultados_df()
        if len(provas) > 0 and len(pilotos_ativos_df) > 0:
            prova_id = st.selectbox(
                "Selecione a prova",
                provas['id'],
                format_func=lambda x: f"{provas[provas['id'] == x]['nome'].values[0]} ({provas[provas['id'] == x]['tipo'].values[0]})"
            )
            tipo_prova = provas[provas['id'] == prova_id]['tipo'].values[0]
            st.info(f"Tipo da prova selecionada: {tipo_prova}")
            pilotos = pilotos_ativos_df['nome'].tolist()

            posicoes = {}
            st.markdown("**Informe o piloto para cada posição:**")
            col1, col2 = st.columns(2)
            # Inicializa opções para cada posição
            pilotos_usados = set()
            # 1º ao 5º
            for pos in range(1, 6):
                with col1:
                    opcoes = [""] + [p for p in pilotos if p not in pilotos_usados]
                    piloto_sel = st.selectbox(
                        f"{pos}º colocado",
                        opcoes,
                        index=0,
                        key=f"pos_{pos}"
                    )
                    if piloto_sel:
                        posicoes[pos] = piloto_sel
                        pilotos_usados.add(piloto_sel)
            # 6º ao 10º
            for pos in range(6, 11):
                with col2:
                    opcoes = [""] + [p for p in pilotos if p not in pilotos_usados]
                    piloto_sel = st.selectbox(
                        f"{pos}º colocado",
                        opcoes,
                        index=0,
                        key=f"pos_{pos}"
                    )
                    if piloto_sel:
                        posicoes[pos] = piloto_sel
                        pilotos_usados.add(piloto_sel)
            # 11º colocado (pode ser qualquer piloto ativo, inclusive já usado)
            st.markdown("**11º colocado:**")
            piloto_11 = st.selectbox(
                "11º colocado",
                [""] + pilotos,
                index=0,
                key="pos_11"
            )
            if piloto_11:
                posicoes[11] = piloto_11

            erro = None
            # Validação antes de salvar
            if st.button("Salvar resultado"):
                # Checa se todos os combos de 1º ao 10º estão preenchidos
                if len(posicoes) < 11 or any(not posicoes.get(pos) for pos in range(1, 11)):
                    erro = "Preencha todos os campos de 1º ao 10º colocado (não deixe em branco)."
                # Checa se há pilotos repetidos entre 1º e 10º
                elif len(set([posicoes.get(pos) for pos in range(1, 11)])) < 10:
                    erro = "Não é permitido repetir piloto entre 1º e 10º colocado."
                elif not posicoes.get(11):
                    erro = "Selecione o piloto para 11º colocado."
                if erro:
                    st.error(erro)
                else:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('REPLACE INTO resultados (prova_id, posicoes) VALUES (?, ?)', (prova_id, str(posicoes)))
                    conn.commit()
                    conn.close()
                    st.success("Resultado salvo!")
                    st.cache_data.clear()
                    st.rerun()

            # Mostra abaixo as provas já cadastradas e seus resultados
            st.markdown("---")
            st.subheader("Resultados cadastrados")
            resultados_df = get_resultados_df()
            provas_resultados = []
            for _, prova in provas.iterrows():
                res = resultados_df[resultados_df['prova_id'] == prova['id']]
                if not res.empty:
                    posicoes_dict = ast.literal_eval(res.iloc[0]['posicoes'])
                    linha = {
                        "Prova": prova['nome'],
                        "Data": pd.to_datetime(prova['data']).strftime("%d/%m/%Y"),
                        "Tipo": prova.get('tipo', 'Normal')
                    }
                    for pos in range(1, 12):
                        linha[f"{pos}º"] = posicoes_dict.get(pos, "")
                    provas_resultados.append(linha)
            if provas_resultados:
                st.dataframe(pd.DataFrame(provas_resultados))
            else:
                st.info("Nenhum resultado cadastrado ainda.")
        else:
            st.warning("Cadastre provas e pilotos ativos antes de lançar resultados.")
    else:
        st.warning("Acesso restrito ao administrador/master.")


# --- LOG DE APOSTAS (visível para todos, mas com filtros) ---
if st.session_state['pagina'] == "Log de Apostas" and st.session_state['token']:
    payload = get_payload()
    conn = db_connect()
    if payload['perfil'] == 'master':
        df = pd.read_sql('SELECT * FROM log_apostas', conn)
    else:
        nome = get_user_by_id(payload['user_id'])[1]
        df = pd.read_sql('SELECT * FROM log_apostas WHERE apostador=?', conn, params=(nome,))
    conn.close()
    st.subheader("Log de Apostas")
    st.dataframe(df)
# --- Regulamento ---
if st.session_state['pagina'] == "Regulamento":
    st.title("Regulamento BF1-2025")
    st.markdown(REGULAMENTO.replace('\n', '  \n'))

# --- Backup ---
import streamlit as st
import sqlite3
import pandas as pd
import io
import os

DB_PATH = 'bolao_f1Prod.db'  # Ajuste para o caminho do seu banco

def exportar_tabelas_para_excel(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tabelas = [row[0] for row in cursor.fetchall()]
    arquivos_excel = {}
    for tabela in tabelas:
        df = pd.read_sql(f"SELECT * FROM {tabela}", conn)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=tabela)
        arquivos_excel[tabela] = output.getvalue()
    conn.close()
    return arquivos_excel

def importar_excel_para_tabela(db_path, tabela, arquivo_excel_bytes):
    df = pd.read_excel(io.BytesIO(arquivo_excel_bytes), engine='openpyxl')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f'DELETE FROM {tabela}')  # Limpa a tabela antes de importar (opcional)
    conn.commit()
    df.to_sql(tabela, conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    return f'Dados importados para a tabela {tabela} com sucesso.'

def modulo_exportar_importar_excel():
    st.title("Exportação e Importação Excel (Master)")

    if not os.path.exists(DB_PATH):
        st.error("Banco de dados não encontrado.")
        return

    # Exportação
    st.header("Exportar tabelas para Excel")
    arquivos_excel = exportar_tabelas_para_excel(DB_PATH)
    if not arquivos_excel:
        st.info('Nenhuma tabela encontrada no banco para exportar.')
    else:
        for tabela, conteudo in arquivos_excel.items():
            st.download_button(
                label=f'Download da tabela {tabela} em Excel',
                data=conteudo,
                file_name=f'{tabela}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    # Importação
    st.header("Importar dados de Excel para uma tabela")
    tabelas = list(arquivos_excel.keys())
    if tabelas:
        tabela_escolhida = st.selectbox("Tabela para importar", tabelas)
        arquivo = st.file_uploader("Selecione o arquivo Excel (.xlsx)", type=["xlsx"])
        if arquivo and tabela_escolhida:
            if st.button("Importar dados"):
                try:
                    msg = importar_excel_para_tabela(DB_PATH, tabela_escolhida, arquivo.read())
                    st.success(msg)
                except Exception as e:
                    st.error(f"Erro ao importar: {e}")
    else:
        st.info("Nenhuma tabela disponível para importação.")

# --- INTEGRAÇÃO NO APP ---
if (
    st.session_state.get('token')
    and st.session_state.get('pagina') == "Exportar/Importar Excel"
    and get_payload()['perfil'] == 'master'
):
    modulo_exportar_importar_excel()

# --- Dash F1 ---
if st.session_state['pagina'] == "Dash F1":
    dash.main()

# --- Logoff ---
if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    st.session_state['token'] = None
    st.session_state['pagina'] = "Login"
    st.success("Logout realizado com sucesso!")
