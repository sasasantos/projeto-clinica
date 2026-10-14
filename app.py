import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# Caminho base do projeto
pasta_base = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(pasta_base, 'templates') if os.path.exists(os.path.join(pasta_base, 'templates')) else os.path.join(pasta_base, 'template'),
    static_folder=os.path.join(pasta_base, 'static')
)

app.secret_key = 'chave_secreta_para_desenvolvimento'

# Nome do arquivo da base de dados SQLite
NOME_BANCO = 'clinica.db'
DB_PATH = os.path.join(pasta_base, NOME_BANCO)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite aceder aos campos pelo nome da coluna
    return conn

# ==========================================
# 1. ROTAS DE AUTENTICAÇÃO E PAINEL
# ==========================================

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('painel'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dados = request.get_json() if request.is_json else request.form
        email = dados.get('usuario')
        senha = dados.get('senha')

        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM USUARIO WHERE EMAIL = ? AND SENHA = ?', (email, senha)).fetchone()
            conn.close()

            if user:
                session['usuario'] = user['NOME']
                session['usuario_id'] = user['IDUSUARIO']
                if request.is_json:
                    return jsonify({"sucesso": True, "redirect": url_for('painel')})
                return redirect(url_for('painel'))
            else:
                if request.is_json:
                    return jsonify({"sucesso": False, "mensagem": "E-mail ou senha inválidos."}), 401
                return render_template('login.html', erro="E-mail ou senha inválidos.")
        except Exception as e:
            if request.is_json:
                return jsonify({"sucesso": False, "mensagem": f"Erro de banco: {str(e)}"}), 500
            return render_template('login.html', erro=f"Erro no banco SQLite: {str(e)}")

    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('painel.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==========================================
# 2. GESTÃO DE USUÁRIOS (QUESTÃO 6)
# ==========================================

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form.get('tipo', 'Atendente')

        try:
            conn.execute(
                'INSERT INTO USUARIO (NOME, EMAIL, SENHA, TIPO, CRIADO_EM) VALUES (?, ?, ?, ?, datetime("now"))',
                (nome, email, senha, tipo)
            )
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro no SQLite: {err}")
        finally:
            conn.close()

        return redirect(url_for('usuarios'))

    lista_usuarios = conn.execute('SELECT * FROM USUARIO').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=lista_usuarios, usuario_logado=session['usuario'])

@app.route('/usuarios/editar/<int:id>', methods=['POST'])
def editar_usuario(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    conn = get_db_connection()
    conn.execute('UPDATE USUARIO SET NOME = ?, EMAIL = ?, SENHA = ? WHERE IDUSUARIO = ?', (nome, email, senha, id))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios'))

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM USUARIO WHERE IDUSUARIO = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios'))


# ==========================================
# 3. GESTÃO DE MÉDICOS (QUESTÃO 7)
# ==========================================

@app.route('/medicos', methods=['GET', 'POST'])
def medicos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        crm = request.form['crm']
        especialidade = request.form['especialidade']
        email = request.form['email']

        try:
            conn.execute(
                'INSERT INTO MEDICO (NOME, CRM, ESPECIALIDADE, EMAIL) VALUES (?, ?, ?, ?)',
                (nome, crm, especialidade, email)
            )
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro ao inserir médico: {err}")
        finally:
            conn.close()

        return redirect(url_for('medicos'))

    lista_medicos = conn.execute('SELECT * FROM MEDICO').fetchall()
    conn.close()
    return render_template('medicos.html', medicos=lista_medicos, usuario_logado=session['usuario'])

@app.route('/medicos/editar/<int:id>', methods=['POST'])
def editar_medico(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nome = request.form['nome']
    crm = request.form['crm']
    especialidade = request.form['especialidade']
    email = request.form['email']

    conn = get_db_connection()
    conn.execute('UPDATE MEDICO SET NOME = ?, CRM = ?, ESPECIALIDADE = ?, EMAIL = ? WHERE IDMEDICO = ?', (nome, crm, especialidade, email, id))
    conn.commit()
    conn.close()
    return redirect(url_for('medicos'))

@app.route('/medicos/excluir/<int:id>', methods=['POST'])
def excluir_medico(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM MEDICO WHERE IDMEDICO = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('medicos'))


# ==========================================
# 4. GESTÃO DE PACIENTES (QUESTÃO 8)
# ==========================================

@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form['data_nascimento']
        telefone = request.form['telefone']
        email = request.form['email']

        try:
            conn.execute(
                'INSERT INTO PACIENTES (NOME, CPF, DATA_NASCIMENTO, TELEFONE, EMAIL) VALUES (?, ?, ?, ?, ?)',
                (nome, cpf, data_nascimento, telefone, email)
            )
            conn.commit()
        except sqlite3.Error as err:
            print(f"Erro ao inserir paciente: {err}")
        finally:
            conn.close()

        return redirect(url_for('pacientes'))

    lista_pacientes = conn.execute('SELECT * FROM PACIENTES').fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=lista_pacientes, usuario_logado=session['usuario'])

@app.route('/pacientes/editar/<int:id>', methods=['POST'])
def editar_paciente(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nome = request.form['nome']
    cpf = request.form['cpf']
    data_nascimento = request.form['data_nascimento']
    telefone = request.form['telefone']
    email = request.form['email']

    conn = get_db_connection()
    conn.execute('UPDATE PACIENTES SET NOME = ?, CPF = ?, DATA_NASCIMENTO = ?, TELEFONE = ?, EMAIL = ? WHERE IDPACIENTES = ?', (nome, cpf, data_nascimento, telefone, email, id))
    conn.commit()
    conn.close()
    return redirect(url_for('pacientes'))

@app.route('/pacientes/excluir/<int:id>', methods=['POST'])
def excluir_paciente(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM PACIENTES WHERE IDPACIENTES = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pacientes'))


# ==========================================
# 5. GESTÃO DE AGENDAMENTOS (QUESTÃO 9)
# ==========================================

def buscar_dados_agendamento(conn):
    pacientes = conn.execute('SELECT * FROM PACIENTES').fetchall()
    medicos = conn.execute('SELECT * FROM MEDICO').fetchall()
    
    # O A.rowid garante o ID numérico correto do SQLite
    query = '''
        SELECT 
            A.rowid AS id_agendamento,
            A.DATA_CONSULTA,
            A.HORA_CONSULTA,
            A.OBSERVACAO,
            P.NOME AS NOME_PACIENTE,
            M.NOME AS NOME_MEDICO,
            A.MEDICO_ID
        FROM AGENDAMENTOS A
        JOIN PACIENTES P ON A.PACIENTES_ID = P.IDPACIENTES
        JOIN MEDICO M ON A.MEDICO_ID = M.IDMEDICO
        ORDER BY A.DATA_CONSULTA, A.HORA_CONSULTA
    '''
    agendamentos = conn.execute(query).fetchall()
    return pacientes, medicos, agendamentos


@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        medico_id = request.form['medico_id']
        data = request.form['data']
        horario = request.form['horario']
        descricao = request.form.get('descricao', '')
        criado_por = session.get('usuario_id', 1)

        # Validação da Questão 9: Impedir choque de horário para o mesmo médico
        conflito = conn.execute(
            'SELECT * FROM AGENDAMENTOS WHERE MEDICO_ID = ? AND DATA_CONSULTA = ? AND HORA_CONSULTA = ?',
            (medico_id, data, horario)
        ).fetchone()

        if conflito:
            pacientes, medicos, lista_agendamentos = buscar_dados_agendamento(conn)
            conn.close()
            return render_template(
                'agendamentos.html',
                pacientes=pacientes,
                medicos=medicos,
                agendamentos=lista_agendamentos,
                erro='O médico selecionado já possui uma consulta agendada nesta mesma data e horário!'
            )

        # Inserção no banco SQLite sem passar chave primária manualmente
        conn.execute(
            '''INSERT INTO AGENDAMENTOS 
               (PACIENTES_ID, MEDICO_ID, DATA_CONSULTA, HORA_CONSULTA, OBSERVACAO, CRIADO_POR, CRIADO_EM) 
               VALUES (?, ?, ?, ?, ?, ?, datetime("now"))''',
            (paciente_id, medico_id, data, horario, descricao, criado_por)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('agendamentos'))

    pacientes, medicos, lista_agendamentos = buscar_dados_agendamento(conn)
    conn.close()

    return render_template('agendamentos.html', pacientes=pacientes, medicos=medicos, agendamentos=lista_agendamentos)


@app.route('/agendamentos/editar/<int:id>', methods=['POST'])
def editar_agendamento(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = request.form['data']
    horario = request.form['horario']
    descricao = request.form['descricao']

    conn = get_db_connection()

    agendamento_atual = conn.execute('SELECT MEDICO_ID FROM AGENDAMENTOS WHERE rowid = ? OR IDAGENDAMENTO = ?', (id, id)).fetchone()

    if agendamento_atual:
        medico_id = agendamento_atual['MEDICO_ID']

        conflito = conn.execute(
            'SELECT * FROM AGENDAMENTOS WHERE MEDICO_ID = ? AND DATA_CONSULTA = ? AND HORA_CONSULTA = ? AND rowid != ?',
            (medico_id, data, horario, id)
        ).fetchone()

        if conflito:
            pacientes, medicos, lista_agendamentos = buscar_dados_agendamento(conn)
            conn.close()
            return render_template(
                'agendamentos.html',
                pacientes=pacientes,
                medicos=medicos,
                agendamentos=lista_agendamentos,
                erro='Não foi possível alterar: O médico já possui outra consulta neste mesmo horário!'
            )

    conn.execute(
        'UPDATE AGENDAMENTOS SET DATA_CONSULTA = ?, HORA_CONSULTA = ?, OBSERVACAO = ? WHERE rowid = ? OR IDAGENDAMENTO = ?',
        (data, horario, descricao, id, id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('agendamentos'))


@app.route('/agendamentos/cancelar/<int:id>', methods=['POST'])
def cancelar_agendamento(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM AGENDAMENTOS WHERE rowid = ? OR IDAGENDAMENTO = ?', (id, id))
    conn.commit()
    conn.close()

    return redirect(url_for('agendamentos'))


if __name__ == '__main__':
    app.run(debug=True)