
#importaos el framework

from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from fpdf import FPDF
import webbrowser
from references import *
from flask_session import Session

#inicializamos el framework
app = Flask(__name__)

#configurar las sesiones
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#configurar la conexion
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='bdConsultorio'
app.secret_key= 'mysecretkey'
mysql = MySQL(app)


    
#rutas de la app para login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods= ["GET", "POST"])
def login():
    if request.method == 'POST':
        rfc = request.form['txtrfc']
        pas = request.form['txtpass']
        
        session["txtrfc"] = request.form.get("txtrfc")
        
        cursor = mysql.connection.cursor()
        cursor.execute('select * from tbmedicos where rfc = %s', (rfc,))
        consulta = cursor.fetchall()
        cursor.close()
        
        if len(consulta)>0:
            if pas == consulta[0][7]:
                session['rol'] = consulta[0][8]
                
                if session['rol'] == 1:
                    if not session.get("txtrfc"):
                        flash('No ha iniciado sesion')
                        return redirect('/')
                    return render_template('menuAdmin.html', id = consulta[0])
                    
                elif session['rol'] == 2:
                    if not session.get("txtrfc"):
                        flash('No ha iniciado sesion')
                        return redirect('/')
                    return render_template('menuDoc.html', id = consulta[0])
            else:
                flash('Contraseña no valida')
                return redirect(url_for('index'))
        else:
            flash('No exite el usuario')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session["txtrfc"] = None
    flash('Se ha cerrado la sesion')
    return redirect("/")


#rutas de la app para medicos

@app.route('/addMedico/<string:idmedico>', methods=['POST'])
def addMedico(idmedico):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vrfc = request.form['txtRFC']
        vced = request.form['txtCedula']
        vesp = request.form['txtEspecialidad']
        vcor = request.form['txtCorreo']
        vcel = request.form['txtCelular']
        vpass = request.form['txtPassword']
        vrol = request.form['txtRol']
        
        cursor = mysql.connection.cursor()
        cursor.execute('insert into tbmedicos(nombre, rfc, cedula, especialidad, correo, celular, password, rol) values(%s,%s,%s,%s,%s,%s,%s,%s)', (vnom, vrfc, vced, vesp, vcor, vcel, vpass, vrol))
        mysql.connection.commit()
        consulta = tablaMedicos()
        
        flash('Medico agregado a la BD')
        return render_template('consultarMedico.html',idmedic = idmedico, medicos = consulta)

@app.route('/addMedic/<string:idmedico>')
def addMedic(idmedico):
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('addMedico.html', idmedic = idmedico)

@app.route('/consultarMedico/<string:idmedico>')
def consultarMedico(idmedico):
    consulta = tablaMedicos()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarMedico.html', idmedic = idmedico, medicos = consulta)

@app.route('/eliminardoc/<string:idmedico>/<string:ideliminar>')
def eliminardoc(idmedico,ideliminar):
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    cursor = mysql.connection.cursor()
    cursor.execute('delete from tbmedicos where idMedico = {0}'.format(ideliminar))
    mysql.connection.commit()
    consulta = tablaMedicos()
    
    flash('Medico eliminado de la BD')
    return render_template('consultarMedico.html',idmedic = idmedico, medicos = consulta)

@app.route('/editardoc/<string:idmedico>/<string:ideditar>')
def editarMedico(idmedico,ideditar):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbmedicos where idMedico = %s',(ideditar,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('editarMedico.html', idmedic = idmedico, medicos = consulta[0])

