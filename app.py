from flask import Flask, render_template, request, redirect, session, url_for
from typing import Dict

app = Flask(__name__)
app.secret_key = 'secret_key_siswa'

class Siswa:
    def __init__(self, nama: str, matematika: int = None, ipa: int = None, 
                 ips: int = None, bindo: int = None, jarak: float = None):
        self.nama = nama
        self.nilai = {
            'matematika': matematika,
            'ipa': ipa,
            'ips': ips,
            'bindo': bindo
        } if all(v is not None for v in [matematika, ipa, ips, bindo]) else None
        self.jarak = jarak
        self._validate_initial_data()

    def _validate_initial_data(self) -> None:
        if self.nilai:
            for k, v in self.nilai.items():
                if not isinstance(v, int) or v < 0:
                    raise ValueError(f"Nilai {k} harus angka positif.")
        if self.jarak is not None and (not isinstance(self.jarak, (int, float)) or self.jarak < 0):
            raise ValueError("Jarak tidak boleh negatif.")

    def set_nilai(self, matematika: str, ipa: str, ips: str, bindo: str, jarak: str = None) -> None:
        try:
            self.nilai = {
                'matematika': int(matematika),
                'ipa': int(ipa),
                'ips': int(ips),
                'bindo': int(bindo)
            }
            self._validate_initial_data()
            if jarak is not None:
                self.jarak = float(jarak)
                self._validate_initial_data()
        except ValueError:
            raise ValueError("Input tidak valid. Pastikan semua nilai berupa angka positif.")

    def hitung_rata_rata(self) -> float:
        if not self.nilai:
            raise ValueError("Nilai belum diatur.")
        return sum(self.nilai.values()) / len(self.nilai)

    def status_penerimaan(self) -> str:
        return 'Diterima' if self.hitung_rata_rata() > 65 else 'Ditolak'

    def to_dict(self) -> Dict:
        return {
            'nama': self.nama,
            'matematika': self.nilai.get('matematika') if self.nilai else None,
            'ipa': self.nilai.get('ipa') if self.nilai else None,
            'ips': self.nilai.get('ips') if self.nilai else None,
            'bindo': self.nilai.get('bindo') if self.nilai else None,
            'jarak': self.jarak
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/siswa', methods=['GET', 'POST'])
def siswa_login():
    if request.method == 'POST':
        nama = request.form.get('nama').strip()
        if not nama:
            return render_template('siswa_login.html', error="Nama tidak boleh kosong.")
        
        session['nama'] = nama
        if 'registered_names' not in session:
            session['registered_names'] = []
        if nama not in session['registered_names']:
            session['registered_names'].append(nama)
            session.modified = True
        return redirect('/siswa_menu')
    return render_template('siswa_login.html', error=None)

@app.route('/siswa_menu')
def siswa_menu():
    if 'nama' not in session:
        return redirect('/siswa')
    nama = session['nama']
    pendaftar_nama_list = [p['nama'] for p in session.get('pendaftar', [])]
    return render_template('siswa_menu.html', nama=nama, 
                         registered_names=session['registered_names'], 
                         pendaftar_nama_list=pendaftar_nama_list)

@app.route('/daftar', methods=['GET', 'POST'])
def daftar():
    if 'nama' not in session:
        return redirect('/siswa')
    
    if request.method == 'POST':
        try:
            nama = session['nama']
            siswa = Siswa(nama)
            siswa.set_nilai(
                request.form['matematika'],
                request.form['ipa'],
                request.form['ips'],
                request.form['bindo'],
                request.form['jarak']
            )
            
            if 'pendaftar' not in session:
                session['pendaftar'] = []
            
            sudah_terdaftar = any(p['nama'] == nama for p in session['pendaftar'])
            if not sudah_terdaftar:
                session['pendaftar'].append(siswa.to_dict())
                session.modified = True
            return redirect('/siswa_menu')
        except ValueError as e:
            return render_template('daftar.html', error=str(e))
    
    return render_template('daftar.html', error=None)

@app.route('/simulasi', methods=['GET', 'POST'])
def simulasi():
    if 'nama' not in session:
        return redirect('/siswa')
    
    nama = session['nama']
    if 'simulasi_histori' not in session or not isinstance(session['simulasi_histori'], dict):
        session['simulasi_histori'] = {}
    if nama not in session['simulasi_histori']:
        session['simulasi_histori'][nama] = []
    
    if request.method == 'POST':
        try:
            siswa = Siswa(nama)
            siswa.set_nilai(
                request.form['matematika'],
                request.form['ipa'],
                request.form['ips'],
                request.form['bindo']
            )
            hasil = siswa.status_penerimaan()
            simulasi_data = siswa.to_dict()
            simulasi_data['hasil'] = hasil
            session['simulasi_histori'][nama].append(simulasi_data)
            session.modified = True
            return render_template('simulasi.html', hasil=hasil, 
                                 histori=session['simulasi_histori'][nama])
        except ValueError as e:
            return render_template('simulasi.html', hasil=None, 
                                 histori=session['simulasi_histori'][nama], error=str(e))
    
    return render_template('simulasi.html', hasil=None, 
                         histori=session['simulasi_histori'][nama])

@app.route('/guru', methods=['GET', 'POST'])
def guru_login():
    if request.method == 'POST':
        kode = request.form.get('kode')
        if kode == 'gr':
            return redirect('/pendaftar')
    return render_template('guru_login.html')

@app.route('/pendaftar')
def lihat_pendaftar():
    data = session.get('pendaftar', [])
    return render_template('pendaftar.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)