import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_da_vinci_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///consultora.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS DE DATOS
# ==========================================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    empresa = db.Column(db.String(120), nullable=True)

    contratos = db.relationship('Contrato', backref='cliente', lazy=True)
    solicitudes = db.relationship('Solicitud', backref='cliente', lazy=True)

class Plan(db.Model):
    __tablename__ = 'planes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio_mensual = db.Column(db.Float, nullable=False)
    sla_horas = db.Column(db.Integer, nullable=False)

    contratos = db.relationship('Contrato', backref='plan', lazy=True)
    solicitudes = db.relationship('Solicitud', backref='plan_solicitado', lazy=True)

class Contrato(db.Model):
    __tablename__ = 'contratos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    solicitudes = db.relationship('Solicitud', backref='contrato', lazy=True)

class Solicitud(db.Model):
    __tablename__ = 'solicitudes'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'), nullable=False)
    plan_solicitado_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    motivo = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow) # Faltaba este campo vital
    fecha_resolucion = db.Column(db.DateTime, nullable=True)
    motivo_rechazo = db.Column(db.String(200), nullable=True)
    
# ==========================================
# RUTAS Y CONTROLADORES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        perfil = request.form.get('perfil')
        if perfil == 'admin':
            session['user_id'] = 0
            session['role'] = 'admin'
            return redirect(url_for('admin_panel'))
        else:
            session['user_id'] = int(perfil)
            session['role'] = 'cliente'
            return redirect(url_for('catalogo'))
            
    clientes = Cliente.query.all()
    return render_template('login.html', clientes=clientes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/catalogo', methods=['GET'])
def catalogo():
    """Catálogo y solicitudes del cliente logueado."""
    if 'user_id' not in session or session.get('role') != 'cliente':
        return redirect(url_for('login'))
        
    cliente_id = session['user_id']
    planes = Plan.query.all()
    contratos = Contrato.query.filter_by(cliente_id=cliente_id, activo=True).all()
    mis_solicitudes = Solicitud.query.filter_by(cliente_id=cliente_id).order_by(Solicitud.id.desc()).all()
    
    return render_template(
        'catalogo.html',
        planes=planes,
        contratos=contratos,
        mis_solicitudes=mis_solicitudes
    )

@app.route('/solicitudes/nueva', methods=['POST'])
def nueva_solicitud():
    """El cliente crea una solicitud de modificación."""
    cliente_id = request.form.get('cliente_id', type=int)
    contrato_id = request.form.get('contrato_id', type=int)
    plan_solicitado_id = request.form.get('plan_id', type=int)
    motivo = request.form.get('motivo', '').strip()

    if not all([cliente_id, contrato_id, plan_solicitado_id]):
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('catalogo'))

    contrato = Contrato.query.get(contrato_id)
    if not contrato or contrato.cliente_id != cliente_id:
        flash('El contrato indicado no pertenece al cliente.', 'danger')
        return redirect(url_for('catalogo'))

    if contrato.plan_id == plan_solicitado_id:
        flash('El plan solicitado debe ser distinto al plan actual del contrato.', 'warning')
        return redirect(url_for('catalogo'))

    solicitud = Solicitud(
        cliente_id=cliente_id,
        contrato_id=contrato_id,
        plan_solicitado_id=plan_solicitado_id,
        motivo=motivo,
        estado='pendiente'
    )

    db.session.add(solicitud)
    db.session.commit()
    flash(f'Solicitud #{solicitud.id} registrada con éxito en estado PENDIENTE.', 'success')
    return redirect(url_for('catalogo'))