@app.route('/actualizardoc/<string:idmedico>/<string:ideditar>', methods = ['POST'])
def actualizar(idmedico,ideditar):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vrfc = request.form['txtRFC']
        vced = request.form['txtCedula']
        vesp = request.form['txtEspecialidad']
        vcor = request.form['txtCorreo']
        vcel = request.form['txtCelular']
        vpass = request.form['txtPassword']
        vrol = request.form['txtRol']
    
        cursor = mysql.connection.cursor()
        cursor.execute('update tbmedicos set nombre = %s, rfc = %s, cedula = %s, especialidad = %s, correo = %s, celular = %s, password = %s, rol = %s where idMedico = %s', (vnom, vrfc, vced, vesp, vcor,vcel, vpass, vrol, ideditar))
        mysql.connection.commit()
        consulta = tablaMedicos()
        
        flash('Medico actualizado en la BD')
        return render_template('consultarMedico.html',idmedic = idmedico, medicos = consulta)

def tablaMedicos():
    cursor = mysql.connection.cursor()
    cursor.execute('select tbmedicos.*, tbroles.rol from tbmedicos, tbroles where tbmedicos.rol = tbroles.id')
    consulta = cursor.fetchall()
    return consulta

def tablaMedicosxId(id):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbmedicos where idMedico = %s',(id,))
    consulta = cursor.fetchall()
    return consulta


#rutas de la app para pacientes de un admin

@app.route('/addPac/<string:idmedico>')
def addPac(idmedico):
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('addPaciente.html', idmedic = idmedico)

@app.route('/insertarPac/<string:idmedico>', methods=['POST'])
def addPacient(idmedico):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vfen = request.form['txtFen']
        venf = request.form['txtEnfe']
        vale = request.form['txtAle']
        vant = request.form['txtAnt']
        
        cursor = mysql.connection.cursor()
        cursor.execute('insert into tbpacientes(nombre, fechaNacimiento, enfermedades, alergias, antecedentes, idMedico) values(%s,%s,%s,%s,%s,%s)', (vnom, vfen, venf, vale, vant, idmedico))
        mysql.connection.commit()
        consulta = tablaPacientes(idmedico)
        
        flash('Paciente agregado a la BD')
        return render_template('consultarPaciente.html',idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientes/<string:idmedico>')
def consultarPaciente(idmedico):
    consulta = tablaPacientes(idmedico)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarPaciente.html', idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientesxNombre/<string:idmedico>', methods = ['POST'])
def consultarPacientexNombre(idmedico):
    if request.method=='POST':
        vnom = request.form['txtBuscarNombre']
        consulta = tablaPacientesxNombre(idmedico, vnom)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarPaciente.html', idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientesxFecha/<string:idmedico>', methods = ['POST'])
def consultarPacientexFecha(idmedico):
    if request.method=='POST':
        vfec = request.form['txtBuscarFecha']
        consulta = tablaPacientesxFecha(idmedico, vfec)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarPaciente.html', idmedic = idmedico, pacientes = consulta)

