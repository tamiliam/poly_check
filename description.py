# description.py

# This file contains the "Human-Friendly" descriptions for all Polytechnic Courses.
# It is imported by app.py to display the "Course Details" card.

course_info = {
    # --- AGROTECHNOLOGY ---
    "POLY-DIP-001": {
        "headline": "🌱 Agroteknologi: Pertanian Moden & Pintar",
        "synopsis": "Lupakan imej petani tradisional dengan cangkul. Kursus ini melatih anda menjadi 'Agropreneur Moden'. Anda akan belajar teknologi Fertigasi (tanam gantung), Pertanian Pintar (IoT/Sensor), dan cara mengurus ladang komersial dari benih hingga pemasaran. Sesuai untuk anda yang suka aktiviti luar (outdoor) tetapi mahukan kerjaya berteknologi tinggi.",
        "jobs": ["Agropreneur (Usahawan Tani)", "Penyelia Ladang Moden", "Juruteknik Pertanian", "Pengurus Estet"]
    },
    
    # --- BIOTECHNOLOGY ---
    "POLY-DIP-002": {
        "headline": "🧬 Bioteknologi: Sains Hayat Industri",
        "synopsis": "Anda akan bekerja di makmal untuk menghasilkan produk berasaskan biologi—seperti makanan, ubat-ubatan, atau benih tanaman hibrid. Anda akan menguasai teknik Kultur Tisu, Mikrobiologi, dan Fermentasi. Ini adalah bidang untuk mereka yang teliti, suka eksperimen sains, dan berminat dengan inovasi makmal.",
        "jobs": ["Juruteknik Makmal (Lab Tech)", "Quality Control (QC)", "Pembantu Penyelidik", "Usahawan Bio-Produk"]
    },

    # --- GEOMATICS ---
    "POLY-DIP-003": {
        "headline": "🌍 Geomatik: Peta, Satelit & Dron",
        "synopsis": "Dulu dikenali sebagai 'Ukur Tanah', kini ia menggunakan Satelit (GPS) dan Dron. Tugas anda adalah mengukur bumi untuk menghasilkan peta digital yang tepat bagi pembinaan bangunan, jalan raya, dan perancangan bandar. Kerjaya ini menggabungkan kerja luar (fieldwork) yang lasak dengan analisis komputer yang canggih.",
        "jobs": ["Juruukur Tanah", "Operator Dron Pemetaan", "GIS Technician", "Penolong Pegawai Tanah"]
    },

    # --- RETAIL MANAGEMENT ---
    "POLY-DIP-004": {
        "headline": "🛒 Pengurusan Runcit: Raja Pasaran",
        "synopsis": "Pernah tertanya bagaimana pasar raya besar (Giant/AEON) atau butik fesyen antarabangsa diuruskan? Kursus ini mengajar anda logistik, susun atur kedai (Visual Merchandising), dan strategi jualan. Anda juga akan menjalani latihan industri intensif (WBL) di kedai sebenar untuk merasai pengalaman menjadi pengurus.",
        "jobs": ["Pengurus Cawangan (Store Manager)", "Visual Merchandiser", "Eksekutif Operasi Runcit", "Event Coordinator"]
    },

    # --- INSURANCE ---
    "POLY-DIP-005": {
        "headline": "🛡️ Insurans: Pengurusan Risiko Profesional",
        "synopsis": "Bukan sekadar menjadi ejen insurans. Ini adalah ilmu profesional tentang Pengurusan Risiko Kewangan. Anda akan belajar menilai kerugian, undang-undang kewangan, dan bagaimana syarikat gergasi melindungi aset bernilai jutaan ringgit. Kemahiran ini sangat diperlukan oleh bank dan syarikat korporat.",
        "jobs": ["Penilai Risiko (Underwriter)", "Eksekutif Tuntutan (Claims)", "Perancang Kewangan", "Broker Insurans"]
    },

    # --- ENVIRONMENTAL ENGINEERING ---
    "POLY-DIP-006": {
        "headline": "♻️ Kejuruteraan Alam Sekitar: Wira Bumi",
        "synopsis": "Anda adalah doktor kepada alam sekitar. Belajar cara merawat air sisa, mengurus sisa pepejal (sampah), dan memantau kualiti udara. Tugas anda memastikan pembangunan negara tidak memusnahkan bumi. Sesuai untuk mereka yang peka dengan isu hijau dan mahukan kerjaya teknikal yang memberi impak positif.",
        "jobs": ["Penolong Pegawai Alam Sekitar", "Penyelia Tapak Pelupusan", "Juruteknik Kualiti Air", "Pegawai Keselamatan & Kesihatan (SHO)"]
    },

    # --- CIVIL ENGINEERING ---
    "POLY-DIP-007": {
        "headline": "🏗️ Kejuruteraan Awam: Pembina Negara",
        "synopsis": "Dari jambatan gergasi ke bangunan pencakar langit, andalah yang merealisasikannya. Anda akan belajar melukis pelan struktur, menguji kekuatan konkrit, dan menyelia tapak pembinaan. Kerja ini mungkin panas dan berdebu, tetapi pulangannya lumayan dan hasilnya kekal berdiri megah.",
        "jobs": ["Penyelia Tapak (Site Supervisor)", "Pelukis Pelan (Draughtsman)", "Kontraktor Binaan", "Clerk of Works"]
    },

    # --- ELECTRICAL ENGINEERING ---
    "POLY-DIP-008": {
        "headline": "⚡ Kejuruteraan Elektrik: Kuasa Tinggi",
        "synopsis": "Fokus sepenuhnya kepada tenaga elektrik. Bagaimana ia dijana, dihantar melalui kabel grid kebangsaan, dan diagihkan ke rumah. Anda akan pakar dalam pendawaian (wiring), motor elektrik industri, dan keselamatan voltan tinggi. Graduan kursus ini adalah 'tulang belakang' kepada TNB dan kilang-kilang besar.",
        "jobs": ["Juruteknik Elektrik", "Chargeman (Penjaga Jentera)", "Kontraktor Pendawaian", "Juruteknik Penyelenggaraan"]
    },

    # --- ELECTRICAL & ELECTRONIC ENGINEERING ---
    "POLY-DIP-009": {
        "headline": "🤖 Elektrik & Elektronik: Kuasa & Robotik",
        "synopsis": "Kursus '2-dalam-1' yang paling versatil. Anda belajar asas kuasa (Elektrik) DAN sistem kawalan pintar (Elektronik). Bayangkan anda boleh membuat wiring rumah, dan pada masa sama memprogramkan robot kilang (PLC). Ini menjadikan anda sangat laku dalam pelbagai industri, dari pembinaan hingga pembuatan cip.",
        "jobs": ["Penolong Jurutera", "Penyelia Kilang (Automation)", "Juruteknik Pakar", "Service Engineer"]
    },

    # --- ELECTRICAL & INSTRUMENTATION (PETROCHEM) ---
    "POLY-DIP-010": {
        "headline": "🛢️ Elektrik & Instrumentasi: Pakar Petrokimia",
        "synopsis": "Kursus elit yang direka khusus untuk industri Minyak & Gas (O&G). Selain elektrik, anda belajar tentang 'Instrumentasi'—sensor dan alat kawalan yang memantau paip minyak dan loji kimia. Anda akan belajar sistem DCS dan PLC yang digunakan di loji penapisan (refinery).",
        "jobs": ["Juruteknik Instrumentasi", "Juruteknik O&G", "Penyelia Loji Petrokimia", "Penolong Jurutera Kawalan"]
    },
}

# --- FALLBACK FUNCTION ---
def get_course_details(cid, raw_name):
    # If we have the custom description, return it
    if cid in course_info:
        return course_info[cid]
    
    # Else, return a generic placeholder so the app doesn't crash
    return {
        "headline": f"{raw_name}",
        "synopsis": "Kursus ini menyediakan latihan teori dan amali yang komprehensif untuk menyediakan pelajar ke alam pekerjaan. (Maklumat terperinci sedang dikemaskini).",
        "jobs": ["Juruteknik", "Penyelia", "Usahawan"]
    }