@app.route('/admin/panel', methods=['GET'])
def admin_panel():
    """Panel de administración."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    filtro_estado = request.args.get('estado')
    query = Solicitud.query

    if filtro_estado in ['pendiente', 'en_revision', 'realizado', 'rechazado']:
        solicitudes = query.filter_by(estado=filtro_estado).order_by(Solicitud.fecha_creacion.desc()).all()
    else:
        solicitudes = query.filter(Solicitud.estado.in_(['pendiente', 'en_revision'])).order_by(Solicitud.fecha_creacion.asc()).all()

    total_pendientes = Solicitud.query.filter_by(estado='pendiente').count()
    total_revision = Solicitud.query.filter_by(estado='en_revision').count()
    total_realizadas = Solicitud.query.filter_by(estado='realizado').count()

    return render_template(
        'admin.html',
        solicitudes=solicitudes,
        filtro=filtro_estado,
        pendientes=total_pendientes,
        revision=total_revision,
        realizadas=total_realizadas
    )

@app.route('/solicitudes/resolver', methods=['POST'])
def resolver_solicitud():
    solicitud_id = request.form.get('solicitud_id', type=int)
    accion = request.form.get('accion') 
    motivo = request.form.get('motivo_rechazo') 

    solicitud = Solicitud.query.get(solicitud_id)
    if not solicitud:
        flash('La solicitud especificada no existe.', 'danger')
        return redirect(url_for('admin_panel'))

    if solicitud.estado in ['realizado', 'rechazado']:
        flash(f'La solicitud #{solicitud.id} ya se encuentra cerrada ({solicitud.estado}).', 'warning')
        return redirect(url_for('admin_panel'))

    try:
        if accion == 'aprobar':
            contrato = Contrato.query.get(solicitud.contrato_id)
            if not contrato or not contrato.activo:
                raise ValueError("El contrato asociado no está activo o no fue encontrado.")

            contrato.plan_id = solicitud.plan_solicitado_id
            solicitud.estado = 'realizado'
            solicitud.fecha_resolucion = datetime.utcnow()
            flash(f'Solicitud #{solicitud.id} aprobada con éxito. Plan del Contrato #{contrato.id} actualizado a {contrato.plan.nombre}.', 'success')

        elif accion == 'revisar':
            solicitud.estado = 'en_revision'
            flash(f'Solicitud #{solicitud.id} movida a estado EN REVISIÓN.', 'info')

        elif accion == 'rechazar':
            solicitud.estado = 'rechazado'
            solicitud.fecha_resolucion = datetime.utcnow()
            solicitud.motivo_rechazo = motivo 
            flash(f'Solicitud #{solicitud.id} ha sido rechazada.', 'secondary')

        else:
            flash('Acción no permitida.', 'danger')
            return redirect(url_for('admin_panel'))

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la transacción: {str(e)}', 'danger')

    return redirect(url_for('admin_panel'))

# ==========================================
# CLI / SEED DATA
# ==========================================

@app.cli.command('init-db')
def init_db():
    db.drop_all()
    db.create_all()

    plan_bronce = Plan(nombre="Soporte Básico", descripcion="Mesa de ayuda N1, resolución en 48hs hábiles y monitoreo pasivo.", precio_mensual=150.0, sla_horas=48)
    plan_plata = Plan(nombre="Infraestructura Pro", descripcion="Mantenimiento preventivo, soporte N2 12x5 y respaldos automáticos.", precio_mensual=350.0, sla_horas=24)
    plan_oro = Plan(nombre="Enterprise Cloud", descripcion="Auditoría continua, alta disponibilidad, soporte 24x7 y Blue Team defensivo.", precio_mensual=750.0, sla_horas=4)

    db.session.add_all([plan_bronce, plan_plata, plan_oro])
    db.session.commit()

    c1 = Cliente(nombre="Acme Logística S.A.", email="it@acmelogistica.com", empresa="Acme Group")
    c2 = Cliente(nombre="Fintech Río S.R.L.", email="infra@fintechrio.com.ar", empresa="Fintech Río")

    db.session.add_all([c1, c2])
    db.session.commit()

    contrato1 = Contrato(cliente_id=c1.id, plan_id=plan_bronce.id, activo=True)
    contrato2 = Contrato(cliente_id=c2.id, plan_id=plan_plata.id, activo=True)

    db.session.add_all([contrato1, contrato2])
    db.session.commit()

    solicitud_demo = Solicitud(
        cliente_id=c1.id,
        contrato_id=contrato1.id,
        plan_solicitado_id=plan_plata.id,
        motivo="Ampliación de sucursal requiere menor tiempo de respuesta en incidentes.",
        estado='pendiente'
    )
    db.session.add(solicitud_demo)
    db.session.commit()

    print(">> Base de datos SQLite 'consultora.db' creada y poblada con datos semilla correctamente.")

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('consultora.db'):
            db.create_all()
    app.run(debug=True, port=5000)