@app.route('/editarPac/<string:idmedico>/<string:idpaciente>')
def editarPac(idmedico,idpaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbpacientes where idPaciente = %s',(idpaciente,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('editarPaciente.html', idmedic = idmedico, pacientes = consulta[0])

@app.route('/actualizarPac/<string:idmedico>/<string:idpaciente>', methods = ['POST'])
def actualizarPac(idmedico,idpaciente):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vfen = request.form['txtFen']
        venf = request.form['txtEnfe']
        vale = request.form['txtAle']
        vant = request.form['txtAnt']

        cursor = mysql.connection.cursor()
        cursor.execute('update tbpacientes set nombre = %s, fechaNacimiento = %s, enfermedades = %s, alergias = %s, antecedentes = %s where idPaciente = %s', (vnom, vfen, venf, vale, vant, idpaciente))
        mysql.connection.commit()
        consulta = tablaPacientes(idmedico)
        
        flash('Paciente actualizado en la BD')
        return render_template('consultarPaciente.html', idmedic = idmedico, pacientes = consulta)

def tablaPacientes(id):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbpacientes where idMedico = %s',(id,))
    consulta = cursor.fetchall()
    return consulta

def tablaPacientesxNombre(id, nombre):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbpacientes where idMedico = %s and nombre like %s',(id, "%" + nombre + "%"))
    consulta = cursor.fetchall()
    return consulta

def tablaPacientesxFecha(id, fecha):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbpacientes where idMedico = %s and fechaNacimiento = %s',(id, fecha))
    consulta = cursor.fetchall()
    return consulta

#rutas de la app para pacientes de un doc

@app.route('/addPacD/<string:idmedico>')
def addPacD(idmedico):
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('addPacienteD.html', idmedic = idmedico)

@app.route('/insertarPacD/<string:idmedico>', methods=['POST'])
def addPacientD(idmedico):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vfen = request.form['txtFen']
        venf = request.form['txtEnfe']
        vale = request.form['txtAle']
        vant = request.form['txtAnt']
        
        cursor = mysql.connection.cursor()
        cursor.execute('insert into tbpacientes(nombre, fechaNacimiento, enfermedades, alergias, antecedentes, idMedico) values(%s,%s,%s,%s,%s,%s)', (vnom, vfen, venf, vale, vant, idmedico))
        mysql.connection.commit()
        consulta = tablaPacientes(idmedico)
        
        flash('Paciente agregado a la BD')
        return render_template('consultarPacienteD.html',idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientesD/<string:idmedico>')
def consultarPacienteD(idmedico):
    consulta = tablaPacientes(idmedico)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarPacienteD.html', idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientesxNombreD/<string:idmedico>', methods = ['POST'])
def consultarPacientexNombreD(idmedico):
    if request.method=='POST':
        vnom = request.form['txtBuscarNombre']
        consulta = tablaPacientesxNombre(idmedico, vnom)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarPacienteD.html', idmedic = idmedico, pacientes = consulta)

@app.route('/consultarPacientesxFechaD/<string:idmedico>', methods = ['POST'])
def consultarPacientexFechaD(idmedico):
    if request.method=='POST':
        vfec = request.form['txtBuscarFecha']
        consulta = tablaPacientesxFecha(idmedico, vfec)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarPacienteD.html', idmedic = idmedico, pacientes = consulta)

@app.route('/editarPacD/<string:idmedico>/<string:idpaciente>')
def editarPacienteD(idmedico,idpaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tbpacientes where idPaciente = %s',(idpaciente,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('editarPacienteD.html', idmedic = idmedico, pacientes = consulta[0])

@app.route('/actualizarPacD/<string:idmedico>/<string:idpaciente>', methods = ['POST'])
def actualizarPacD(idmedico,idpaciente):
    if request.method=='POST':
        vnom = request.form['txtNombre']
        vfen = request.form['txtFen']
        venf = request.form['txtEnfe']
        vale = request.form['txtAle']
        vant = request.form['txtAnt']
    
        cursor = mysql.connection.cursor()
        cursor.execute('update tbpacientes set nombre = %s, fechaNacimiento = %s, enfermedades = %s, alergias = %s, antecedentes = %s where idPaciente = %s', (vnom, vfen, venf, vale, vant, idpaciente))
        mysql.connection.commit()
        consulta = tablaPacientes(idmedico)
        
        flash('Paciente actualizado en la BD')
        return render_template('consultarPacienteD.html', idmedic = idmedico, pacientes = consulta)



#rutas de la app para citas de un admin

@app.route('/addCita/<string:idmedico>/<string:idpaciente>')
def addCita(idmedico,idpaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select *, timestampdiff(YEAR, fechaNacimiento, CURDATE()) as edad from tbpacientes where idPaciente = %s',(idpaciente,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('addCita.html', idmedic = idmedico, idpac = idpaciente, pacientes = consulta[0])

@app.route('/insertarCita/<string:idmedico>/<string:idpaciente>/<string:edad>/<string:name>', methods=['POST'])
def insertCita(idmedico,idpaciente, edad, name):
    if request.method=='POST':
        vfec = request.form['txtFecha']
        vpes = request.form['txtPeso']
        valt = request.form['txtAltura']
        vtem = request.form['txtTemperatura']
        vlat = request.form['txtLatidos']
        voxi = request.form['txtOxigenacion']
        vglu = request.form['txtGlucosa']
        vsin = request.form['txtSintomas']
        vdia = request.form['txtDiagnostico']
        vtra = request.form['txtTratamiento']
        vest = request.form['txtEstudios']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into tbcitas(fecha, peso, altura, temperatura, latidos, oxigenacion, glucosa, edad, sintomas, diagnostico, tratamiento, estudios, idPaciente, idMedico) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (vfec, vpes, valt, vtem, vlat, voxi, vglu, edad, vsin, vdia, vtra, vest, idpaciente, idmedico))
        mysql.connection.commit()
        consulta = tablaCitasxPaciente(idmedico, idpaciente)
        consul = tablaMedicosxId(idmedico)
        createPDF(consul[0][1], consul[0][4], consul[0][5], consul[0][6], name, vfec, vpes, valt, vtem, vlat, voxi, vglu, edad, vdia, vtra, vest)
        
        flash('Cita agregada a la BD')
        return render_template('consultarCita.html',idmedic = idmedico, citas = consulta)

@app.route('/consultarCitas/<string:idmedico>')
def consultarCitas(idmedico):
    consulta = tablaCitas(idmedico)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarCita.html', idmedic = idmedico, citas = consulta)

@app.route('/consultarCita/<string:idmedico>/<string:idpaciente>')
def consultarCita(idmedico, idpaciente):
    consulta = tablaCitasxPaciente(idmedico, idpaciente)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarCita.html', idmedic = idmedico, citas = consulta)

@app.route('/consultarCit/<string:idmedico>', methods = ['POST'])
def consultarCit(idmedico):
    if request.method=='POST':
        vnom = request.form['txtBuscarNombre']
        consulta = tablaCitasxNombre(idmedico, vnom)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarCita.html', idmedic = idmedico, citas = consulta)

@app.route('/consultCita/<string:idmedico>', methods = ['POST'])
def consultCita(idmedico):
    if request.method=='POST':
        vfec = request.form['txtBuscarFecha']
        consulta = tablaCitasxFecha(idmedico, vfec)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarCita.html', idmedic = idmedico, citas = consulta)
    
@app.route('/verCita/<string:idmedico>/<string:idcita>')
def verCita(idmedico,idcita):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idCita = %s',(idcita,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('verCita.html', idmedic = idmedico, citas = consulta[0])

def tablaCitas(id):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idMedico = %s',(id,))
    consulta = cursor.fetchall()
    return consulta

def tablaCitasxPaciente(idmedico, idpaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idMedico = %s and tbpacientes.idPaciente = %s',(idmedico, idpaciente))
    consulta = cursor.fetchall()
    return consulta

def tablaCitasxNombre(idmedico, namepaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idMedico = %s and tbpacientes.nombre like %s',(idmedico, "%" + namepaciente + "%"))
    consulta = cursor.fetchall()
    return consulta

def tablaCitasxFecha(idmedico, fechacita):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idMedico = %s and tbcitas.fecha = %s',(idmedico, fechacita))
    consulta = cursor.fetchall()
    return consulta

#rutas de la app para citas de un doc

@app.route('/addCitaD/<string:idmedico>/<string:idpaciente>')
def addCitaD(idmedico,idpaciente):
    cursor = mysql.connection.cursor()
    cursor.execute('select *, timestampdiff(YEAR, fechaNacimiento, CURDATE()) as edad from tbpacientes where idPaciente = %s',(idpaciente,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('addCitaD.html', idmedic = idmedico, idpac = idpaciente, pacientes = consulta[0])

@app.route('/insertarCitaD/<string:idmedico>/<string:idpaciente>/<string:edad>/<string:name>', methods=['POST'])
def insertCitaD(idmedico,idpaciente, edad, name):
    if request.method=='POST':
        vfec = request.form['txtFecha']
        vpes = request.form['txtPeso']
        valt = request.form['txtAltura']
        vtem = request.form['txtTemperatura']
        vlat = request.form['txtLatidos']
        voxi = request.form['txtOxigenacion']
        vglu = request.form['txtGlucosa']
        vsin = request.form['txtSintomas']
        vdia = request.form['txtDiagnostico']
        vtra = request.form['txtTratamiento']
        vest = request.form['txtEstudios']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into tbcitas(fecha, peso, altura, temperatura, latidos, oxigenacion, glucosa, edad, sintomas, diagnostico, tratamiento, estudios, idPaciente, idMedico) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (vfec, vpes, valt, vtem, vlat, voxi, vglu, edad, vsin, vdia, vtra, vest, idpaciente, idmedico))
        mysql.connection.commit()
        consulta = tablaCitasxPaciente(idmedico, idpaciente)
        consul = tablaMedicosxId(idmedico)
        createPDF(consul[0][1], consul[0][4], consul[0][5], consul[0][6], name, vfec, vpes, valt, vtem, vlat, voxi, vglu, edad, vdia, vtra, vest)
        
        flash('Cita agregada a la BD')
        return render_template('consultarCitaD.html',idmedic = idmedico, citas = consulta)

@app.route('/consultarCitasD/<string:idmedico>')
def consultarCitasD(idmedico):
    consulta = tablaCitas(idmedico)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarCitaD.html', idmedic = idmedico, citas = consulta)

@app.route('/consultarCitaD/<string:idmedico>/<string:idpaciente>')
def consultarCitaD(idmedico, idpaciente):
    consulta = tablaCitasxPaciente(idmedico, idpaciente)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('consultarCitaD.html', idmedic = idmedico, citas = consulta)

@app.route('/consultarCitD/<string:idmedico>', methods = ['POST'])
def consultarCitD(idmedico):
    if request.method=='POST':
        vnom = request.form['txtBuscarNombre']
        consulta = tablaCitasxNombre(idmedico, vnom)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarCitaD.html', idmedic = idmedico, citas = consulta)

@app.route('/consultCitaD/<string:idmedico>', methods = ['POST'])
def consultCitaD(idmedico):
    if request.method=='POST':
        vfec = request.form['txtBuscarFecha']
        consulta = tablaCitasxFecha(idmedico, vfec)
        if not session.get("txtrfc"):
            flash('No ha iniciado sesion')
            return redirect('/')
        return render_template('consultarCitaD.html', idmedic = idmedico, citas = consulta)
    
@app.route('/verCitaD/<string:idmedico>/<string:idcita>')
def verCitaD(idmedico,idcita):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idCita = %s',(idcita,))
    consulta = cursor.fetchall()
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    return render_template('verCitaD.html', idmedic = idmedico, citas = consulta[0])


#rutas de la app pra el PDF de un admin

@app.route('/verReceta/<string:idmedico>/<string:idcita>')
def verReceta(idmedico,idcita):
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idCita = %s',(idcita,))
    consulta = cursor.fetchall()
    consul = tablaMedicosxId(idmedico)
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    createPDF(str(consul[0][1]), str(consul[0][4]), str(consul[0][5]), str(consul[0][6]), str(consulta[0][15]), str(consulta[0][1]), str(consulta[0][2]), str(consulta[0][3]), str(consulta[0][4]), str(consulta[0][5]), str(consulta[0][6]), str(consulta[0][7]), str(consulta[0][8]), str(consulta[0][10]), str(consulta[0][11]), str(consulta[0][12]))
    return render_template('verCita.html', idmedic = idmedico, citas = consulta[0])

def createPDF(nombreDoc, especialidad, correo, numero, nombrePac, fecha, peso, altura, temperatura, latidos, oxigenacion, glucosa, edad, diagnostico, tratamiento, estudios):
    class PDF(FPDF):

        # Page header
        def header(self):
            self.set_font('Arial', '', 11)
        
            tcol_set(self, 'red')
            tfont_size(self,35)
            tfont(self,'B')
            self.multi_cell(w = 0, h = 11, txt = 'Consultorio Santa Cruz Azul', border = 0,
                    align = 'C', fill = 0)
        
            self.image('C:/Users/fredy/OneDrive/Escritorio/Consultorio Santa Cruz Azul/static/img/logo.jpg',
                  x = 20, y = 25, w = 55, h = 55)

            self.set_font('Arial', '', 11)

            tcol_set(self, 'blue')
            tfont_size(self,24)
            tfont(self,'B')
            self.cell(w = 0, h = 16, txt = '', border = 0, ln=1,
                 align = 'R', fill = 0)

            tcol_set(self, 'blue')
            tfont_size(self,21)
            tfont(self,'B')
            self.cell(w = 0, h = 10, txt = 'Dr(a). ' + nombreDoc, border = 0, ln=1,
                    align = 'R', fill = 0)

            tfont_size(self,16)
            tcol_set(self, 'blue')
            tfont(self,'')
            self.cell(w = 0, h = 7, txt = especialidad, border = 0, ln=2,
                 align = 'R', fill = 0)
        
            tfont_size(self,16)
            tcol_set(self, 'blue')
            tfont(self,'')
            self.cell(w = 0, h = 7, txt = correo, border = 0, ln=2,
                 align = 'R', fill = 0)
        
            tfont_size(self,16)
            tcol_set(self, 'blue')
            tfont(self,'')
            self.cell(w = 0, h = 7, txt = numero, border = 0, ln=2,
                 align = 'R', fill = 0)

            self.ln(22)

        # Page footer
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-20)

            # Arial italic 8
            self.set_font('Arial', 'I', 13)

            # Firma
            pdf.line(50, 276, 160, 276)
            self.cell(w = 0, h = 10, txt =  'Dr(a). ' + nombreDoc,
                    border = 0,
                    align = 'C', fill = 0)   



    pdf = PDF(orientation = 'P', unit = 'mm', format='A4') 
    pdf.alias_nb_pages()

    pdf.add_page()

    # TEXTO
    pdf.set_font('Arial', '', 12) 


    # 1er encabezado ----

    bcol_set(pdf, 'green')
    tfont_size(pdf,16)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 7, txt = 'Paciente', border= 0,
            align = 'C', fill = 0)
    tfont(pdf,'')

    bcol_set(pdf, 'green')
    tfont_size(pdf,15)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 2, txt = '', border= '1',
             align = 'C', fill = 1)
    tfont(pdf,'')

    h_sep = 9
    pdf.ln(1)
    tfont_size(pdf,12)

    # fila 1 --

    tcol_set(pdf, 'gray')
    pdf.cell(w = 23, h = h_sep, txt = 'Nombre:', border = 0, 
             align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 80, h = h_sep, txt = nombrePac, border = 0,
             align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 23, h = h_sep, txt = 'Edad: ', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 15, h = h_sep, txt = edad, border = 0,
             align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 16, h = h_sep, txt = 'Fecha:', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.multi_cell(w = 0, h = h_sep, txt = fecha, border = 0,
         align = 'L', fill = 0)

     #FILA 2
    tcol_set(pdf, 'gray')
    pdf.cell(w = 19, h = h_sep, txt = 'Peso: ', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 13, h = h_sep, txt = peso + ' kg', border = 0,
             align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 19, h = h_sep, txt = 'Altura:', border = 0, 
             align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 15, h = h_sep, txt = altura + ' cm', border = 0,
         align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 19, h = h_sep, txt = 'Temp:', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 15, h = h_sep, txt = temperatura + ' °C', border = 0,
         align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 15, h = h_sep, txt = 'BPN:', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 13, h = h_sep, txt = latidos, border = 0,
         align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 13, h = h_sep, txt = 'SpO2:', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.cell(w = 15, h = h_sep, txt = oxigenacion + ' %', border = 0,
         align = 'L', fill = 0)

    tcol_set(pdf, 'gray')
    pdf.cell(w = 12, h = h_sep, txt = 'Glu:', border = 0, 
         align = 'R', fill = 0)

    tcol_set(pdf, 'black')         
    pdf.multi_cell(w = 0, h = h_sep, txt = glucosa + ' gr', border = 0,
         align = 'L', fill = 0)


    # 2do encabezado --

    pdf.ln(15)
    bcol_set(pdf, 'green')
    tfont_size(pdf,16)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 9, txt = 'Diagnostico', border = 0,
             align = 'C', fill = 0)
    tfont(pdf,'')

    bcol_set(pdf, 'green')
    tfont_size(pdf,15)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 2, txt = '', border= '1',
             align = 'C', fill = 1)
    tfont(pdf,'')


    h_sep = 9
    pdf.ln(1)
    tfont_size(pdf,12)

    # fila 1 --

    tcol_set(pdf, 'black') 
    pdf.multi_cell(w = 0, h = h_sep, txt = diagnostico, border = 0,
             align = 'L', fill = 0)


    # 3er encabezado --

    pdf.ln(15)
    bcol_set(pdf, 'green')
    tfont_size(pdf,16)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 9, txt = 'Tratamiento', border = 0,
             align = 'C', fill = 0)
    tfont(pdf,'')

    bcol_set(pdf, 'green')
    tfont_size(pdf,15)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 2, txt = '', border= '1',
         align = 'C', fill = 1)
    tfont(pdf,'')

    h_sep = 9
    pdf.ln(1)
    tfont_size(pdf,12)

    # fila 1 --

    tcol_set(pdf, 'black') 
    pdf.multi_cell(w = 0, h = h_sep, txt = tratamiento, border = 0,
             align = 'L', fill = 0)


    # 4to encabezado --

    pdf.ln(15)
    bcol_set(pdf, 'green')
    tfont_size(pdf,16)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 9, txt = 'Estudios', border = 0,
             align = 'C', fill = 0)
    tfont(pdf,'')

    bcol_set(pdf, 'green')
    tfont_size(pdf,15)
    tfont(pdf,'B')
    pdf.multi_cell(w = 0, h = 2, txt = '', border= '1',
            align = 'C', fill = 1)
    tfont(pdf,'')

    h_sep = 9
    pdf.ln(1)
    tfont_size(pdf,12)

    # fila 1 --

    tcol_set(pdf, 'black') 
    pdf.multi_cell(w = 0, h = h_sep, txt = estudios, border = 0,
            align = 'L', fill = 0)


    pdfname = "Receta Medica.pdf"
    pdf.output(pdfname)
    url = "C:/Users/fredy/OneDrive/Escritorio/Consultorio Santa Cruz Azul/" + pdfname
    webbrowser.open_new(url)

#rutas de la app pra el PDF de un admin

@app.route('/verRecetaD/<string:idmedico>/<string:idcita>')
def verRecetaD(idmedico,idcita):
    if not session.get("txtrfc"):
        flash('No ha iniciado sesion')
        return redirect('/')
    cursor = mysql.connection.cursor()
    cursor.execute('select tbcitas.*, tbpacientes.nombre as name from tbcitas, tbpacientes where tbcitas.idPaciente = tbpacientes.idPaciente and tbcitas.idCita = %s',(idcita,))
    consulta = cursor.fetchall()
    consul = tablaMedicosxId(idmedico)
    createPDF(str(consul[0][1]), str(consul[0][4]), str(consul[0][5]), str(consul[0][6]), str(consulta[0][15]), str(consulta[0][1]), str(consulta[0][2]), str(consulta[0][3]), str(consulta[0][4]), str(consulta[0][5]), str(consulta[0][6]), str(consulta[0][7]), str(consulta[0][8]), str(consulta[0][10]), str(consulta[0][11]), str(consulta[0][12]))
    
    return render_template('verCitaD.html', idmedic = idmedico, citas = consulta[0])

#levantamos el server de Flask
if __name__ == '__main__':
    app.run(port=3000, debug= True)
    